from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA512
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import json
import time
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List
import base64

class Certificat:
    def __init__(self, sujet: str, cle_publique, emetteur: str, validite_jours: int = 365):
        self.numero_serie = str(uuid.uuid4())
        self.sujet = sujet
        self.emetteur = emetteur
        self.cle_publique = cle_publique
        self.date_creation = datetime.now()
        self.date_expiration = self.date_creation + timedelta(days=validite_jours)
        self.signature = None
        self.revoque = False
        
    def signer(self, cle_privee_emetteur):
        data = self._get_data_to_sign()
        h = SHA512.new(data)
        self.signature = pkcs1_15.new(cle_privee_emetteur).sign(h)
        
    def _get_data_to_sign(self) -> bytes:
        data = {
            'numero_serie': self.numero_serie,
            'sujet': self.sujet,
            'emetteur': self.emetteur,
            'cle_publique': self.cle_publique.export_key().decode(),
            'date_creation': self.date_creation.isoformat(),
            'date_expiration': self.date_expiration.isoformat()
        }
        return json.dumps(data, sort_keys=True).encode()
    
    def verifier_signature(self, cle_publique_emetteur) -> bool:
        if not self.signature:
            return False
        data = self._get_data_to_sign()
        h = SHA512.new(data)
        try:
            pkcs1_15.new(cle_publique_emetteur).verify(h, self.signature)
            return True
        except (ValueError, TypeError):
            return False
    
    def est_valide(self) -> Tuple[bool, str]:
        if self.revoque:
            return False, "Certificat révoqué"
        
        maintenant = datetime.now()
        if maintenant < self.date_creation:
            return False, "Certificat pas encore valide"
        
        if maintenant > self.date_expiration:
            return False, "Certificat expiré"
        
        return True, "Certificat valide"
    
    def revoquer(self):
        self.revoque = True
    
    def to_dict(self) -> dict:
        return {
            'numero_serie': self.numero_serie,
            'sujet': self.sujet,
            'emetteur': self.emetteur,
            'date_creation': self.date_creation.isoformat(),
            'date_expiration': self.date_expiration.isoformat(),
            'revoque': self.revoque,
            'signature': base64.b64encode(self.signature).decode() if self.signature else None
        }


class AutoriteCertification:
    def __init__(self):
        self.nom = "Autorité de Certification SET"
        print(f"[{self.nom}] Initialisation...")
        self.key = RSA.generate(2048)
        self.pub_key = self.key.publickey()
        self.certificats_emis: Dict[str, Certificat] = {}
        self.certificats_revoques: List[str] = []
        
        self.certificat_racine = Certificat(
            sujet=self.nom,
            cle_publique=self.pub_key,
            emetteur=self.nom,
            validite_jours=3650
        )
        self.certificat_racine.signer(self.key)
        print(f"[{self.nom}] ✅ Certificat racine auto-signé créé")
    
    def emettre_certificat(self, entite_nom: str, cle_publique, validite_jours: int = 365) -> Certificat:
        print(f"[{self.nom}] Émission d'un certificat pour '{entite_nom}'...")
        
        certificat = Certificat(
            sujet=entite_nom,
            cle_publique=cle_publique,
            emetteur=self.nom,
            validite_jours=validite_jours
        )
        
        certificat.signer(self.key)
        self.certificats_emis[certificat.numero_serie] = certificat
        
        print(f"[{self.nom}] ✅ Certificat émis (N° {certificat.numero_serie[:8]}...)")
        return certificat
    
    def verifier_certificat(self, certificat: Certificat) -> Tuple[bool, str]:
        valide, raison = certificat.est_valide()
        if not valide:
            return False, raison
        
        if certificat.numero_serie in self.certificats_revoques:
            return False, "Certificat révoqué"
        
        if not certificat.verifier_signature(self.pub_key):
            return False, "Signature du certificat invalide"
        
        return True, "Certificat valide"
    
    def revoquer_certificat(self, numero_serie: str):
        if numero_serie in self.certificats_emis:
            self.certificats_emis[numero_serie].revoquer()
            self.certificats_revoques.append(numero_serie)
            print(f"[{self.nom}] ⛔ Certificat {numero_serie[:8]}... révoqué")
    
    def get_public_key(self):
        return self.pub_key


