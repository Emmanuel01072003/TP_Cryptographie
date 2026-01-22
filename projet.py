from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import json

# =============================================================================
# CLASSES MÉTIER (LE COEUR DU SYSTÈME)
# =============================================================================

class Entite:
    """Classe de base pour gérer les clés RSA et les opérations crypto."""
    def __init__(self, nom):
        self.nom = nom
        # Génération des clés RSA 2048 bits
        print(f"[{self.nom}] Génération des clés en cours...")
        self.key = RSA.generate(2048)
        self.pub_key = self.key.publickey()

    def get_public_key(self):
        return self.pub_key

    def signer_donnee(self, donnee_bytes):
        """Signe une donnée avec la clé PRIVÉE."""
        h = SHA256.new(donnee_bytes)
        return pkcs1_15.new(self.key).sign(h)

    def verifier_signature(self, donnee_bytes, signature, cle_publique_emetteur):
        """Vérifie une signature avec la clé PUBLIQUE de l'émetteur."""
        h = SHA256.new(donnee_bytes)
        try:
            pkcs1_15.new(cle_publique_emetteur).verify(h, signature)
            return True
        except (ValueError, TypeError):
            return False

    def chiffrer_pour(self, message_bytes, cle_publique_destinataire):
        """Chiffre un message pour quelqu'un d'autre (avec sa clé PUBLIQUE)."""
        cipher = PKCS1_OAEP.new(cle_publique_destinataire)
        return cipher.encrypt(message_bytes)

    def dechiffrer(self, message_chiffre):
        """Déchiffre un message reçu (avec ma clé PRIVÉE)."""
        cipher = PKCS1_OAEP.new(self.key)
        return cipher.decrypt(message_chiffre)


class Banque(Entite):
    def __init__(self):
        super().__init__("Banque Centrale")

    def verifier_paiement(self, paquet_paiement_chiffre):
        print(f"\n   -> [Banque] Reçoit une demande d'autorisation...")
        try:
            # 1. Seule la banque peut déchiffrer les infos de paiement
            infos_paiement_bytes = self.dechiffrer(paquet_paiement_chiffre)
            infos = json.loads(infos_paiement_bytes.decode())
            
            print(f"   -> [Banque] 🔓 Déchiffrement réussi. Carte: {infos['carte']} | Montant: {infos['montant']}€")
            
            # 2. Logique métier simple (Vérification de solde)
            if infos['montant'] <= 1000:
                print("   -> [Banque] ✅ Solde suffisant. Paiement validé.")
                return True, "Autorisation Accordée"
            else:
                print("   -> [Banque] ❌ Montant trop élevé (>1000). Refusé.")
                return False, "Fonds insuffisants"
                
        except Exception as e:
            print(f"   -> [Banque] Erreur : {e}")
            return False, f"Erreur technique banque"


class Marchand(Entite):
    def __init__(self, nom, banque_ref):
        super().__init__(nom)
        self.banque = banque_ref # Le marchand doit savoir à quelle banque parler

    def traiter_commande(self, paquet_commande):
        print(f"\n[Marchand] 📦 Reçoit une nouvelle commande.")
        
        # 1. Extraction des données du paquet SET
        oi_clair = paquet_commande['order_info']         # Visible
        pi_chiffre = paquet_commande['payment_info_enc'] # Illisible (chiffré pour la banque)
        signature = paquet_commande['signature']
        client_pub_key = paquet_commande['client_pub_key']
        
        # 2. Vérification de la Double Signature
        # On recrée la donnée qui a été signée : (OI + PI_Chiffre)
        donnees_combinees = json.dumps(oi_clair).encode() + pi_chiffre
        
        if self.verifier_signature(donnees_combinees, signature, client_pub_key):
            print("   [Marchand] ✅ Signature du client VALIDE.")
            print(f"   [Marchand] Contenu commande : {oi_clair['items']}")
            print("   [Marchand] Note : Je ne vois PAS le numéro de carte (confidentialité respectée).")
            
            # 3. Transfert à la banque
            print("   [Marchand] 📡 Interrogation de la banque...")
            succes_banque, msg_banque = self.banque.verifier_paiement(pi_chiffre)
            
            if succes_banque:
                print(f"   [Marchand] 🎉 Banque OK. J'expédie la commande !")
                return True, "Commande Validée"
            else:
                print(f"   [Marchand] ⛔ Banque a refusé : {msg_banque}")
                return False, "Paiement Refusé"
        else:
            print("   [Marchand] ❌ Signature INVALIDE ! Tentative de fraude détectée.")
            return False, "Signature Invalide"


class Client(Entite):
    def __init__(self, nom, num_carte):
        super().__init__(nom)
        self.carte = num_carte
    
    def acheter(self, marchand, liste_items, montant):
        print(f"\n--- 🛒 Client {self.nom} démarre un achat de {montant}€ ---")
        
        # A. Préparation des infos
        oi = {"items": liste_items, "montant": montant}    # Order Info (Pour Marchand)
        pi = {"carte": self.carte, "montant": montant}     # Payment Info (Pour Banque)
        
        # B. Chiffrement du PI pour la Banque
        # On récupère la clé publique de la banque via le marchand
        cle_pub_banque = marchand.banque.get_public_key()
        pi_chiffre = self.chiffrer_pour(json.dumps(pi).encode(), cle_pub_banque)
        
        # C. Double Signature
        # On signe la concaténation de la commande et du paiement chiffré
        donnees_combinees = json.dumps(oi).encode() + pi_chiffre
        signature = self.signer_donnee(donnees_combinees)
        
        # D. Création du paquet SET
        paquet = {
            "order_info": oi,
            "payment_info_enc": pi_chiffre,
            "signature": signature,
            "client_pub_key": self.get_public_key()
        }
        
        # E. Envoi
        print(f"[Client] Envoi du paquet sécurisé à {marchand.nom}...")
        return marchand.traiter_commande(paquet)

# =============================================================================
# SCÉNARIO DE TEST (POUR VÉRIFIER QUE CA MARCHE)
# =============================================================================

if __name__ == "__main__":
    print("=== INITIALISATION DU SYSTÈME SET ===")
    
    # 1. Création des acteurs
    banque_centrale = Banque()
    amazon = Marchand("Amazon", banque_centrale)
    alice = Client("Alice", "4970-1111-2222-3333")
    
    # 2. Test 1 : Achat Valide
    print("\n\n=== TEST 1 : ACHAT NORMAL ===")
    alice.acheter(amazon, ["Livre Python", "Clé USB"], 45)
    
    # 3. Test 2 : Achat Refusé (Montant trop haut)
    print("\n\n=== TEST 2 : ACHAT TROP CHER ===")
    alice.acheter(amazon, ["Voiture de luxe"], 25000)