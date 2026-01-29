# 📚 GUIDE DÉTAILLÉ DU CODE - Protocole SET/CDA
## Comprendre le code de A à Z pour l'expliquer à votre professeur

---

## 🎯 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Imports et Dépendances](#imports-et-dépendances)
3. [Classe Certificat](#classe-certificat)
4. [Classe AutoriteCertification](#classe-autoritecertification)
5. [Classe Entite (Base)](#classe-entite-base)
6. [Classe Banque](#classe-banque)
7. [Classe Marchand](#classe-marchand)
8. [Classe Client](#classe-client)
9. [Fonctions de Test](#fonctions-de-test)
10. [Flux Complet d'une Transaction](#flux-complet-dune-transaction)

---

## 📖 Vue d'Ensemble

### Qu'est-ce que le protocole SET ?

**SET (Secure Electronic Transaction)** est un protocole de paiement sécurisé créé par Visa et MasterCard dans les années 90. Il garantit que :

1. **Le marchand ne voit JAMAIS votre numéro de carte** 🔒
2. **Seule la banque peut lire vos infos bancaires** 🏦
3. **Personne ne peut modifier la transaction** ✅
4. **Tout le monde est authentifié avec des certificats** 🎫

### Analogie Simple

Imaginez que vous voulez acheter un livre chez un libraire, mais vous ne voulez pas lui donner directement votre argent :

1. **Vous** : Mettez votre argent dans une **enveloppe scellée** que seule la banque peut ouvrir
2. **Vous** : Écrivez sur une feuille "Je veux acheter le livre X" et signez
3. **Vous** : Collez l'enveloppe scellée sur la feuille et donnez le tout au libraire
4. **Libraire** : Voit ce que vous voulez acheter, mais PAS votre argent
5. **Libraire** : Transmet l'enveloppe scellée à la banque
6. **Banque** : Ouvre l'enveloppe, vérifie que vous avez assez d'argent, prend l'argent
7. **Banque** : Dit au libraire "OK, c'est bon, expédiez le livre"

C'est exactement ce que fait SET avec la cryptographie !

---

## 🔧 Imports et Dépendances

```python
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import json
import time
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List
import base64
```

### Explication de chaque import :

#### `from Crypto.PublicKey import RSA`
- **Quoi** : Génération de paires de clés RSA (publique/privée)
- **Analogie** : C'est comme créer une serrure (clé publique) et sa clé unique (clé privée)
- **Usage** : `RSA.generate(2048)` crée une paire de clés de 2048 bits

#### `from Crypto.Cipher import PKCS1_OAEP`
- **Quoi** : Algorithme de chiffrement RSA avec padding OAEP
- **Pourquoi** : Le padding rend le chiffrement RSA plus sûr
- **Usage** : Chiffrer les informations de paiement

#### `from Crypto.Signature import pkcs1_15`
- **Quoi** : Algorithme de signature numérique RSA
- **Analogie** : Comme signer un document, mais impossible à falsifier
- **Usage** : Signer les transactions pour prouver leur authenticité

#### `from Crypto.Hash import SHA256`
- **Quoi** : Fonction de hachage SHA-256
- **Analogie** : Comme une empreinte digitale unique pour un document
- **Usage** : Créer un "résumé" des données avant de les signer

#### `from Crypto.Random import get_random_bytes`
- **Quoi** : Générateur de nombres aléatoires cryptographiquement sûr
- **Usage** : Créer des nonces (nombres utilisés une seule fois)

#### `import uuid`
- **Quoi** : Génération d'identifiants uniques universels
- **Usage** : Créer des IDs de transaction uniques

#### `import hashlib`
- **Quoi** : Bibliothèque de hachage
- **Usage** : Générer les ARQC (cryptogrammes)

#### `from datetime import datetime, timedelta`
- **Quoi** : Gestion des dates et heures
- **Usage** : Gérer la validité des certificats

#### `from typing import Dict, Tuple, Optional, List`
- **Quoi** : Annotations de types pour Python
- **Pourquoi** : Rend le code plus clair et aide à détecter les erreurs

---

## 🎫 Classe Certificat

### Qu'est-ce qu'un certificat ?

Un **certificat numérique** est comme une **carte d'identité électronique**. Il prouve que vous êtes bien qui vous prétendez être.

### Code Complet Expliqué

```python
class Certificat:
    def __init__(self, sujet: str, cle_publique, emetteur: str, validite_jours: int = 365):
        # Numéro de série unique (comme le numéro sur votre carte d'identité)
        self.numero_serie = str(uuid.uuid4())
        
        # À qui appartient ce certificat (ex: "Alice", "Amazon")
        self.sujet = sujet
        
        # Qui a délivré ce certificat (normalement l'Autorité de Certification)
        self.emetteur = emetteur
        
        # La clé publique de la personne (pour chiffrer/vérifier)
        self.cle_publique = cle_publique
        
        # Date de création (maintenant)
        self.date_creation = datetime.now()
        
        # Date d'expiration (dans 365 jours par défaut)
        self.date_expiration = self.date_creation + timedelta(days=validite_jours)
        
        # La signature de la CA (sera ajoutée plus tard)
        self.signature = None
        
        # Est-ce que le certificat a été révoqué ?
        self.revoque = False
```

### Méthode : `signer()`

**Rôle** : L'Autorité de Certification signe le certificat pour le rendre officiel

```python
def signer(self, cle_privee_emetteur):
    # 1. Récupérer toutes les données du certificat
    data = self._get_data_to_sign()
    
    # 2. Calculer l'empreinte SHA-256 de ces données
    h = SHA256.new(data)
    
    # 3. Signer l'empreinte avec la clé privée de la CA
    self.signature = pkcs1_15.new(cle_privee_emetteur).sign(h)
```

**Analogie** :
1. La CA prend toutes les infos du certificat
2. Elle fait un résumé (hash)
3. Elle "signe" ce résumé avec sa clé secrète
4. Cette signature prouve que c'est bien la CA qui l'a délivré

### Méthode : `_get_data_to_sign()`

**Rôle** : Préparer les données du certificat pour la signature

```python
def _get_data_to_sign(self) -> bytes:
    # Créer un dictionnaire avec toutes les infos importantes
    data = {
        'numero_serie': self.numero_serie,
        'sujet': self.sujet,
        'emetteur': self.emetteur,
        'cle_publique': self.cle_publique.export_key().decode(),
        'date_creation': self.date_creation.isoformat(),
        'date_expiration': self.date_expiration.isoformat()
    }
    
    # Convertir en JSON (texte structuré)
    # sort_keys=True garantit que l'ordre est toujours le même
    return json.dumps(data, sort_keys=True).encode()
```

**Pourquoi `sort_keys=True` ?**
- Sans ça, `{"a": 1, "b": 2}` et `{"b": 2, "a": 1}` donneraient des hash différents
- Avec, l'ordre est toujours alphabétique → même hash

### Méthode : `verifier_signature()`

**Rôle** : Vérifier que le certificat a bien été signé par la CA

```python
def verifier_signature(self, cle_publique_emetteur) -> bool:
    # Si pas de signature, c'est faux
    if not self.signature:
        return False
    
    # Récupérer les mêmes données qu'au moment de la signature
    data = self._get_data_to_sign()
    
    # Calculer le hash
    h = SHA256.new(data)
    
    try:
        # Essayer de vérifier la signature avec la clé publique de la CA
        pkcs1_15.new(cle_publique_emetteur).verify(h, self.signature)
        return True  # ✅ Signature valide
    except (ValueError, TypeError):
        return False  # ❌ Signature invalide
```

**Comment ça marche ?**
1. On refait le même hash des données
2. On utilise la **clé publique** de la CA pour vérifier
3. Si la signature est valide, c'est que c'est bien la CA qui a signé

**Analogie** :
- Signer = Fermer une enveloppe avec un sceau royal
- Vérifier = Regarder le sceau pour confirmer que c'est bien le roi

### Méthode : `est_valide()`

**Rôle** : Vérifier que le certificat est encore utilisable

```python
def est_valide(self) -> Tuple[bool, str]:
    # 1. Est-il révoqué ?
    if self.revoque:
        return False, "Certificat révoqué"
    
    maintenant = datetime.now()
    
    # 2. Est-il déjà actif ?
    if maintenant < self.date_creation:
        return False, "Certificat pas encore valide"
    
    # 3. Est-il expiré ?
    if maintenant > self.date_expiration:
        return False, "Certificat expiré"
    
    # ✅ Tout est bon
    return True, "Certificat valide"
```

---

## 🏛️ Classe AutoriteCertification

### Rôle de la CA

L'**Autorité de Certification** (CA) est comme un **bureau d'état civil** :
- Elle délivre les "cartes d'identité" (certificats)
- Elle peut les révoquer si besoin
- Elle vérifie que les certificats sont valides

### Initialisation

```python
class AutoriteCertification:
    def __init__(self):
        # Nom de l'autorité
        self.nom = "Autorité de Certification SET"
        
        print(f"[{self.nom}] Initialisation...")
        
        # 1. Générer sa propre paire de clés RSA 2048 bits
        self.key = RSA.generate(2048)
        self.pub_key = self.key.publickey()
        
        # 2. Dictionnaire pour stocker tous les certificats émis
        self.certificats_emis: Dict[str, Certificat] = {}
        
        # 3. Liste des numéros de série révoqués
        self.certificats_revoques: List[str] = []
        
        # 4. Créer son propre certificat (auto-signé)
        self.certificat_racine = Certificat(
            sujet=self.nom,
            cle_publique=self.pub_key,
            emetteur=self.nom,  # Elle se signe elle-même
            validite_jours=3650  # Valide 10 ans
        )
        
        # 5. Signer son propre certificat
        self.certificat_racine.signer(self.key)
        
        print(f"[{self.nom}] ✅ Certificat racine auto-signé créé")
```

**Pourquoi auto-signé ?**
- La CA est au sommet de la hiérarchie
- Personne au-dessus d'elle pour la signer
- Elle se signe elle-même pour créer la "racine de confiance"

### Méthode : `emettre_certificat()`

**Rôle** : Créer un certificat pour une entité (client, marchand, banque)

```python
def emettre_certificat(self, entite_nom: str, cle_publique, validite_jours: int = 365) -> Certificat:
    print(f"[{self.nom}] Émission d'un certificat pour '{entite_nom}'...")
    
    # 1. Créer le certificat
    certificat = Certificat(
        sujet=entite_nom,           # Ex: "Alice"
        cle_publique=cle_publique,  # Clé publique d'Alice
        emetteur=self.nom,          # "Autorité de Certification SET"
        validite_jours=validite_jours
    )
    
    # 2. Signer le certificat avec la clé privée de la CA
    certificat.signer(self.key)
    
    # 3. Stocker le certificat
    self.certificats_emis[certificat.numero_serie] = certificat
    
    print(f"[{self.nom}] ✅ Certificat émis (N° {certificat.numero_serie[:8]}...)")
    
    return certificat
```

**Processus étape par étape** :
1. Alice génère sa paire de clés (publique + privée)
2. Alice envoie sa clé **publique** à la CA
3. La CA crée un certificat contenant la clé publique d'Alice
4. La CA **signe** ce certificat avec sa clé **privée**
5. Alice reçoit son certificat signé

### Méthode : `verifier_certificat()`

**Rôle** : Vérifier qu'un certificat est valide et pas révoqué

```python
def verifier_certificat(self, certificat: Certificat) -> Tuple[bool, str]:
    # 1. Vérifier les dates (création, expiration)
    valide, raison = certificat.est_valide()
    if not valide:
        return False, raison
    
    # 2. Vérifier s'il est dans la liste de révocation
    if certificat.numero_serie in self.certificats_revoques:
        return False, "Certificat révoqué"
    
    # 3. Vérifier la signature cryptographique
    if not certificat.verifier_signature(self.pub_key):
        return False, "Signature du certificat invalide"
    
    # ✅ Tout est bon
    return True, "Certificat valide"
```

**Vérifications en cascade** :
1. ✅ Dates OK ? (pas expiré, déjà actif)
2. ✅ Pas révoqué ?
3. ✅ Signature valide ?

### Méthode : `revoquer_certificat()`

**Rôle** : Invalider un certificat (ex: carte volée, compromission)

```python
def revoquer_certificat(self, numero_serie: str):
    # Trouver le certificat
    if numero_serie in self.certificats_emis:
        # Marquer comme révoqué
        self.certificats_emis[numero_serie].revoquer()
        
        # Ajouter à la liste de révocation
        self.certificats_revoques.append(numero_serie)
        
        print(f"[{self.nom}] ⛔ Certificat {numero_serie[:8]}... révoqué")
```

**Cas d'usage** :
- Clé privée compromise
- Carte bancaire volée
- Entité malveillante détectée

---

## 👤 Classe Entite (Base)

### Rôle

C'est la **classe de base** pour Client, Marchand et Banque. Elle contient tout ce qui est **commun** à toutes les entités.

### Initialisation

```python
class Entite:
    def __init__(self, nom: str, ca: AutoriteCertification):
        # Nom de l'entité
        self.nom = nom
        
        # Référence vers l'Autorité de Certification
        self.ca = ca
        
        print(f"[{self.nom}] Génération des clés RSA...")
        
        # 1. Générer une paire de clés RSA (publique + privée)
        self.key = RSA.generate(2048)
        self.pub_key = self.key.publickey()
        
        # 2. Demander un certificat à la CA
        self.certificat = self.ca.emettre_certificat(self.nom, self.pub_key)
        
        # 3. Ensemble pour traquer les transactions déjà vues (anti-rejeu)
        self.transactions_vues: set = set()
```

**Étapes détaillées** :
1. On génère 2048 bits aléatoires → Clé privée
2. On calcule la clé publique à partir de la privée (math RSA)
3. On envoie la clé publique à la CA
4. La CA crée et signe un certificat
5. On stocke ce certificat

### Méthode : `signer_donnee()`

**Rôle** : Signer des données avec ma clé **privée**

```python
def signer_donnee(self, donnee_bytes: bytes) -> bytes:
    # 1. Calculer le hash SHA-256 des données
    h = SHA256.new(donnee_bytes)
    
    # 2. Signer le hash avec ma clé PRIVÉE
    return pkcs1_15.new(self.key).sign(h)
```

**Analogie** :
- Vous signez un contrat avec votre stylo unique
- Personne d'autre ne peut reproduire exactement votre signature

### Méthode : `verifier_signature()`

**Rôle** : Vérifier qu'une signature est valide et provient du bon certificat

```python
def verifier_signature(self, donnee_bytes: bytes, signature: bytes, certificat: Certificat) -> Tuple[bool, str]:
    # 1. Vérifier que le certificat est valide
    valide, raison = self.ca.verifier_certificat(certificat)
    if not valide:
        return False, f"Certificat invalide: {raison}"
    
    # 2. Calculer le hash des données
    h = SHA256.new(donnee_bytes)
    
    try:
        # 3. Vérifier la signature avec la clé PUBLIQUE du certificat
        pkcs1_15.new(certificat.cle_publique).verify(h, signature)
        return True, "Signature valide"
    except (ValueError, TypeError):
        return False, "Signature cryptographique invalide"
```

**Processus complet** :
1. Alice signe avec sa clé **privée** → Seule Alice peut faire ça
2. Bob vérifie avec la clé **publique** d'Alice → Tout le monde peut faire ça
3. Si ça marche, c'est que c'est bien Alice qui a signé

### Méthode : `chiffrer_pour()`

**Rôle** : Chiffrer un message pour quelqu'un d'autre

```python
def chiffrer_pour(self, message_bytes: bytes, cle_publique_destinataire) -> bytes:
    # Créer un chiffreur avec la clé PUBLIQUE du destinataire
    cipher = PKCS1_OAEP.new(cle_publique_destinataire)
    
    # Chiffrer le message
    return cipher.encrypt(message_bytes)
```

**Analogie** :
- Vous avez une **boîte aux lettres** (clé publique)
- N'importe qui peut y **déposer** un message (chiffrer)
- Seul **vous** avez la clé pour l'ouvrir (clé privée)

**Exemple** :
```python
# Alice veut envoyer "secret" à Bob
message = b"secret"

# Alice chiffre avec la clé PUBLIQUE de Bob
chiffre = alice.chiffrer_pour(message, bob.pub_key)

# Maintenant, seul Bob peut déchiffrer avec sa clé PRIVÉE
dechiffre = bob.dechiffrer(chiffre)  # → b"secret"
```

### Méthode : `dechiffrer()`

**Rôle** : Déchiffrer un message qui m'a été envoyé

```python
def dechiffrer(self, message_chiffre: bytes) -> bytes:
    # Créer un déchiffreur avec MA clé PRIVÉE
    cipher = PKCS1_OAEP.new(self.key)
    
    # Déchiffrer
    return cipher.decrypt(message_chiffre)
```

**Important** : Seule la personne qui a la clé **privée** peut déchiffrer !

### Méthode : `verifier_anti_rejeu()`

**Rôle** : Empêcher qu'une transaction soit rejouée (attaque)

```python
def verifier_anti_rejeu(self, transaction_id: str, timestamp: float) -> Tuple[bool, str]:
    # 1. Vérifier que cet ID n'a jamais été vu
    if transaction_id in self.transactions_vues:
        return False, "Transaction déjà traitée (attaque par rejeu détectée)"
    
    # 2. Vérifier que le timestamp est récent (< 5 minutes)
    temps_actuel = time.time()
    if abs(temps_actuel - timestamp) > 300:  # 300 secondes = 5 minutes
        return False, "Transaction expirée (timestamp trop ancien/futur)"
    
    # ✅ Tout est bon
    return True, "Transaction unique et récente"
```

**Attaque par rejeu** :
1. Un attaquant intercepte une transaction valide
2. Il essaie de la "rejouer" pour acheter 2 fois
3. La protection détecte que l'ID a déjà été utilisé → REFUSÉ

**Fenêtre de 5 minutes** :
- Empêche de rejouer une vieille transaction
- Empêche d'envoyer une transaction avec une date future

---

## 🏦 Classe Banque

### Rôle

La banque :
1. Garde les comptes avec les soldes
2. Autorise ou refuse les paiements
3. Génère les ARQC (cryptogrammes)
4. Garde l'historique des transactions

### Initialisation

```python
class Banque(Entite):
    def __init__(self, ca: AutoriteCertification):
        # Hérite de Entite → génère clés + certificat
        super().__init__("Banque Centrale", ca)
        
        # Base de données des comptes
        self.comptes = {
            "4970-1111-2222-3333": {"solde": 5000, "titulaire": "Alice"},
            "4970-4444-5555-6666": {"solde": 100, "titulaire": "Bob"},
            "4970-7777-8888-9999": {"solde": 50000, "titulaire": "Charlie"}
        }
        
        # Historique de toutes les transactions
        self.historique_transactions = []
```

**Structure d'un compte** :
```python
{
    "numéro de carte": {
        "solde": montant en euros,
        "titulaire": nom du propriétaire
    }
}
```

### Méthode : `verifier_paiement()`

**Rôle** : Autoriser ou refuser un paiement

```python
def verifier_paiement(self, paquet_paiement_chiffre: bytes, transaction_id: str, timestamp: float) -> Tuple[bool, str, Optional[str]]:
    print(f"\n   -> [Banque] Réception demande d'autorisation (ID: {transaction_id[:8]}...)")
    
    # 1. PROTECTION ANTI-REJEU
    anti_rejeu_ok, raison = self.verifier_anti_rejeu(transaction_id, timestamp)
    if not anti_rejeu_ok:
        print(f"   -> [Banque] ❌ {raison}")
        return False, raison, None
    
    try:
        # 2. DÉCHIFFREMENT DES INFOS DE PAIEMENT
        # Seule la banque peut déchiffrer (clé privée)
        infos_paiement_bytes = self.dechiffrer(paquet_paiement_chiffre)
        infos = json.loads(infos_paiement_bytes.decode())
        
        # Extraire les données
        carte = infos['carte']
        montant = infos['montant']
        nonce = infos['nonce']
        
        print(f"   -> [Banque] 🔓 Déchiffrement réussi")
        print(f"   -> [Banque] Carte: {carte}, Montant: {montant}€")
        
        # 3. VÉRIFICATION DE LA CARTE
        if carte not in self.comptes:
            print("   -> [Banque] ❌ Carte inconnue")
            return False, "Carte invalide", None
        
        # 4. VÉRIFICATION DU SOLDE
        compte = self.comptes[carte]
        if compte['solde'] < montant:
            print(f"   -> [Banque] ❌ Solde insuffisant ({compte['solde']}€ disponible)")
            return False, "Fonds insuffisants", None
        
        # 5. DÉBIT DU COMPTE
        self.comptes[carte]['solde'] -= montant
        
        # 6. GÉNÉRATION DE L'ARQC (Cryptogramme)
        arqc = self._generer_arqc(transaction_id, montant, carte)
        
        # 7. ENREGISTREMENT DE LA TRANSACTION
        self.transactions_vues.add(transaction_id)
        
        transaction_record = {
            'id': transaction_id,
            'carte': carte,
            'montant': montant,
            'timestamp': timestamp,
            'arqc': arqc,
            'statut': 'approuvé'
        }
        self.historique_transactions.append(transaction_record)
        
        print(f"   -> [Banque] ✅ Paiement autorisé. Nouveau solde: {compte['solde']}€")
        print(f"   -> [Banque] 🔐 ARQC généré: {arqc[:16]}...")
        
        # ✅ RETOUR : (succès=True, message, ARQC)
        return True, "Autorisation accordée", arqc
        
    except Exception as e:
        print(f"   -> [Banque] ❌ Erreur: {e}")
        return False, f"Erreur technique: {str(e)}", None
```

**Étapes en détail** :

#### Étape 1 : Protection Anti-Rejeu
```python
anti_rejeu_ok, raison = self.verifier_anti_rejeu(transaction_id, timestamp)
```
- Vérifie que l'ID n'a jamais été vu
- Vérifie que le timestamp est récent

#### Étape 2 : Déchiffrement
```python
infos_paiement_bytes = self.dechiffrer(paquet_paiement_chiffre)
```
- **Crucial** : Seule la banque peut déchiffrer
- Le marchand ne peut PAS voir ces infos
- C'est ça la confidentialité SET !

#### Étape 3 : Vérification Carte
```python
if carte not in self.comptes:
    return False, "Carte invalide", None
```
- La carte existe-t-elle ?

#### Étape 4 : Vérification Solde
```python
if compte['solde'] < montant:
    return False, "Fonds insuffisants", None
```
- Y a-t-il assez d'argent ?

#### Étape 5 : Débit
```python
self.comptes[carte]['solde'] -= montant
```
- On retire l'argent du compte

#### Étape 6 : ARQC
```python
arqc = self._generer_arqc(transaction_id, montant, carte)
```
- Génère un cryptogramme unique
- Preuve que la banque a approuvé

### Méthode : `_generer_arqc()`

**Rôle** : Créer un cryptogramme unique pour cette transaction

```python
def _generer_arqc(self, transaction_id: str, montant: float, carte: str) -> str:
    # Combiner les données de la transaction
    data = f"{transaction_id}{montant}{carte}{time.time()}".encode()
    
    # Calculer le hash SHA-256
    return hashlib.sha256(data).hexdigest()
```

**Qu'est-ce qu'un ARQC ?**
- **A**pplication **R**equest **C**ryptogram
- C'est comme un "tampon" unique de la banque
- Preuve que la banque a bien autorisé cette transaction
- Impossible à falsifier (hash)

---

## 🛒 Classe Marchand

### Rôle

Le marchand :
1. Reçoit les commandes des clients
2. Vérifie les signatures
3. Vérifie les certificats
4. Transmet les paiements à la banque
5. Expédie si tout est OK

### Initialisation

```python
class Marchand(Entite):
    def __init__(self, nom: str, ca: AutoriteCertification, banque: 'Banque'):
        super().__init__(nom, ca)
        
        # Référence vers la banque
        self.banque = banque
        
        # Liste de toutes les commandes
        self.commandes = []
```

### Méthode : `traiter_commande()`

**Rôle** : Traiter une commande reçue d'un client

```python
def traiter_commande(self, paquet_commande: dict) -> Tuple[bool, str]:
    print(f"\n{'='*70}")
    print(f"[{self.nom}] 📦 Nouvelle commande reçue")
    print(f"{'='*70}")
    
    try:
        # 1. EXTRACTION DES DONNÉES DU PAQUET
        oi_clair = paquet_commande['order_info']         # Info commande (clair)
        pi_chiffre = paquet_commande['payment_info_enc'] # Info paiement (chiffré)
        signature = paquet_commande['signature']
        certificat_client = paquet_commande['certificat_client']
        transaction_id = paquet_commande['transaction_id']
        timestamp = paquet_commande['timestamp']
        
        print(f"[{self.nom}] Transaction ID: {transaction_id[:16]}...")
        print(f"[{self.nom}] Articles: {oi_clair['items']}")
        print(f"[{self.nom}] Montant: {oi_clair['montant']}€")
        
        # 2. VÉRIFICATION ANTI-REJEU
        anti_rejeu_ok, raison = self.verifier_anti_rejeu(transaction_id, timestamp)
        if not anti_rejeu_ok:
            print(f"[{self.nom}] ❌ {raison}")
            return False, raison
        
        # 3. VÉRIFICATION DE LA SIGNATURE
        # Recréer les données qui ont été signées
        donnees_combinees = json.dumps(oi_clair, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
        
        sig_valide, raison_sig = self.verifier_signature(donnees_combinees, signature, certificat_client)
        
        if not sig_valide:
            print(f"[{self.nom}] ❌ {raison_sig}")
            return False, raison_sig
        
        print(f"[{self.nom}] ✅ Signature client validée")
        print(f"[{self.nom}] ✅ Certificat client vérifié ({certificat_client.sujet})")
        print(f"[{self.nom}] 🔒 Informations de paiement chiffrées (invisibles pour le marchand)")
        
        # 4. DEMANDE D'AUTORISATION À LA BANQUE
        print(f"[{self.nom}] 📡 Demande d'autorisation à la banque...")
        
        succes_banque, msg_banque, arqc = self.banque.verifier_paiement(
            pi_chiffre, transaction_id, timestamp
        )
        
        if succes_banque:
            # ✅ PAIEMENT AUTORISÉ
            self.transactions_vues.add(transaction_id)
            
            # Enregistrer la commande
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
            # ❌ PAIEMENT REFUSÉ
            print(f"\n{'='*70}")
            print(f"[{self.nom}] ⛔ COMMANDE REFUSÉE: {msg_banque}")
            print(f"{'='*70}\n")
            return False, f"Paiement refusé: {msg_banque}"
            
    except Exception as e:
        print(f"[{self.nom}] ❌ Erreur lors du traitement: {e}")
        return False, f"Erreur technique: {str(e)}"
```

**Point clé** : Le marchand voit :
- ✅ Les articles commandés (Order Info)
- ✅ Le montant
- ❌ **PAS** le numéro de carte (chiffré pour la banque)

---

## 💳 Classe Client

### Rôle

Le client :
1. Crée les commandes
2. Chiffre les infos de paiement pour la banque
3. Signe la transaction
4. Envoie le tout au marchand

### Initialisation

```python
class Client(Entite):
    def __init__(self, nom: str, num_carte: str, ca: AutoriteCertification):
        super().__init__(nom, ca)
        
        # Numéro de carte bancaire
        self.carte = num_carte
        
        # Historique des achats
        self.historique_achats = []
```

### Méthode : `acheter()`

**Rôle** : Effectuer un achat sécurisé

```python
def acheter(self, marchand: Marchand, liste_items: List[str], montant: float) -> Tuple[bool, str]:
    print(f"\n{'#'*70}")
    print(f"# 🛒 CLIENT: {self.nom} - NOUVEL ACHAT")
    print(f"{'#'*70}")
    
    # 1. GÉNÉRATION D'IDENTIFIANTS UNIQUES
    transaction_id = str(uuid.uuid4())  # ID unique universel
    timestamp = time.time()              # Temps actuel
    nonce = get_random_bytes(16).hex()  # Nombre aléatoire
    
    print(f"[{self.nom}] Génération transaction ID: {transaction_id[:16]}...")
    print(f"[{self.nom}] Articles: {liste_items}")
    print(f"[{self.nom}] Montant: {montant}€")
    
    # 2. PRÉPARATION ORDER INFO (OI)
    # → Ce que le marchand PEUT voir
    oi = {
        "items": liste_items,
        "montant": montant,
        "client": self.nom,
        "timestamp": timestamp
    }
    
    # 3. PRÉPARATION PAYMENT INFO (PI)
    # → Ce que SEULE la banque peut voir
    pi = {
        "carte": self.carte,        # ← SENSIBLE
        "montant": montant,
        "nonce": nonce,             # ← Unicité
        "transaction_id": transaction_id
    }
    
    # 4. CHIFFREMENT DU PI POUR LA BANQUE
    print(f"[{self.nom}] 🔐 Chiffrement des informations de paiement pour la banque...")
    cle_pub_banque = marchand.banque.get_public_key()
    pi_chiffre = self.chiffrer_pour(json.dumps(pi).encode(), cle_pub_banque)
    
    # 5. DOUBLE SIGNATURE
    print(f"[{self.nom}] ✍️  Signature de la transaction...")
    donnees_combinees = json.dumps(oi, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
    signature = self.signer_donnee(donnees_combinees)
    
    # 6. CRÉATION DU PAQUET SET
    paquet = {
        "order_info": oi,
        "payment_info_enc": pi_chiffre,
        "signature": signature,
        "certificat_client": self.certificat,
        "transaction_id": transaction_id,
        "timestamp": timestamp
    }
    
    # 7. ENVOI AU MARCHAND
    print(f"[{self.nom}] 📤 Envoi du paquet sécurisé à {marchand.nom}...")
    
    succes, message = marchand.traiter_commande(paquet)
    
    # 8. ENREGISTREMENT DANS L'HISTORIQUE
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
```

**Étapes détaillées** :

#### Étape 1 : Génération d'identifiants
```python
transaction_id = str(uuid.uuid4())  # Ex: "a3f2d9e1-..."
timestamp = time.time()              # Ex: 1674395821.45
nonce = get_random_bytes(16).hex()  # Ex: "a3b5c7..."
```

#### Étape 2-3 : Séparation OI / PI
```python
# OI = Order Info (pour le marchand)
oi = {"items": [...], "montant": 45}

# PI = Payment Info (pour la banque UNIQUEMENT)
pi = {"carte": "4970-...", "montant": 45}
```

**CRUCIAL** : Cette séparation garantit que le marchand ne voit jamais la carte !

#### Étape 4 : Chiffrement
```python
pi_chiffre = self.chiffrer_pour(
    json.dumps(pi).encode(),  # Convertir PI en bytes
    cle_pub_banque            # Chiffrer avec clé publique banque
)
```

**Résultat** :
- `pi` (clair) : `{"carte": "4970-1111-2222-3333", ...}`
- `pi_chiffre` : `b'\x8a\x3f\x9e...'` (illisible)
- Seule la banque peut déchiffrer

#### Étape 5 : Double Signature
```python
donnees_combinees = OI + PI_chiffré + transaction_id
signature = signer(donnees_combinees)
```

**Pourquoi "double" ?**
- On signe à la fois l'OI (commande) et le PI chiffré (paiement)
- Garantit que les deux sont liés
- Empêche de modifier le montant après signature

#### Étape 6 : Paquet SET
```python
paquet = {
    "order_info": oi,           # Clair
    "payment_info_enc": pi_chiffre,  # Chiffré
    "signature": signature,
    "certificat_client": self.certificat,
    "transaction_id": transaction_id,
    "timestamp": timestamp
}
```

**Contenu du paquet** :
- Info commande (visible marchand)
- Info paiement (invisible marchand, visible banque)
- Signature (pour vérifier)
- Certificat (pour authentifier)
- IDs (pour tracer)

---

## 🧪 Fonctions de Test

### Test 1 : Attaque par Rejeu

```python
def test_attaque_rejeu(client: Client, marchand: Marchand):
    print(f"\n{'='*70}")
    print("🔴 TEST ATTAQUE PAR REJEU")
    print(f"{'='*70}")
    
    # 1. Créer une transaction
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
    
    # 2. Premier envoi (légitime)
    print("Premier envoi (légitime):")
    marchand.traiter_commande(paquet)
    
    # 3. Deuxième envoi (REJEU - attaque)
    print("\n⚠️  Tentative de rejeu du même paquet:")
    marchand.traiter_commande(paquet)
```

**Résultat attendu** :
- 1er envoi : ✅ Accepté
- 2e envoi : ❌ Refusé ("Transaction déjà traitée")

### Test 2 : Certificat Révoqué

```python
def test_certificat_revoque(ca: AutoriteCertification, banque: Banque):
    print(f"\n{'='*70}")
    print("🔴 TEST CERTIFICAT RÉVOQUÉ")
    print(f"{'='*70}")
    
    # 1. Créer un "attaquant"
    attaquant = Client("Attaquant", "4970-9999-9999-9999", ca)
    
    # 2. Révoquer son certificat
    print(f"\n⚠️  Révocation du certificat de l'attaquant...")
    ca.revoquer_certificat(attaquant.certificat.numero_serie)
    
    # 3. Créer un marchand de test
    marchand_test = Marchand("MarchandTest", ca, banque)
    
    # 4. Tenter un achat
    print(f"\nTentative d'achat avec certificat révoqué:")
    attaquant.acheter(marchand_test, ["Article volé"], 50)
```

**Résultat attendu** :
- ❌ Refusé ("Certificat invalide: Certificat révoqué")

### Test 3 : Manipulation de Montant

```python
def test_manipulation_montant(client: Client, marchand: Marchand):
    print(f"\n{'='*70}")
    print("🔴 TEST MANIPULATION DE MONTANT")
    print(f"{'='*70}")
    
    # 1. Créer transaction avec montant 10€
    transaction_id = str(uuid.uuid4())
    timestamp = time.time()
    
    oi_legitime = {"items": ["Article"], "montant": 10, "client": client.nom, "timestamp": timestamp}
    pi = {"carte": client.carte, "montant": 10, "nonce": get_random_bytes(16).hex(), "transaction_id": transaction_id}
    
    pi_chiffre = client.chiffrer_pour(json.dumps(pi).encode(), marchand.banque.get_public_key())
    donnees_combinees = json.dumps(oi_legitime, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
    signature = client.signer_donnee(donnees_combinees)
    
    # 2. MODIFIER le montant à 1€ APRÈS signature
    oi_modifie = {"items": ["Article"], "montant": 1, "client": client.nom, "timestamp": timestamp}
    
    paquet_modifie = {
        "order_info": oi_modifie,  # ← Modifié !
        "payment_info_enc": pi_chiffre,
        "signature": signature,     # ← Signature de l'ancien montant
        "certificat_client": client.certificat,
        "transaction_id": transaction_id,
        "timestamp": timestamp
    }
    
    # 3. Envoyer
    print("⚠️  Tentative avec montant modifié après signature:")
    marchand.traiter_commande(paquet_modifie)
```

**Résultat attendu** :
- ❌ Refusé ("Signature cryptographique invalide")

**Pourquoi ça échoue ?**
- La signature a été calculée sur `montant=10`
- Le paquet contient `montant=1`
- Lors de la vérification, le hash ne correspond plus
- La signature est invalide

---

## 🔄 Flux Complet d'une Transaction

### Étape par Étape

#### Phase 1 : Initialisation du Système

```python
# 1. Créer l'Autorité de Certification
ca = AutoriteCertification()

# 2. Créer la Banque (reçoit un certificat de la CA)
banque = Banque(ca)

# 3. Créer les Marchands (reçoivent des certificats)
amazon = Marchand("Amazon", ca, banque)
fnac = Marchand("FNAC", ca, banque)

# 4. Créer les Clients (reçoivent des certificats)
alice = Client("Alice", "4970-1111-2222-3333", ca)
bob = Client("Bob", "4970-4444-5555-6666", ca)
```

**Résultat** :
- CA possède son certificat racine
- Tous ont des certificats signés par la CA
- Chaîne de confiance établie

#### Phase 2 : Alice achète chez Amazon

```python
alice.acheter(amazon, ["Livre Python"], 45)
```

**Détail du flux** :

##### 1. Alice prépare sa commande
```python
# OI (Order Info) - Visible par Amazon
oi = {
    "items": ["Livre Python"],
    "montant": 45,
    "client": "Alice"
}

# PI (Payment Info) - Visible UNIQUEMENT par la banque
pi = {
    "carte": "4970-1111-2222-3333",
    "montant": 45,
    "nonce": "a3f9e2..."
}
```

##### 2. Alice chiffre le PI
```python
# Récupérer la clé publique de la banque
cle_banque = amazon.banque.get_public_key()

# Chiffrer avec cette clé
pi_chiffre = alice.chiffrer_pour(pi, cle_banque)
```

**État** :
- Amazon ne peut PAS déchiffrer `pi_chiffre`
- Seule la banque le peut

##### 3. Alice signe tout
```python
donnees = OI + PI_chiffré + transaction_id
signature = alice.signer_donnee(donnees)
```

##### 4. Alice envoie le paquet à Amazon
```python
paquet = {
    "order_info": oi,
    "payment_info_enc": pi_chiffre,
    "signature": signature,
    "certificat_client": alice.certificat,
    "transaction_id": "uuid...",
    "timestamp": 1674395821.45
}

amazon.traiter_commande(paquet)
```

##### 5. Amazon vérifie
```python
# Vérifier anti-rejeu
✅ Transaction ID jamais vu
✅ Timestamp récent (< 5 min)

# Vérifier le certificat d'Alice
✅ Certificat signé par la CA
✅ Pas expiré
✅ Pas révoqué

# Vérifier la signature
donnees_reconstruites = OI + PI_chiffré + transaction_id
✅ Signature valide avec la clé publique d'Alice
```

##### 6. Amazon transmet à la Banque
```python
banque.verifier_paiement(pi_chiffre, transaction_id, timestamp)
```

##### 7. Banque déchiffre et vérifie
```python
# Déchiffrer le PI
pi = banque.dechiffrer(pi_chiffre)
# → {"carte": "4970-1111-2222-3333", "montant": 45}

# Vérifier le solde
solde_alice = 5000€
montant = 45€
✅ Solde suffisant

# Débiter
5000€ - 45€ = 4955€
```

##### 8. Banque génère l'ARQC
```python
arqc = SHA256(transaction_id + montant + carte + timestamp)
# → "a3f2d9e1b5c7..."
```

##### 9. Banque retourne la réponse
```python
return (True, "Autorisation accordée", "a3f2d9e1...")
```

##### 10. Amazon expédie
```python
if succes_banque:
    enregistrer_commande()
    print("🎉 COMMANDE VALIDÉE")
```

### Diagramme du Flux Complet

```
ALICE                    AMAZON                  BANQUE                CA
  │                        │                        │                  │
  │ 1. Demande cert.       │                        │                  │
  │────────────────────────┼────────────────────────┼─────────────────>│
  │                        │                        │                  │
  │ 2. Certificat signé    │                        │                  │
  │<───────────────────────┼────────────────────────┼──────────────────│
  │                        │                        │                  │
  │ 3. Prépare OI + PI     │                        │                  │
  │                        │                        │                  │
  │ 4. Chiffre PI (clé pub banque)                  │                  │
  │                        │                        │                  │
  │ 5. Signe OI + PI_chiffré                        │                  │
  │                        │                        │                  │
  │ 6. Envoie paquet SET   │                        │                  │
  │───────────────────────>│                        │                  │
  │                        │                        │                  │
  │                        │ 7. Vérifie signature   │                  │
  │                        │                        │                  │
  │                        │ 8. Vérifie certificat  │                  │
  │                        │────────────────────────┼─────────────────>│
  │                        │                        │                  │
  │                        │ 9. Certificat OK       │                  │
  │                        │<───────────────────────┼──────────────────│
  │                        │                        │                  │
  │                        │ 10. Transmet PI_chiffré│                  │
  │                        │───────────────────────>│                  │
  │                        │                        │                  │
  │                        │                        │ 11. Déchiffre PI │
  │                        │                        │                  │
  │                        │                        │ 12. Vérifie solde│
  │                        │                        │                  │
  │                        │                        │ 13. Débite       │
  │                        │                        │                  │
  │                        │                        │ 14. Génère ARQC  │
  │                        │                        │                  │
  │                        │ 15. Autorisation + ARQC│                  │
  │                        │<───────────────────────│                  │
  │                        │                        │                  │
  │                        │ 16. Expédie commande   │                  │
  │                        │                        │                  │
  │ 17. Confirmation       │                        │                  │
  │<───────────────────────│                        │                  │
```

---

## 🔑 Points Clés à Retenir

### 1. Séparation OI / PI
- **OI** (Order Info) : Visible par le marchand
- **PI** (Payment Info) : Chiffré, visible UNIQUEMENT par la banque

### 2. Chiffrement Asymétrique
- **Clé publique** : Tout le monde peut chiffrer
- **Clé privée** : Seul le propriétaire peut déchiffrer

### 3. Signature Numérique
- **Signer** : Avec ma clé privée
- **Vérifier** : Avec ma clé publique
- Prouve l'authenticité et l'intégrité

### 4. Certificats
- **Émis par** : Autorité de Certification
- **Contient** : Clé publique + infos propriétaire
- **Signé par** : Clé privée de la CA
- **Prouve** : L'identité de l'entité

### 5. Protection Anti-Rejeu
- **Transaction ID** : Unique, jamais réutilisé
- **Timestamp** : Fenêtre de 5 minutes
- **Nonce** : Aléatoire, garantit unicité

### 6. ARQC
- **Cryptogramme** : Preuve de l'autorisation bancaire
- **Unique** : Par transaction
- **Calcul** : SHA-256(données transaction)

---

## ❓ Questions que Votre Prof Peut Poser

### Q1 : Pourquoi le marchand ne peut pas voir la carte ?

**Réponse** :
Le Payment Info (PI) est chiffré avec la **clé publique de la banque**. Seule la banque possède la **clé privée** correspondante. Le marchand n'a pas cette clé privée, donc il ne peut pas déchiffrer.

### Q2 : Comment on empêche la modification du montant ?

**Réponse** :
La **double signature** ! On signe à la fois l'Order Info (qui contient le montant) ET le Payment Info chiffré. Si quelqu'un modifie le montant après, la signature ne correspond plus et la transaction est rejetée.

### Q3 : C'est quoi la différence entre chiffrer et signer ?

**Réponse** :
- **Chiffrer** : Cacher des données (confidentialité)
  - Avec clé publique du destinataire
  - Seul lui peut déchiffrer
  
- **Signer** : Prouver l'authenticité (intégrité + authentification)
  - Avec ma clé privée
  - Tout le monde peut vérifier avec ma clé publique

### Q4 : Pourquoi RSA 2048 bits ?

**Réponse** :
- Plus sécurisé que 1024 bits (considéré faible maintenant)
- Recommandé par les standards actuels (NIST, ANSSI)
- Impossible à casser avec les ordinateurs actuels
- Bon compromis entre sécurité et performance

### Q5 : C'est quoi un certificat "auto-signé" ?

**Réponse** :
C'est un certificat signé par soi-même. L'Autorité de Certification se signe elle-même car il n'y a personne au-dessus d'elle. C'est la "racine de confiance". Tous les autres certificats sont signés par la CA.

---

## ✅ Checklist de Compréhension

Avant de présenter à votre prof, vérifiez que vous pouvez expliquer :

- [ ] Ce qu'est le protocole SET
- [ ] La différence entre chiffrement et signature
- [ ] Pourquoi le marchand ne voit pas la carte
- [ ] Comment fonctionne un certificat
- [ ] Le rôle de l'Autorité de Certification
- [ ] Comment la protection anti-rejeu fonctionne
- [ ] Ce qu'est un ARQC et pourquoi c'est utile
- [ ] Le flux complet d'une transaction
- [ ] Comment la double signature empêche la fraude
- [ ] Pourquoi RSA est asymétrique

---

**Bonne présentation ! 🚀**