class Entite:
    def __init__(self, nom: str, ca: AutoriteCertification):
        self.nom = nom
        self.ca = ca
        print(f"[{self.nom}] Génération des clés RSA...")
        self.key = RSA.generate(2048)
        self.pub_key = self.key.publickey()
        
        self.certificat = self.ca.emettre_certificat(self.nom, self.pub_key)
        self.transactions_vues: set = set()
        
    def get_public_key(self):
        return self.pub_key
    
    def get_certificat(self) -> Certificat:
        return self.certificat
    
    def signer_donnee(self, donnee_bytes: bytes) -> bytes:
        h =SHA512.new(donnee_bytes)
        return pkcs1_15.new(self.key).sign(h)
    
    def verifier_signature(self, donnee_bytes: bytes, signature: bytes, certificat: Certificat) -> Tuple[bool, str]:
        valide, raison = self.ca.verifier_certificat(certificat)
        if not valide:
            return False, f"Certificat invalide: {raison}"
        
        h =SHA512.new(donnee_bytes)
        try:
            pkcs1_15.new(certificat.cle_publique).verify(h, signature)
            return True, "Signature valide"
        except (ValueError, TypeError):
            return False, "Signature cryptographique invalide"
    
    def chiffrer_pour(self, message_bytes: bytes, cle_publique_destinataire) -> bytes:
        cipher = PKCS1_OAEP.new(cle_publique_destinataire)
        return cipher.encrypt(message_bytes)
    
    def dechiffrer(self, message_chiffre: bytes) -> bytes:
        cipher = PKCS1_OAEP.new(self.key)
        return cipher.decrypt(message_chiffre)
    
    def verifier_anti_rejeu(self, transaction_id: str, timestamp: float) -> Tuple[bool, str]:
        if transaction_id in self.transactions_vues:
            return False, "Transaction déjà traitée (attaque par rejeu détectée)"
        
        temps_actuel = time.time()
        if abs(temps_actuel - timestamp) > 300:
            return False, "Transaction expirée (timestamp trop ancien/futur)"
        
        return True, "Transaction unique et récente"


