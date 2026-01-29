# 🔬 Moniteur de Processus Techniques - Mode Développeur

## 📋 Description

Le **Moniteur de Processus Techniques** est un onglet spécial qui affiche **EN TEMPS RÉEL** et **EN DÉTAIL COMPLET** tous les processus cryptographiques et les opérations internes du système SET/CDA.

**C'est comme avoir une fenêtre transparente sur le moteur cryptographique !** 🪟🔐

## 🎯 Accès

```
http://localhost:5001/processus
```

Ou cliquez sur **"Processus Technique"** dans la barre de navigation.

## ✨ Fonctionnalités

### 1. **Visualisation en Temps Réel** ⏱️
Chaque action effectuée dans le système génère un **processus détaillé** qui s'affiche instantanément dans le moniteur via WebSocket.

### 2. **Détails Complets**

Pour **chaque opération**, vous voyez :

#### 🔑 Clés Cryptographiques
```
Clé Publique Client (RSA 2048):
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----

Clé Publique Banque (RSA 2048):
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----
```

#### 🔒 Données Avant/Après Chiffrement
```
Données en clair (Payment Info):
{
  "carte": "4970-1111-2222-3333",
  "montant": 45,
  "nonce": "a1b2c3d4e5f6...",
  "transaction_id": "abc-123-def-456..."
}

Données chiffrées (hex):
3a4f8e2d1c9b7a6e5f4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b...
(256 octets - RSA 2048 bits)
```

#### ✍️ Signatures Numériques
```
Signature SHA-256 + RSA:
7f8e9d0c1b2a3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8c9b0a1f2e3d4c5b6a...
(256 octets)

Validation: ✅ VALIDE
```

#### 🔐 Hash SHA-256
```
Hash des données combinées (OI + PI + ID):
a1b2c3d4e5f6789...0f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6b7a8f9e0d1c2b3a...
```

#### 📜 Certificats X.509
```json
{
  "numero_serie": "abc123-def456-...",
  "sujet": "Alice",
  "emetteur": "Autorité de Certification SET",
  "date_expiration": "2027-01-22T12:00:00"
}
```

### 3. **Étapes du Processus** 📝

Chaque opération est décomposée en étapes numérotées :

```
Étape 1 ✅ Génération des identifiants de transaction
  Transaction ID: abc123-def456..., Nonce: x9y8z7w6v5u4...
  ⏱️ 2ms

Étape 2 ✅ Création de l'Order Info (OI) - Données visibles par le marchand
  Items: ['Livre Python', 'Clé USB'], Montant: 45€
  ⏱️ 3ms

Étape 3 ✅ Création du Payment Info (PI) - Données sensibles
  Carte: 4970-111******, Montant: 45€
  ⏱️ 1ms

Étape 4 ✅ Chiffrement RSA 2048 bits du Payment Info
  Données chiffrées: 256 octets. Seule la banque peut déchiffrer
  ⏱️ 8ms

Étape 5 ✅ Signature numérique SHA-256 + RSA
  Hash: a1b2c3d4e5f6..., Signature: 256 octets
  ⏱️ 5ms
```

## 🚀 Exemple d'Utilisation

### Scénario : Achat d'Alice chez Amazon

1. **Accédez** à l'onglet **Processus Technique**
2. **Ouvrez** un autre onglet avec l'interface **Client**
3. **Effectuez un achat** : Alice achète pour 45€ chez Amazon
4. **Retournez** au Moniteur de Processus

**Vous verrez apparaître en temps réel :**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 Achat de Alice chez Amazon - 45€
12:34:56

┌─ Étape 1 ✅ Génération des identifiants de transaction
│  Transaction ID: 3f4e5d6c-7b8a-..., Nonce: a1b2c3d4...
│  ⏱️ 2ms
│
├─ Étape 2 ✅ Création de l'Order Info (OI)
│  Items: ['Livre Python', 'Clé USB'], Montant: 45€
│  ⏱️ 3ms
│
├─ Étape 3 ✅ Création du Payment Info (PI)
│  Carte: 4970-111******, Montant: 45€
│  ⏱️ 1ms
│
├─ Étape 4 ✅ Chiffrement RSA 2048 bits
│  Données chiffrées: 256 octets
│  ⏱️ 8ms
│
└─ Étape 5 ✅ Signature SHA-256 + RSA
   Hash: a1b2c3d4e5f6789...
   ⏱️ 5ms

🔑 Clés Cryptographiques (cliquez pour afficher)
  └─ Clé Publique Client (RSA 2048)
  └─ Clé Publique Banque (RSA 2048)

🔒 Données Chiffrées/Déchiffrées (cliquez pour afficher)
  ├─ Données en clair:
  │  {"carte": "4970-1111-2222-3333", "montant": 45, ...}
  │
  └─ Données chiffrées (hex):
     3a4f8e2d1c9b7a6e5f4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b...

✍️ Signature Numérique (cliquez pour afficher)
  Signature SHA-256 + RSA:
  7f8e9d0c1b2a3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8c9b0a1f2e3d4c5b6a...
  Validation: ✅ VALIDE

🔐 Hash SHA-256:
  a1b2c3d4e5f6789...0f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6b7a8f9e0d1c2b3a...

