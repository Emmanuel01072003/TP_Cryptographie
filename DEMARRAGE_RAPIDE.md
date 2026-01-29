# 🚀 Guide de Démarrage Rapide - Moniteur Technique

## ⚡ Démarrage en 3 Étapes

### 1️⃣ Lancer le Serveur
```bash
cd /Users/koblanemmanuel/Documents/TP_Cyber
python start.py
```

### 2️⃣ Ouvrir Deux Onglets

**Onglet 1 - Moniteur Technique :**
```
http://localhost:5001/processus
```

**Onglet 2 - Interface Client :**
```
http://localhost:5001/client
```

### 3️⃣ Faire un Test

Dans l'onglet **Client** :
- Client : **Alice**
- Marchand : **Amazon**
- Articles : `Livre Python, Clé USB`
- Montant : **45**
- Cliquez sur **"Acheter"**

Dans l'onglet **Moniteur** :
- **Regardez apparaître** tous les détails techniques en temps réel ! 🎉

## 🔥 Ce que Vous Verrez

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 Achat de Alice chez Amazon - 45€
12:34:56

Étape 1 ✅ Génération des identifiants de transaction
  Transaction ID: 3f4e5d6c-7b8a-..., Nonce: a1b2c3d4...
  ⏱️ 2ms

Étape 2 ✅ Création de l'Order Info (OI)
  Items: ['Livre Python', 'Clé USB'], Montant: 45€
  ⏱️ 3ms

Étape 3 ✅ Création du Payment Info (PI)
  Carte: 4970-111******, Montant: 45€
  ⏱️ 1ms

Étape 4 ✅ Chiffrement RSA 2048 bits du Payment Info
  Données chiffrées: 256 octets. Seule la banque peut déchiffrer
  ⏱️ 8ms

Étape 5 ✅ Signature numérique SHA-256 + RSA
  Hash: a1b2c3d4e5f6..., Signature: 256 octets
  ⏱️ 5ms

🔑 Clés Cryptographiques (cliquez pour afficher)
🔒 Données Chiffrées/Déchiffrées (cliquez pour afficher)
✍️ Signature Numérique (cliquez pour afficher)
🔐 Hash SHA-256
📜 Certificat X.509 (cliquez pour afficher)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Résultat de la transaction
12:34:56

✅ Résultat: Commande validée (ARQC: f5e4d3c2b1a0...)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🎯 Tests Recommandés

### Test 1 : Transaction Normale
1. Client : Alice → Amazon, 45€
2. **Observez** : Toutes les étapes en vert ✅
3. **Cliquez** sur les sections pliables pour voir les détails

### Test 2 : Attaque par Usurpation
1. Allez sur `/attaques`
2. Sélectionnez **"Usurpation d'Identité"**
3. Client cible : Alice, Marchand : Amazon
4. **Lancez l'attaque** 🔴
5. **Retournez** au moniteur
6. **Voyez** : Le faux certificat et sa détection

### Test 3 : Modification de Montant
1. Allez sur `/attaques`
2. Sélectionnez **"Modification de Montant"**
3. Montant original : 100€, Modifié : 1€
4. **Lancez l'attaque** 🔴
5. **Retournez** au moniteur
6. **Voyez** : Les deux hash différents et le rejet

## 💡 Astuces

### Voir les Clés Complètes
Cliquez sur **"🔑 Clés Cryptographiques"** pour déplier :
```
Clé Publique Client (RSA 2048):
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA7xGT...
-----END PUBLIC KEY-----
```

### Voir le Chiffrement
Cliquez sur **"🔒 Données Chiffrées/Déchiffrées"** :
```
Données en clair:
{"carte": "4970-1111-2222-3333", "montant": 45, ...}

Données chiffrées (hex):
3a4f8e2d1c9b7a6e5f4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b...
(256 octets)
```

### Voir la Signature
Cliquez sur **"✍️ Signature Numérique"** :
```
Signature SHA-256 + RSA:
7f8e9d0c1b2a3f4e5d6c7b8a9f0e1d2c3b4a5f6e7d8c9b0a1f2e3d4c5b6a...
(256 octets)

Validation: ✅ VALIDE
```

## 🎓 Pour une Présentation

### Configuration Écran
```
┌─────────────────────────┬─────────────────────────┐
│  Interface Client       │  Moniteur Technique     │
│  (localhost:5001/client)│  (localhost:5001/       │
│                         │   processus)            │
│                         │                         │
│  [Faire un achat ici]   │  [Détails s'affichent   │
│                         │   automatiquement]      │
└─────────────────────────┴─────────────────────────┘
```

### Scénario de Démonstration

**1. Introduction (2 min)**
- "Je vais vous montrer ce qui se passe EXACTEMENT quand Alice achète un livre"

**2. Action (1 min)**
- Effectuer l'achat dans l'onglet Client

**3. Explication (5 min)**
- Montrer chaque étape dans le moniteur
- Expliquer le chiffrement RSA
- Montrer la signature numérique
- Expliquer le certificat X.509

**4. Attaque (3 min)**
- Tester une usurpation d'identité
- Montrer comment c'est détecté

**Total : 11 minutes de démo impressionnante** 🎉

## 🛠️ Contrôles du Moniteur

### Bouton "Effacer" 🗑️
Efface tous les logs affichés.

### Bouton "Pause" ⏸️
Met en pause l'affichage (utile pour expliquer un processus).

### Filtres 🔍
Désactivez certains types de détails si trop d'informations.

## 📚 Documentation Complète

Pour plus de détails, consultez :
- **`README_MONITEUR_TECHNIQUE.md`** - Guide complet
- **`RESEME_COMPLET.md`** - Résumé de tout le projet
- **`GUIDE_DETAILS_ATTAQUES.md`** - Détails des attaques

## 🚨 Résolution de Problèmes

### Le moniteur ne s'affiche pas ?
1. Vérifiez que le serveur est lancé
2. Rafraîchissez la page (F5)
3. Vérifiez la console du navigateur (F12)

### Rien ne s'affiche dans le moniteur ?
1. Effectuez une action (achat, attaque, etc.)
2. Vérifiez que le WebSocket est connecté (toast "Moniteur technique connecté")
3. Cliquez sur "Reprendre" si le moniteur est en pause

### Les sections ne se déplient pas ?
Assurez-vous que JavaScript est activé et que Bootstrap est chargé.

## 🎉 C'est Tout !

Vous êtes prêt à **démontrer la puissance du chiffrement** ! 🔐✨

**Bon test !** 🚀