class Banque(Entite):
    def __init__(self, ca: AutoriteCertification):
        super().__init__("Banque Centrale", ca)
        self.comptes = {
            "4970-1111-2222-3333": {"solde": 5000, "titulaire": "Alice"},
            "4970-4444-5555-6666": {"solde": 100, "titulaire": "Bob"},
            "4970-7777-8888-9999": {"solde": 50000, "titulaire": "Charlie"}
        }
        self.historique_transactions = []
    
    def verifier_paiement(self, paquet_paiement_chiffre: bytes, transaction_id: str, timestamp: float) -> Tuple[bool, str, Optional[str]]:
        print(f"\n   -> [Banque] Réception demande d'autorisation (ID: {transaction_id[:8]}...)")
        
        anti_rejeu_ok, raison = self.verifier_anti_rejeu(transaction_id, timestamp)
        if not anti_rejeu_ok:
            print(f"   -> [Banque] ❌ {raison}")
            # Enregistrer la transaction refusée
            transaction_record = {
                'id': transaction_id,
                'carte': 'inconnu',
                'montant': 0,
                'timestamp': timestamp,
                'arqc': 'N/A',
                'statut': 'refusé',
                'raison': raison
            }
            self.historique_transactions.append(transaction_record)
            return False, raison, None
        
        try:
            infos_paiement_bytes = self.dechiffrer(paquet_paiement_chiffre)
            infos = json.loads(infos_paiement_bytes.decode())
            
            carte = infos['carte']
            montant = infos['montant']
            nonce = infos['nonce']
            
            print(f"   -> [Banque] 🔓 Déchiffrement réussi")
            print(f"   -> [Banque] Carte: {carte}, Montant: {montant}€")
            
            if carte not in self.comptes:
                print("   -> [Banque] ❌ Carte inconnue")
                # Enregistrer la transaction refusée
                transaction_record = {
                    'id': transaction_id,
                    'carte': carte,
                    'montant': montant,
                    'timestamp': timestamp,
                    'arqc': 'N/A',
                    'statut': 'refusé',
                    'raison': 'Carte invalide'
                }
                self.historique_transactions.append(transaction_record)
                return False, "Carte invalide", None
            
            compte = self.comptes[carte]
            if compte['solde'] < montant:
                print(f"   -> [Banque] ❌ Solde insuffisant ({compte['solde']}€ disponible)")
                # Enregistrer la transaction refusée
                transaction_record = {
                    'id': transaction_id,
                    'carte': carte,
                    'montant': montant,
                    'timestamp': timestamp,
                    'arqc': 'N/A',
                    'statut': 'refusé',
                    'raison': 'Fonds insuffisants'
                }
                self.historique_transactions.append(transaction_record)
                return False, "Fonds insuffisants", None
            
            self.comptes[carte]['solde'] -= montant
            
            arqc = self._generer_arqc(transaction_id, montant, carte)
            
            self.transactions_vues.add(transaction_id)
            
            transaction_record = {
                'id': transaction_id,
                'carte': carte,
                'montant': montant,
                'timestamp': timestamp,
                'arqc': arqc,
                'statut': 'approuvé',
                'raison': 'Autorisation accordée'
            }
            self.historique_transactions.append(transaction_record)
            
            print(f"   -> [Banque] ✅ Paiement autorisé. Nouveau solde: {compte['solde']}€")
            print(f"   -> [Banque] 🔐 ARQC généré: {arqc[:16]}...")
            
            return True, "Autorisation accordée", arqc
            
        except Exception as e:
            print(f"   -> [Banque] ❌ Erreur: {e}")
            # Enregistrer la transaction refusée
            transaction_record = {
                'id': transaction_id,
                'carte': 'inconnu',
                'montant': 0,
                'timestamp': timestamp,
                'arqc': 'N/A',
                'statut': 'refusé',
                'raison': f'Erreur technique: {str(e)}'
            }
            self.historique_transactions.append(transaction_record)
            return False, f"Erreur technique: {str(e)}", None
    
    def _generer_arqc(self, transaction_id: str, montant: float, carte: str) -> str:
        data = f"{transaction_id}{montant}{carte}{time.time()}".encode()
        return hashlib.sha512(data).hexdigest()
    
    def get_solde(self, carte: str) -> Optional[float]:
        if carte in self.comptes:
            return self.comptes[carte]['solde']
        return None
    
    def creer_compte(self, carte: str, titulaire: str, solde_initial: float = 0) -> Tuple[bool, str]:
        if carte in self.comptes:
            return False, "Un compte existe déjà pour cette carte"
        
        if solde_initial < 0:
            return False, "Le solde initial ne peut pas être négatif"
        
        self.comptes[carte] = {
            'solde': solde_initial,
            'titulaire': titulaire
        }
        
        print(f"[Banque] ✅ Compte créé pour {titulaire} (carte {carte})")
        print(f"[Banque] Solde initial: {solde_initial}€")
        
        return True, f"Compte créé avec succès. Solde initial: {solde_initial}€"
    
    def recharger_compte(self, carte: str, montant: float) -> Tuple[bool, str]:
        if carte not in self.comptes:
            return False, "Carte inconnue"
        
        if montant <= 0:
            return False, "Le montant doit être positif"
        
        if montant > 10000:
            return False, "Montant maximum de rechargement: 10000€"
        
        self.comptes[carte]['solde'] += montant
        
        print(f"[Banque] ✅ Compte {carte} rechargé de {montant}€")
        print(f"[Banque] Nouveau solde: {self.comptes[carte]['solde']}€")
        
        return True, f"Compte rechargé de {montant}€. Nouveau solde: {self.comptes[carte]['solde']}€"


