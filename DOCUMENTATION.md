# Simulation du Protocole SET/CDA
## Secure Electronic Transaction avec Combined DDA / Application Cryptogram Generation

---

## 📋 Table des Matières

1. [Présentation du Projet](#présentation-du-projet)
2. [Architecture du Système](#architecture-du-système)
3. [Fonctionnalités Implémentées](#fonctionnalités-implémentées)
4. [Installation et Utilisation](#installation-et-utilisation)
5. [Analyse de Sécurité](#analyse-de-sécurité)
6. [Tests et Validation](#tests-et-validation)
7. [Améliorations Possibles](#améliorations-possibles)

---

## 🎯 Présentation du Projet

Ce projet implémente une **simulation complète du protocole SET (Secure Electronic Transaction)** avec le protocole **CDA (Combined DDA / Application Cryptogram Generation)**. Il s'agit d'un système de paiement électronique sécurisé permettant des transactions en ligne avec garanties de :

- **Confidentialité** : Les informations de paiement sont chiffrées
- **Intégrité** : Les données ne peuvent être modifiées sans détection
- **Authentification** : Chaque entité est identifiée par un certificat X.509
- **Non-répudiation** : Les signatures numériques prouvent l'origine des transactions

### Objectifs Pédagogiques

✅ Comprendre le fonctionnement du protocole SET  
✅ Maîtriser la cryptographie asymétrique (RSA)  
✅ Implémenter un système de PKI (Public Key Infrastructure)  
✅ Développer une application web sécurisée avec Flask  
✅ Analyser et renforcer la sécurité d'un système

---

## 🏗️ Architecture du Système

### Entités du Système

Le système comprend **4 entités principales** :

#### 1️⃣ Autorité de Certification (CA)
- **Rôle** : Émettre et gérer les certificats numériques
- **Responsabilités** :
  - Génération de certificats X.509
  - Signature des certificats avec sa clé privée
  - Révocation de certificats compromis
  - Vérification de la chaîne de confiance
- **Sécurité** : Certificat racine auto-signé, clé RSA 2048 bits

#### 2️⃣ Client (Acheteur)
- **Rôle** : Effectuer des achats en ligne de manière sécurisée
- **Responsabilités** :
  - Créer les Order Info (OI) et Payment Info (PI)
  - Chiffrer le PI avec la clé publique de la banque
  - Signer la transaction avec sa clé privée (double signature)
  - Envoyer le paquet SET au marchand
- **Attributs** : Nom, numéro de carte bancaire, certificat X.509

#### 3️⃣ Marchand (Vendeur)
- **Rôle** : Traiter les commandes des clients
- **Responsabilités** :
  - Vérifier la signature du client
  - Vérifier le certificat du client auprès de la CA
  - Transférer le PI chiffré à la banque pour autorisation
  - Expédier la commande si paiement autorisé
- **Particularité** : Ne peut PAS déchiffrer les informations bancaires du client

#### 4️⃣ Banque
- **Rôle** : Autoriser ou refuser les paiements
- **Responsabilités** :
  - Déchiffrer le PI avec sa clé privée
  - Vérifier le solde du compte
  - Débiter le compte si autorisation accordée
  - Générer un ARQC (Application Request Cryptogram)
  - Détecter les tentatives de rejeu
- **Données** : Gestion des comptes clients, historique des transactions

### Flux de Transaction

```
┌─────────┐         ┌──────────┐         ┌─────────┐         ┌────────────┐
│ Client  │         │ Marchand │         │ Banque  │         │     CA     │
└────┬────┘         └─────┬────┘         └────┬────┘         └──────┬─────┘
     │                    │                   │                     │
     │ 1. Demande cert.   │                   │                     │
     │────────────────────┼───────────────────┼────────────────────>│
     │                    │                   │                     │
     │ 2. Certificat émis │                   │                     │
     │<───────────────────┼───────────────────┼─────────────────────│
     │                    │                   │                     │
     │ 3. Création paquet SET (OI + PI chiffré + Signature)         │
     │                    │                   │                     │
     │ 4. Envoi paquet    │                   │                     │
     │───────────────────>│                   │                     │
     │                    │                   │                     │
     │                    │ 5. Vérification signature + certificat  │
     │                    │───────────────────┼────────────────────>│
     │                    │                   │                     │
     │                    │ 6. Certificat OK  │                     │
     │                    │<──────────────────┼─────────────────────│
     │                    │                   │                     │
     │                    │ 7. Demande autorisation (PI chiffré)    │
     │                    │──────────────────>│                     │
     │                    │                   │                     │
     │                    │                   │ 8. Déchiffrement PI │
     │                    │                   │ Vérification solde  │
     │                    │                   │ Génération ARQC     │
     │                    │                   │                     │
     │                    │ 9. Autorisation + ARQC                  │
     │                    │<──────────────────│                     │
     │                    │                   │                     │
     │                    │ 10. Expédition commande                 │
     │                    │                   │                     │
     │ 11. Confirmation   │                   │                     │
     │<───────────────────│                   │                     │
     │                    │                   │                     │
```

---

## ✨ Fonctionnalités Implémentées

### 🔐 Cryptographie

#### Chiffrement Asymétrique (RSA)
- **Algorithme** : RSA 2048 bits
- **Padding** : PKCS1_OAEP
- **Usage** : 
  - Chiffrement du Payment Info pour la banque
  - Le marchand ne peut pas déchiffrer les données bancaires
  - Seule la banque possède la clé privée correspondante

#### Signatures Numériques
- **Algorithme** : SHA-256 with RSA
- **Padding** : PKCS#1 v1.5
- **Double Signature** :
  - Signature de : `OI + PI_chiffré + Transaction_ID`
  - Garantit l'intégrité et l'authenticité
  - Empêche la modification des données

### 📜 Gestion des Certificats X.509

#### Classe `Certificat`
Attributs :
- `numero_serie` : Identifiant unique (UUID)
- `sujet` : Entité à qui appartient le certificat
- `emetteur` : Autorité de Certification
- `cle_publique` : Clé publique RSA du sujet
- `date_creation` : Date d'émission
- `date_expiration` : Date de fin de validité
- `signature` : Signature de la CA
- `revoque` : État de révocation

Méthodes :
- `signer()` : Signature par la CA
- `verifier_signature()` : Vérification de l'authenticité
- `est_valide()` : Vérification de la validité (date, révocation)
- `revoquer()` : Révocation du certificat

### 🛡️ Sécurité Avancée

#### Protection Anti-Rejeu
- **Mécanisme** : Tracking des transaction IDs
- **Validation** : 
  - Vérification que l'ID n'a jamais été utilisé
  - Fenêtre temporelle de 5 minutes (300 secondes)
  - Détection des tentatives de rejeu

```python
def verifier_anti_rejeu(self, transaction_id: str, timestamp: float):
    if transaction_id in self.transactions_vues:
        return False, "Attaque par rejeu détectée"
    
    temps_actuel = time.time()
    if abs(temps_actuel - timestamp) > 300:
        return False, "Transaction expirée"
    
    return True, "Transaction unique et récente"
```

#### Génération de Nonces
- **Usage** : Garantir l'unicité de chaque transaction
- **Implémentation** : `get_random_bytes(16)` (128 bits)
- **Intégration** : Inclus dans le Payment Info

#### ARQC (Application Request Cryptogram)
- **Définition** : Cryptogramme unique généré par la banque
- **Calcul** : `SHA-256(Transaction_ID + Montant + Carte + Timestamp)`
- **Rôle** : Preuve de l'autorisation bancaire

### 🌐 Interface Web Flask

#### Pages Implémentées

1. **Page d'Accueil** (`/`)
   - Présentation du protocole
   - Architecture du système
   - Guide de démarrage rapide

2. **Dashboard** (`/dashboard`)
   - Statistiques en temps réel
   - Graphiques d'activité (Chart.js)
   - Monitoring des transactions
   - Logs système en direct

3. **Interface Client** (`/client`)
   - Formulaire d'achat sécurisé
   - Sélection client/marchand
   - Affichage du solde en temps réel
   - Historique des achats

4. **Interface Marchand** (`/marchand`)
   - Liste des commandes reçues
   - Statistiques par marchand (CA, panier moyen)
   - Détails des transactions
   - Visualisation des ARQC

5. **Interface Banque** (`/banque`)
   - Gestion des comptes clients
   - Historique complet des transactions
   - Monitoring de sécurité
   - Tableau de bord des autorisations

6. **Gestion Certificats** (`/certificats`)
   - Liste de tous les certificats
   - Création de nouveaux clients avec certificats
   - Révocation de certificats
   - Visualisation détaillée (modal)

#### Technologies Utilisées
- **Backend** : Flask 3.0
- **WebSockets** : Flask-SocketIO (communication temps réel)
- **Frontend** : Bootstrap 5 + Bootstrap Icons
- **Graphiques** : Chart.js
- **Design** : Interface moderne avec gradients et animations

---

## 🚀 Installation et Utilisation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation

```bash
# 1. Cloner ou télécharger le projet
cd /chemin/vers/TP_Cyber

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer la simulation en ligne de commande
python projet.py

# 4. Lancer l'interface web
python app.py
```

### Accès à l'Interface Web

Ouvrir un navigateur et accéder à : **http://localhost:5000**

### Utilisation

#### Effectuer un Achat

1. Aller sur **Interface Client**
2. Sélectionner un client (Alice, Bob, Charlie)
3. Choisir un marchand (Amazon, FNAC, Darty)
4. Ajouter des articles
5. Indiquer le montant
6. Cliquer sur "Effectuer l'Achat Sécurisé"
7. Observer les logs en temps réel dans le Dashboard

#### Créer un Nouveau Client

1. Aller sur **Certificats**
2. Remplir le formulaire "Nouveau Client"
3. Le système génère automatiquement :
   - Paire de clés RSA
   - Certificat X.509 signé par la CA
   - Enregistrement du client

#### Révoquer un Certificat

1. Aller sur **Certificats**
2. Cliquer sur l'icône de révocation (❌) à côté du certificat
3. Confirmer la révocation
4. Le certificat devient invalide immédiatement

---

## 🔒 Analyse de Sécurité

### Points Forts

#### 1. Confidentialité des Données Bancaires
✅ **Protection efficace** : Le Payment Info est chiffré avec RSA-2048  
✅ **Isolation** : Le marchand ne peut jamais voir le numéro de carte  
✅ **Déchiffrement unique** : Seule la banque possède la clé privée

**Code critique** :
```python
# Chiffrement pour la banque uniquement
cle_pub_banque = marchand.banque.get_public_key()
pi_chiffre = self.chiffrer_pour(json.dumps(pi).encode(), cle_pub_banque)
```

#### 2. Authentification Forte
✅ **Certificats X.509** : Chaque entité possède un certificat signé par la CA  
✅ **Vérification stricte** : Le marchand vérifie le certificat avant traitement  
✅ **Chaîne de confiance** : Tous les certificats sont signés par la CA racine

#### 3. Intégrité et Non-Répudiation
✅ **Double Signature** : OI + PI_chiffré + Transaction_ID  
✅ **Hash SHA-256** : Garantit la détection de toute modification  
✅ **Non-répudiation** : La signature prouve l'origine du client

#### 4. Protection Contre les Attaques

**Attaque par Rejeu** :
```python
# Détection
if transaction_id in self.transactions_vues:
    return False, "Attaque par rejeu détectée"

# Validation temporelle
if abs(temps_actuel - timestamp) > 300:
    return False, "Transaction expirée"
```

**Man-in-the-Middle** :
- Les certificats préviennent l'usurpation d'identité
- La signature garantit que les données viennent du bon client

**Manipulation de Montant** :
- La signature couvre le montant dans OI ET PI
- Toute modification invalide la signature

#### 5. Génération de Cryptogrammes (ARQC)
✅ **Unicité** : SHA-256(Transaction_ID + Montant + Carte + Timestamp)  
✅ **Traçabilité** : Chaque transaction a un cryptogramme unique  
✅ **Validation** : Permet de vérifier l'autorisation bancaire

### Vulnérabilités Identifiées

#### ⚠️ Vulnérabilité 1 : Absence de CRL Distribuée

**Problème** : Les certificats révoqués sont stockés localement  
**Impact** : Dans un système distribué, les révocations ne se propagent pas  
**Risque** : Utilisation de certificats révoqués avant synchronisation

**Mesure corrective** :
```python
# Implémenter une CRL (Certificate Revocation List)
class CRL:
    def __init__(self):
        self.revoked_serials = set()
        self.last_update = datetime.now()
    
    def add_revoked(self, serial):
        self.revoked_serials.add(serial)
        self.last_update = datetime.now()
    
    def is_revoked(self, serial):
        return serial in self.revoked_serials
```

#### ⚠️ Vulnérabilité 2 : Stockage des Clés Privées en Mémoire

**Problème** : Les clés privées sont stockées en clair en RAM  
**Impact** : Vulnérable aux attaques par dump mémoire  
**Risque** : Exposition des clés privées critiques

**Mesures correctives** :
1. Utiliser un HSM (Hardware Security Module)
2. Chiffrer les clés privées au repos avec un KMS
3. Implémenter le memory locking (mlock)

```python
# Exemple avec chiffrement de clé
from Crypto.Protocol.KDF import PBKDF2

def encrypt_private_key(key, password):
    salt = get_random_bytes(32)
    derived_key = PBKDF2(password, salt, dkLen=32)
    cipher = AES.new(derived_key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(key.export_key())
    return {
        'ciphertext': ciphertext,
        'nonce': cipher.nonce,
        'tag': tag,
        'salt': salt
    }
```

#### ⚠️ Vulnérabilité 3 : Absence de Validation Stricte des Montants

**Problème** : Pas de limite maximale configurable par client  
**Impact** : Risque de transactions frauduleuses importantes  
**Risque** : Perte financière en cas de compromission

**Mesure corrective** :
```python
class Client:
    def __init__(self, nom, carte, ca, limite_journaliere=1000):
        # ...
        self.limite_journaliere = limite_journaliere
        self.transactions_jour = {}
    
    def verifier_limite(self, montant):
        aujourd_hui = date.today().isoformat()
        total_jour = self.transactions_jour.get(aujourd_hui, 0)
        
        if total_jour + montant > self.limite_journaliere:
            return False, "Limite journalière dépassée"
        
        return True, "OK"
```

#### ⚠️ Vulnérabilité 4 : Pas de Vérification CVC/CVV

**Problème** : Seul le numéro de carte est vérifié  
**Impact** : Sécurité réduite en cas de vol de numéro de carte  
**Risque** : Transactions non autorisées

**Mesure corrective** :
```python
pi = {
    "carte": self.carte,
    "cvc": self.cvc,  # Ajouter CVC
    "date_expiration": self.expiration,  # Ajouter date d'expiration
    "montant": montant,
    "nonce": nonce
}
```

#### ⚠️ Vulnérabilité 5 : Communication Non Chiffrée (HTTP)

**Problème** : L'interface web utilise HTTP au lieu de HTTPS  
**Impact** : Vulnérable aux attaques MITM sur le réseau  
**Risque** : Interception des communications client-serveur

**Mesure corrective** :
```python
# Générer un certificat SSL auto-signé
# openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Dans app.py
if __name__ == '__main__':
    socketio.run(
        app, 
        debug=False,  # Désactiver en production
        host='0.0.0.0', 
        port=5000,
        ssl_context=('cert.pem', 'key.pem')  # Activer HTTPS
    )
```

### Recommandations de Sécurité

#### Niveau Application

1. **Chiffrement de bout en bout**
   - Implémenter TLS 1.3 pour toutes les communications
   - Utiliser des certificats SSL/TLS valides (Let's Encrypt)

2. **Gestion des Secrets**
   - Ne jamais stocker de secrets dans le code
   - Utiliser des variables d'environnement
   - Implémenter un vault (HashiCorp Vault, AWS Secrets Manager)

3. **Logging et Audit**
   - Logger tous les événements de sécurité
   - Implémenter un SIEM pour la détection d'anomalies
   - Conserver les logs de manière sécurisée et immuable

4. **Rate Limiting**
   ```python
   from flask_limiter import Limiter
   
   limiter = Limiter(
       app,
       key_func=lambda: request.remote_addr,
       default_limits=["100 per hour"]
   )
   
   @app.route('/api/acheter', methods=['POST'])
   @limiter.limit("10 per minute")
   def api_acheter():
       # ...
   ```

5. **Input Validation**
   ```python
   from marshmallow import Schema, fields, validate
   
   class AchatSchema(Schema):
       client = fields.Str(required=True, validate=validate.Length(min=1, max=100))
       montant = fields.Float(required=True, validate=validate.Range(min=0.01, max=10000))
       items = fields.List(fields.Str(), required=True, validate=validate.Length(min=1))
   ```

#### Niveau Infrastructure

1. **Isolation des Environnements**
   - Séparer dev/staging/production
   - Utiliser des containers (Docker)
   - Déployer dans un environnement isolé (VPC)

2. **Backup et Disaster Recovery**
   - Sauvegardes régulières des certificats et clés
   - Plan de récupération en cas de compromission
   - Tests réguliers de restauration

3. **Monitoring et Alerting**
   - Surveiller les tentatives de rejeu
   - Alertes sur les échecs de validation de certificat
   - Monitoring des performances et anomalies

---

## 🧪 Tests et Validation

### Tests Implémentés

Le fichier `projet.py` inclut plusieurs tests automatisés :

#### Test 1 : Transaction Normale Valide
```python
alice.acheter(amazon, ["Livre Python", "Clé USB 64GB"], 45)
```
✅ **Résultat attendu** : Transaction approuvée, ARQC généré

#### Test 2 : Transaction Normale Valide (Autre Client)
```python
charlie.acheter(fnac, ["Ordinateur portable", "Souris gaming"], 850)
```
✅ **Résultat attendu** : Transaction approuvée

#### Test 3 : Fonds Insuffisants
```python
bob.acheter(amazon, ["iPhone 15 Pro"], 1200)
```
❌ **Résultat attendu** : Transaction refusée (solde insuffisant)

#### Test 4 : Attaque par Rejeu
```python
test_attaque_rejeu(alice, amazon)
```
❌ **Résultat attendu** : 
- Premier envoi : ✅ Succès
- Deuxième envoi (rejeu) : ❌ Refusé

#### Test 5 : Certificat Révoqué
```python
test_certificat_revoque(ca, banque)
```
❌ **Résultat attendu** : Transaction refusée (certificat invalide)

#### Test 6 : Manipulation de Montant
```python
test_manipulation_montant(alice, amazon)
```
❌ **Résultat attendu** : Signature invalide détectée

### Scénarios de Test Supplémentaires

#### Test de Charge
```python
import threading

def test_charge():
    threads = []
    for i in range(100):
        t = threading.Thread(
            target=lambda: alice.acheter(amazon, [f"Article {i}"], 10)
        )
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
```

#### Test de Timestamp Expiré
```python
def test_timestamp_expire():
    import time
    transaction_id = str(uuid.uuid4())
    timestamp = time.time() - 400  # 400 secondes dans le passé (> 300)
    
    # ... créer paquet avec timestamp expiré
    # Résultat attendu : Transaction expirée
```

---

## 🚀 Améliorations Possibles

### Court Terme

1. **Support OCSP (Online Certificate Status Protocol)**
   - Vérification en temps réel du statut des certificats
   - Alternative plus efficace aux CRL

2. **Authentification Multi-Facteurs (2FA)**
   - TOTP (Time-based One-Time Password)
   - SMS/Email de confirmation

3. **Internationalisation (i18n)**
   - Support multi-langues (FR, EN, ES, etc.)
   - Devises multiples

4. **Export des Données**
   - Génération de rapports PDF
   - Export CSV des transactions
   - Visualisations avancées (heatmaps, etc.)

### Moyen Terme

1. **Support de la Cryptographie à Courbes Elliptiques (ECC)**
   - Clés plus petites pour même niveau de sécurité
   - Performance améliorée

   ```python
   from Crypto.PublicKey import ECC
   
   key = ECC.generate(curve='P-256')
   ```

2. **3D Secure / Strong Customer Authentication (SCA)**
   - Conformité DSP2 européenne
   - Réduction de la fraude

3. **Smart Contracts / Blockchain**
   - Audit trail immuable
   - Transactions décentralisées

4. **API RESTful Complète**
   - Documentation OpenAPI/Swagger
   - Authentification OAuth 2.0
   - Rate limiting par API key

### Long Terme

1. **Architecture Microservices**
   - Séparation CA / Banque / Marchand en services indépendants
   - Scalabilité horizontale
   - Résilience améliorée

2. **Support des Paiements Tokenisés**
   - Génération de tokens à usage unique
   - Conformité PCI DSS

3. **Intelligence Artificielle**
   - Détection de fraude par machine learning
   - Analyse comportementale des utilisateurs

4. **Support Mobile**
   - Application iOS/Android native
   - Biométrie (Face ID, Touch ID)
   - Notifications push

---

## 📚 Références

- **SET Protocol Specification** : https://en.wikipedia.org/wiki/Secure_Electronic_Transaction
- **EMV Specifications** : https://www.emvco.com/
- **RFC 5280** : Internet X.509 Public Key Infrastructure Certificate
- **NIST Guidelines** : https://csrc.nist.gov/publications/
- **OWASP Top 10** : https://owasp.org/www-project-top-ten/

---

## 👥 Auteur

Projet réalisé dans le cadre du module de Cybersécurité  
**Technologies** : Python, Flask, PyCryptodome, Bootstrap 5, Chart.js

---

## 📄 Licence

Ce projet est à usage éducatif uniquement.

---

**✨ Merci d'avoir exploré cette simulation du protocole SET/CDA ! ✨**
