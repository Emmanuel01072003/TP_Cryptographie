# Guide des Détails Techniques des Attaques

## 🎯 Objectif

Cette interface montre **tous les détails techniques** de chaque attaque testée, permettant une compréhension approfondie des mécanismes de sécurité du protocole SET/CDA.

## 📋 Ce qui est Affiché

### 1. **Étapes de Vérification** 📝
Pour chaque attaque, vous verrez le processus complet étape par étape :
- ✅ Étapes réussies (en vert)
- ❌ Étapes échouées (en rouge)  
- ⚠️ Étapes d'avertissement (en orange)

**Exemple pour l'usurpation d'identité :**
```
Étape 1: Réception du paquet par le marchand ✅
Étape 2: Vérification de la signature du certificat par la CA ❌
Étape 3: Décision finale du marchand ❌ (REFUSÉ)
```

### 2. **Comparaison de Certificats** 🔐
Affichage côte à côte du **certificat légitime** vs **certificat forgé** :

| Certificat Légitime | Certificat Forgé |
|-------------------|-----------------|
| ✅ Sujet: Alice | ❌ Sujet: Alice (usurpé) |
| ✅ Émetteur: Autorité de Certification SET | ❌ Émetteur: Fausse CA |
| ✅ Clé Publique: xxx... | ❌ Clé Publique: yyy... (différente!) |
| ✅ Signature CA: Valide | ❌ Signature CA: INVALIDE |

**Incompatibilité détectée :** Les clés publiques sont différentes !

### 3. **Détails Cryptographiques** 🔑

#### Pour la Modification de Montant :
```
Transaction ID: abc123...
Hash Original (SHA-256):  a1b2c3d4... (montant 100€)
Hash Modifié (SHA-256):   x9y8z7w6... (montant 1€)
Comparaison: ❌ DIFFÉRENTS - Signature invalide
```

#### Pour l'Usurpation :
```
Transaction ID: def456...
Hash SHA-256: f5e4d3c2...
Données chiffrées: 256 octets (RSA 2048 bits)
Signature: 256 octets
```

### 4. **Paquet Reçu par le Marchand** 📦
Visualisation complète de ce que le marchand reçoit :

```json
{
  "order_info": {
    "items": ["Test Usurpation"],
    "montant": 100,
    "client": "Alice",
    "timestamp": 1705951234.56
  },
  "payment_info": "🔒 Chiffré RSA pour la banque (256 octets)",
  "certificat_emetteur": "Fausse CA",
  "certificat_sujet": "Alice"
}
```

## 🧪 Attaques avec Détails Complets

### ✅ Actuellement Enrichies :
1. **Usurpation d'Identité** - Comparaison certificats, étapes de vérification
2. **Modification de Montant** - Comparaison de hash SHA-256, ordre de modification

### 🔄 Prochainement :
3. Certificat Révoqué
4. Timestamp Expiré
5. Attaque par Rejeu
6. Fonds Insuffisants
7. Carte Invalide
8. Injection de Code

## 🚀 Comment Tester

1. **Accédez à** : http://localhost:5001/attaques
2. **Sélectionnez une attaque** (ex: Usurpation d'Identité)
3. **Remplissez les paramètres** :
   - Client cible : Alice
   - Marchand : Amazon
4. **Lancez l'attaque** 🔴
5. **Observez tous les détails** :
   - Les certificats comparés
   - Le processus de vérification
   - Les données cryptographiques
   - Le paquet intercepté

## 📊 Exemple Complet : Usurpation d'Identité

### Scénario :
Un attaquant génère ses propres clés RSA et crée un faux certificat prétendant être "Alice".

### Ce que vous verrez :

#### 1️⃣ Alertes
```
🛡️ SÉCURITÉ VALIDÉE
Le système a détecté et bloqué l'attaque
```

#### 2️⃣ Étapes de Vérification
```
1. Réception du paquet par le marchand ✅
   Transaction ID: abc123..., Montant: 100€

2. Vérification de la signature du certificat par la CA ❌
   Résultat: INVALIDE - Signature non vérifiable

3. Décision finale du marchand ❌
   Certificat invalide: Signature du certificat invalide
```

#### 3️⃣ Comparaison Certificats
```
Certificat Légitime              | Certificat Forgé
---------------------------------|----------------------------------
Sujet: Alice                     | Sujet: Alice
Émetteur: Autorité CA SET ✅     | Émetteur: Fausse CA ❌
Clé Publique: 12345...           | Clé Publique: 98765... (≠)
Signature CA: Valide ✅          | Signature CA: INVALIDE ❌

⚠️ Incompatibilité : Les clés sont différentes et le certificat 
n'est pas signé par la CA légitime !
```

#### 4️⃣ Détails Crypto
```
Transaction ID: abc123-def456-...
Hash SHA-256: a1b2c3d4e5f6...
Données chiffrées: 256 octets (RSA 2048)
Signature: 256 octets
```

#### 5️⃣ Paquet Reçu
```json
{
  "order_info": { "montant": 100, "client": "Alice" },
  "payment_info": "🔒 Chiffré (256 octets)",
  "certificat_emetteur": "Fausse CA"
}
```

#### 6️⃣ Mécanisme de Défense
```
🔒 Vérification de certificat : La CA détecte que la 
signature du certificat est invalide

💡 Le certificat auto-signé par l'attaquant ne peut pas 
être vérifié par la CA légitime
```

## 🎓 Apprentissage Pédagogique

### Ce que vous comprenez maintenant :

1. **La Cryptographie en Action**
   - Comment les hash SHA-256 changent quand les données changent
   - Pourquoi RSA 2048 bits est utilisé
   - La taille des signatures (256 octets)

2. **Les Certificats X.509**
   - Structure d'un certificat
   - Importance de la signature de la CA
   - Comment détecter un faux certificat

3. **Le Processus de Vérification**
   - Ordre des étapes de validation
   - Où exactement l'attaque échoue
   - Pourquoi la sécurité est multi-couches

4. **Le Chiffrement Bout en Bout**
   - Ce que le marchand voit (Order Info en clair)
   - Ce que le marchand NE voit PAS (Payment Info chiffré)
   - Protection de la vie privée bancaire

## 🔍 Points Clés

### ❌ Modification de Montant
- Le hash change si on modifie 100€ → 1€
- La signature devient invalide
- Le marchand détecte immédiatement

### ❌ Usurpation d'Identité  
- Impossible de forger la signature de la CA
- Les clés publiques ne correspondent pas
- Le certificat est rejeté avant tout traitement

### ❌ Certificat Révoqué
- La CRL (Certificate Revocation List) est consultée
- Même si le certificat était valide, il est maintenant bloqué

## 📚 Documentation Complète

- **Guide Interface Attaques** : `GUIDE_INTERFACE_ATTAQUES.md`
- **Tests Sécurité CLI** : `README_TESTS_SECURITE.md`
- **Documentation Générale** : `DOCUMENTATION.md`

## 🎯 Conclusion

Cette interface détaillée transforme les tests de sécurité en une **expérience pédagogique visuelle**. Vous ne testez pas seulement si l'attaque est bloquée, vous **voyez exactement pourquoi et comment** elle est bloquée, avec tous les détails cryptographiques.

Parfait pour :
- 🎓 Présenter votre projet
- 📖 Comprendre le protocole SET/CDA
- 🔒 Démontrer la robustesse de la sécurité
- 💡 Expliquer la cryptographie appliquée