class Marchand(Entite):
    def __init__(self, nom: str, ca: AutoriteCertification, banque: 'Banque'):
        super().__init__(nom, ca)
        self.banque = banque
        self.commandes = []
    
    def traiter_commande(self, paquet_commande: dict) -> Tuple[bool, str]:
        print(f"\n{'='*70}")
        print(f"[{self.nom}] 📦 Nouvelle commande reçue")
        print(f"{'='*70}")
        
        try:
            oi_clair = paquet_commande['order_info']
            pi_chiffre = paquet_commande['payment_info_enc']
            signature = paquet_commande['signature']
            certificat_client = paquet_commande['certificat_client']
            transaction_id = paquet_commande['transaction_id']
            timestamp = paquet_commande['timestamp']
            
            print(f"[{self.nom}] Transaction ID: {transaction_id[:16]}...")
            print(f"[{self.nom}] Articles: {oi_clair['items']}")
            print(f"[{self.nom}] Montant: {oi_clair['montant']}€")
            
            anti_rejeu_ok, raison = self.verifier_anti_rejeu(transaction_id, timestamp)
            if not anti_rejeu_ok:
                print(f"[{self.nom}] ❌ {raison}")
                return False, raison
            
            donnees_combinees = json.dumps(oi_clair, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
            
            sig_valide, raison_sig = self.verifier_signature(donnees_combinees, signature, certificat_client)
            
            if not sig_valide:
                print(f"[{self.nom}] ❌ {raison_sig}")
                return False, raison_sig
            
            print(f"[{self.nom}] ✅ Signature client validée")
            print(f"[{self.nom}] ✅ Certificat client vérifié ({certificat_client.sujet})")
            print(f"[{self.nom}] 🔒 Informations de paiement chiffrées (invisibles pour le marchand)")
            
            print(f"[{self.nom}] 📡 Demande d'autorisation à la banque...")
            
            succes_banque, msg_banque, arqc = self.banque.verifier_paiement(
                pi_chiffre, transaction_id, timestamp
            )
            
            if succes_banque:
                self.transactions_vues.add(transaction_id)
                
                commande_record = {
                    'id': transaction_id,
                    'client': certificat_client.sujet,
                    'items': oi_clair['items'],
                    'montant': oi_clair['montant'],
                    'timestamp': timestamp,
                    'arqc': arqc,
                    'statut': 'validée'
                }
                self.commandes.append(commande_record)
                
                print(f"\n{'='*70}")
                print(f"[{self.nom}] 🎉 COMMANDE VALIDÉE ET EXPÉDIÉE")
                print(f"[{self.nom}] ARQC de la banque: {arqc[:16]}...")
                print(f"{'='*70}\n")
                
                return True, f"Commande validée (ARQC: {arqc[:16]}...)"
            else:
                print(f"\n{'='*70}")
                print(f"[{self.nom}] ⛔ COMMANDE REFUSÉE: {msg_banque}")
                print(f"{'='*70}\n")
                return False, f"Paiement refusé: {msg_banque}"
                
        except Exception as e:
            print(f"[{self.nom}] ❌ Erreur lors du traitement: {e}")
            return False, f"Erreur technique: {str(e)}"


class Client(Entite):
    def __init__(self, nom: str, num_carte: str, ca: AutoriteCertification):
        super().__init__(nom, ca)
        self.carte = num_carte
        self.historique_achats = []
    
    def acheter(self, marchand: Marchand, liste_items: List[str], montant: float) -> Tuple[bool, str]:
        print(f"\n{'#'*70}")
        print(f"# 🛒 CLIENT: {self.nom} - NOUVEL ACHAT")
        print(f"{'#'*70}")
        
        transaction_id = str(uuid.uuid4())
        timestamp = time.time()
        nonce = get_random_bytes(16).hex()
        
        print(f"[{self.nom}] Génération transaction ID: {transaction_id[:16]}...")
        print(f"[{self.nom}] Articles: {liste_items}")
        print(f"[{self.nom}] Montant: {montant}€")
        
        oi = {
            "items": liste_items,
            "montant": montant,
            "client": self.nom,
            "timestamp": timestamp
        }
        
        pi = {
            "carte": self.carte,
            "montant": montant,
            "nonce": nonce,
            "transaction_id": transaction_id
        }
        
        print(f"[{self.nom}] 🔐 Chiffrement des informations de paiement pour la banque...")
        cle_pub_banque = marchand.banque.get_public_key()
        pi_chiffre = self.chiffrer_pour(json.dumps(pi).encode(), cle_pub_banque)
        
        print(f"[{self.nom}] ✍️  Signature de la transaction...")
        donnees_combinees = json.dumps(oi, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
        signature = self.signer_donnee(donnees_combinees)
        
        paquet = {
            "order_info": oi,
            "payment_info_enc": pi_chiffre,
            "signature": signature,
            "certificat_client": self.certificat,
            "transaction_id": transaction_id,
            "timestamp": timestamp
        }
        
        print(f"[{self.nom}] 📤 Envoi du paquet sécurisé à {marchand.nom}...")
        
        succes, message = marchand.traiter_commande(paquet)
        
        achat_record = {
            'id': transaction_id,
            'marchand': marchand.nom,
            'items': liste_items,
            'montant': montant,
            'timestamp': timestamp,
            'statut': 'succès' if succes else 'échec',
            'message': message
        }
        self.historique_achats.append(achat_record)
        
        return succes, message


def test_attaque_rejeu(client: Client, marchand: Marchand):
    print(f"\n{'='*70}")
    print("🔴 TEST ATTAQUE PAR REJEU")
    print(f"{'='*70}")
    
    transaction_id = str(uuid.uuid4())
    timestamp = time.time()
    
    oi = {"items": ["Test"], "montant": 10, "client": client.nom, "timestamp": timestamp}
    pi = {"carte": client.carte, "montant": 10, "nonce": get_random_bytes(16).hex(), "transaction_id": transaction_id}
    
    pi_chiffre = client.chiffrer_pour(json.dumps(pi).encode(), marchand.banque.get_public_key())
    donnees_combinees = json.dumps(oi, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
    signature = client.signer_donnee(donnees_combinees)
    
    paquet = {
        "order_info": oi,
        "payment_info_enc": pi_chiffre,
        "signature": signature,
        "certificat_client": client.certificat,
        "transaction_id": transaction_id,
        "timestamp": timestamp
    }
    
    print("Premier envoi (légitime):")
    marchand.traiter_commande(paquet)
    
    print("\n⚠️  Tentative de rejeu du même paquet:")
    marchand.traiter_commande(paquet)


def test_certificat_revoque(ca: AutoriteCertification, banque: Banque):
    print(f"\n{'='*70}")
    print("🔴 TEST CERTIFICAT RÉVOQUÉ")
    print(f"{'='*70}")
    
    attaquant = Client("Attaquant", "4970-9999-9999-9999", ca)
    
    print(f"\n⚠️  Révocation du certificat de l'attaquant...")
    ca.revoquer_certificat(attaquant.certificat.numero_serie)
    
    marchand_test = Marchand("MarchandTest", ca, banque)
    
    print(f"\nTentative d'achat avec certificat révoqué:")
    attaquant.acheter(marchand_test, ["Article volé"], 50)


def test_manipulation_montant(client: Client, marchand: Marchand):
    print(f"\n{'='*70}")
    print("🔴 TEST MANIPULATION DE MONTANT")
    print(f"{'='*70}")
    
    transaction_id = str(uuid.uuid4())
    timestamp = time.time()
    
    oi_legitime = {"items": ["Article"], "montant": 10, "client": client.nom, "timestamp": timestamp}
    pi = {"carte": client.carte, "montant": 10, "nonce": get_random_bytes(16).hex(), "transaction_id": transaction_id}
    
    pi_chiffre = client.chiffrer_pour(json.dumps(pi).encode(), marchand.banque.get_public_key())
    donnees_combinees = json.dumps(oi_legitime, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
    signature = client.signer_donnee(donnees_combinees)
    
    oi_modifie = {"items": ["Article"], "montant": 1, "client": client.nom, "timestamp": timestamp}
    
    paquet_modifie = {
        "order_info": oi_modifie,
        "payment_info_enc": pi_chiffre,
        "signature": signature,
        "certificat_client": client.certificat,
        "transaction_id": transaction_id,
        "timestamp": timestamp
    }
    
    print("⚠️  Tentative avec montant modifié après signature:")
    marchand.traiter_commande(paquet_modifie)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔐 SIMULATION PROTOCOLE SET AVEC CDA")
    print("="*70 + "\n")
    
    print("📋 PHASE 1: INITIALISATION DU SYSTÈME")
    print("-" * 70)
    ca = AutoriteCertification()
    banque = Banque(ca)
    amazon = Marchand("Amazon", ca, banque)
    fnac = Marchand("FNAC", ca, banque)
    
    alice = Client("Alice", "4970-1111-2222-3333", ca)
    bob = Client("Bob", "4970-4444-5555-6666", ca)
    charlie = Client("Charlie", "4970-7777-8888-9999", ca)
    
    print(f"\n✅ Système initialisé avec {len(ca.certificats_emis)} certificats émis")
    
    print("\n" + "="*70)
    print("📋 PHASE 2: TESTS DE TRANSACTIONS LÉGITIMES")
    print("="*70)
    
    print("\n🧪 TEST 1: Achat normal (Alice)")
    alice.acheter(amazon, ["Livre Python", "Clé USB 64GB"], 45)
    
    print("\n🧪 TEST 2: Achat normal (Charlie)")
    charlie.acheter(fnac, ["Ordinateur portable", "Souris gaming"], 850)
    
    print("\n🧪 TEST 3: Achat refusé - Fonds insuffisants (Bob)")
    bob.acheter(amazon, ["iPhone 15 Pro"], 1200)
    
    print("\n" + "="*70)
    print("📋 PHASE 3: TESTS DE SÉCURITÉ")
    print("="*70)
    
    test_attaque_rejeu(alice, amazon)
    
    test_certificat_revoque(ca, banque)
    
    test_manipulation_montant(alice, amazon)
    
    print("\n" + "="*70)
    print("📊 RÉSUMÉ FINAL")
    print("="*70)
    print(f"Transactions Amazon: {len(amazon.commandes)} commandes")
    print(f"Transactions FNAC: {len(fnac.commandes)} commandes")
    print(f"Historique Banque: {len(banque.historique_transactions)} transactions")
    print(f"\nSoldes finaux:")
    for carte, info in banque.comptes.items():
        print(f"  {info['titulaire']}: {info['solde']}€")
    
    print("\n" + "="*70)
    print("✅ SIMULATION TERMINÉE")
    print("="*70 + "\n")