📜 Certificat X.509 (cliquez pour afficher)
  {
    "numero_serie": "abc123-def456-...",
    "sujet": "Alice",
    "emetteur": "Autorité de Certification SET",
    "date_expiration": "2027-01-22T12:00:00"
  }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Résultat de la transaction
12:34:56

✅ Résultat: Commande validée (ARQC: f5e4d3c2b1a0...)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🎛️ Contrôles

### Bouton "Effacer" 🗑️
Efface tous les logs affichés pour recommencer à zéro.

### Bouton "Pause" ⏸️
Met en pause l'affichage des nouveaux processus (utile pour examiner un processus spécifique).

### Filtres d'Affichage 🔍
Activez/désactivez l'affichage de :
- 🔑 Clés Cryptographiques
- 🔒 Chiffrement/Déchiffrement
- ✍️ Signatures Numériques
- 📜 Certificats

## 📊 Opérations Monitorées

Le moniteur affiche les détails pour **TOUTES** les opérations suivantes :

### 1. **Transactions (Achats)** 💳
- Génération des identifiants
- Création OI et PI
- Chiffrement RSA du PI
- Signature numérique
- Envoi au marchand
- Vérification par la banque
- Résultat final

### 2. **Création de Clients** 👤 _(à venir)_
- Génération des clés RSA (privée + publique)
- Demande de certificat à la CA
- Signature du certificat par la CA
- Enregistrement

### 3. **Tests d'Attaques** 🔴 _(à venir)_
- Tentative de modification de données
- Vérification de signature
- Détection de l'incohérence
- Rejet de la transaction

### 4. **Révocation de Certificats** ⛔ _(à venir)_
- Ajout à la CRL
- Mise à jour de la liste

## 🎓 Valeur Pédagogique

### Pour une Présentation Technique

Ce moniteur est **parfait** pour :

1. **Démontrer le Chiffrement RSA** 🔒
   - Montrez les données en clair
   - Montrez les données chiffrées (incompréhensibles)
   - Expliquez que seule la banque peut les déchiffrer

2. **Expliquer les Signatures Numériques** ✍️
   - Montrez le hash SHA-256
   - Montrez la signature (hash chiffré avec clé privée)
   - Expliquez comment on vérifie avec la clé publique

3. **Illustrer les Certificats X.509** 📜
   - Montrez la structure du certificat
   - Expliquez le rôle de la CA
   - Montrez la signature de la CA

4. **Timing des Opérations** ⏱️
   - Montrez que le chiffrement RSA prend ~8ms
   - Montrez que la signature prend ~5ms
   - Total : transaction complète en ~20ms

## 🔒 Sécurité et Confidentialité

⚠️ **IMPORTANT** : Ce moniteur affiche des **données sensibles** :
- Clés privées complètes
- Numéros de carte en clair
- Données bancaires non chiffrées

**Ce mode est destiné uniquement à :**
- Démonstrations pédagogiques
- Environnements de développement
- Présentations techniques

**NE JAMAIS activer en production !**

## 💡 Cas d'Usage

### 1. Présentation à un Professeur
Montrez en temps réel comment chaque opération cryptographique se déroule.

### 2. Debugging
Identifiez où une erreur se produit dans le processus.

### 3. Apprentissage
Comprenez visuellement comment fonctionne le protocole SET/CDA.

### 4. Comparaison
Comparez une transaction légitime vs une attaque (données différentes).

## 🎨 Interface

### Design
- **Thème sombre** : Fond noir avec texte vert (style terminal)
- **Code formaté** : Police monospace pour le code
- **Sections pliables** : Cliquez pour afficher/masquer les détails
- **Couleurs** :
  - 🟢 Vert : Données en clair
  - 🔴 Rouge : Données chiffrées
  - 🟣 Violet : Clés RSA
  - 🟡 Jaune : Hash SHA-256

### Ergonomie
- **Scroll infini** : Les nouveaux processus s'ajoutent en haut
- **Limite de 50 entrées** : Pour les performances
- **Sections pliables** : Économise l'espace à l'écran

## 🔧 Technique

### WebSocket
Le moniteur utilise **Socket.IO** pour recevoir les processus en temps réel :

```javascript
socket.on('technical_process', function(data) {
    displayProcess(data);
});
```

### Format des Données
```javascript
{
  timestamp: "2026-01-22T12:34:56",
  title: "💳 Achat de Alice chez Amazon - 45€",
  type: "transaction",
  status: "success",
  steps: [...],
  crypto: {
    keys: {...},
    plaintext: "...",
    encrypted: "...",
    hash: "...",
    signature: "...",
    certificate: {...}
  },
  result: {
    success: true,
    message: "..."
  }
}
```

## 🚀 Prochaines Fonctionnalités

- [ ] Export des logs en JSON
- [ ] Recherche dans les logs
- [ ] Comparaison de deux processus côte à côte
- [ ] Graphique de timing
- [ ] Mode "replay" pour rejouer un processus
- [ ] Capture d'écran des processus

## 📚 Documentation Complémentaire

- **Guide Principal** : `DOCUMENTATION.md`
- **Tests de Sécurité** : `README_TESTS_SECURITE.md`
- **Interface Attaques** : `GUIDE_INTERFACE_ATTAQUES.md`
- **Détails Attaques** : `GUIDE_DETAILS_ATTAQUES.md`

---

**Développé avec ❤️ pour la transparence cryptographique totale** 🔐✨
