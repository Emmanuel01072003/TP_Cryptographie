# 🎯 Interface de Tests de Sécurité - Guide d'Utilisation

## 🚀 Accès Rapide

Une fois votre serveur lancé :

```bash
python start.py
```

**Accédez à l'interface de tests** :
- URL directe : http://localhost:5001/attaques
- Ou depuis la page d'accueil : cliquez sur "Tests Sécurité" (bouton rouge)
- Ou depuis le menu de navigation : "Tests Sécurité"

---

## 🎨 Interface Interactive

### Vue d'Ensemble

L'interface est divisée en 3 zones :

1. **Zone de Sélection** (Gauche) : 8 cartes d'attaques différentes
2. **Zone de Description** (Droite en haut) : Explication de l'attaque sélectionnée
3. **Zone de Résultat** (Droite en bas) : Résultat du test après exécution

---

## 📋 Les 8 Types d'Attaques Disponibles

### 1. 🔄 Attaque par Rejeu
**Niveau : Moyen** | **Badge : Rouge**

#### Ce que vous pouvez tester :
- Sélectionnez un client (Alice, Bob, Charlie)
- Sélectionnez un marchand (Amazon, FNAC, Darty)
- Cliquez sur "Lancer l'Attaque"

#### Ce qui se passe :
1. Une transaction légitime de 10€ est créée et envoyée
2. Le système capture le paquet
3. Le même paquet est renvoyé immédiatement (rejeu)

#### Résultat attendu :
- ✅ **Premier envoi** : Accepté
- ❌ **Deuxième envoi** : REFUSÉ (transaction_id déjà vu)
- **Défense** : Protection anti-rejeu activée

---

### 2. 💰 Modification de Montant
**Niveau : Élevé** | **Badge : Orange**

#### Paramètres modifiables :
- Client
- Marchand
- **Montant Original** (défaut : 100€)
- **Montant Modifié** (défaut : 1€)

#### Ce que vous pouvez tester :
Changez le montant original à 500€ et le montant modifié à 5€ pour voir une différence plus impressionnante.

#### Ce qui se passe :
1. Le client signe une transaction de 500€
2. L'attaquant modifie le montant à 5€
3. Le paquet modifié est envoyé au marchand

#### Résultat attendu :
- ❌ **Transaction REFUSÉE**
- **Raison** : Signature cryptographique invalide
- **Défense** : La signature couvre hash(OI + PI + ID), toute modification est détectée

---

### 3. 🎭 Usurpation d'Identité
**Niveau : Critique** | **Badge : Rouge**

#### Paramètres :
- **Client à Usurper** : Choisissez qui l'attaquant veut se faire passer pour
- **Marchand** : Où l'attaque est tentée

#### Ce qui se passe :
1. L'attaquant génère sa propre paire de clés RSA 2048 bits
2. Il crée un faux certificat prétendant être "Alice"
3. Il signe le certificat avec sa propre clé (auto-signé)
4. Il tente un achat

#### Résultat attendu :
- ❌ **Transaction REFUSÉE**
- **Raison** : Certificat invalide (signature CA non valide)
- **Défense** : Seuls les certificats signés par la CA légitime sont acceptés

---

### 4. 📜 Certificat Révoqué
**Niveau : Élevé** | **Badge : Orange**

#### Paramètres :
- Marchand uniquement (un client "Attaquant" est créé automatiquement)

#### Ce qui se passe :
1. Un nouveau client "Attaquant" est créé
2. Son certificat est immédiatement révoqué par la CA
3. Il essaie quand même d'acheter pour 50€

#### Résultat attendu :
- ❌ **Transaction REFUSÉE**
- **Raison** : Certificat révoqué (dans la CRL)
- **Défense** : Vérification de la liste de révocation avant chaque transaction

---

### 5. ⏰ Timestamp Expiré
**Niveau : Faible** | **Badge : Bleu**

#### Paramètres modifiables :
- Client
- Marchand
- **Âge de la Transaction** (défaut : 60 minutes)

#### Test recommandé :
- Testez avec 60 minutes (résultat : refusé)
- Testez avec 3 minutes (résultat : accepté)
- Testez avec 10 minutes (résultat : refusé)

#### Ce qui se passe :
Une transaction datant de X minutes est créée et envoyée.

#### Résultat attendu :
- ❌ **REFUSÉ si > 5 minutes**
- ✅ **ACCEPTÉ si < 5 minutes**
- **Défense** : Fenêtre temporelle de validation (5 minutes)

---

### 6. 💸 Fonds Insuffisants
**Niveau : Faible** | **Badge : Bleu**

#### Paramètres modifiables :
- Marchand
- **Solde Disponible** (défaut : 50€)
- **Montant à Acheter** (défaut : 1000€)

#### Test recommandé :
- Testez avec solde 10€ et montant 500€
- Testez avec solde 100€ et montant 99€ (devrait passer)
- Testez avec solde 100€ et montant 101€ (devrait échouer)

#### Résultat attendu :
- ❌ **REFUSÉ si solde < montant**
- ✅ **ACCEPTÉ si solde ≥ montant**
- **Défense** : Vérification du solde en temps réel par la banque

---

### 7. 💳 Carte Invalide
**Niveau : Faible** | **Badge : Gris**

#### Paramètres :
- Marchand uniquement (une carte invalide est générée automatiquement)

#### Ce qui se passe :
1. Un client avec la carte `4970-9999-9999-9999` est créé
2. **Mais aucun compte bancaire n'est créé** (carte non enregistrée)
3. Tentative d'achat de 100€

#### Résultat attendu :
- ❌ **Transaction REFUSÉE**
- **Raison** : Carte invalide (non trouvée dans la base)
- **Défense** : Vérification de l'existence de la carte dans le système bancaire

---

### 8. 💉 Injection de Code
**Niveau : Critique** | **Badge : Rouge**

#### Paramètres :
- Client
- Marchand

#### Ce qui est injecté automatiquement :
```javascript
Articles : 
  - "'; DROP TABLE users; --"  (SQL Injection)
  - "<script>alert('XSS')</script>"  (XSS)

Client :
  - "Alice' OR '1'='1"  (SQL Auth Bypass)
```

#### Ce qui se passe :
Le système essaie d'injecter du code malveillant dans les champs de transaction.

#### Résultat attendu :
- ⚠️ **Transaction traitée normalement** (pas d'injection réussie)
- **Pourquoi ?** : Les données sont traitées comme **texte brut**, jamais comme du code
- **Défense** : Pas de base de données SQL → pas d'injection SQL possible
- **Note** : Les données malveillantes sont stockées comme texte, sans être exécutées

---

## 🎮 Scénarios de Démonstration Recommandés

### Scénario 1 : Démonstration Rapide (5 minutes)
Testez dans cet ordre pour impressionner :

1. **Modification de Montant** (100€ → 1€) → Montre la puissance des signatures
2. **Attaque par Rejeu** → Montre la protection anti-rejeu
3. **Usurpation d'Identité** → Montre l'utilité des certificats CA

### Scénario 2 : Présentation Complète (15 minutes)
Testez toutes les attaques dans l'ordre de criticité :

1. Usurpation d'Identité ⚠️ Critique
2. Injection de Code ⚠️ Critique
3. Modification de Montant ⚠️ Élevé
4. Certificat Révoqué ⚠️ Élevé
5. Attaque par Rejeu ⚠️ Moyen
6. Timestamp Expiré ℹ️ Faible
7. Fonds Insuffisants ℹ️ Faible
8. Carte Invalide ℹ️ Faible

### Scénario 3 : Démonstration Personnalisée
Créez votre propre scénario :

1. **Modification de Montant** avec des valeurs extrêmes :
   - Montant Original : 10 000€
   - Montant Modifié : 0.01€

2. **Timestamp Expiré** avec différentes valeurs :
   - 3 minutes (accepté)
   - 6 minutes (refusé)
   - 60 minutes (refusé)

3. **Fonds Insuffisants** :
   - Solde : 1000€
   - Montant : 999€ (accepté)
   - Montant : 1001€ (refusé)

---

## 📊 Interprétation des Résultats

### Badge Vert (Attaque Bloquée ✅)
```
✅ SÉCURITÉ VALIDÉE
Le système a détecté et bloqué l'attaque
```

**Cela signifie** :
- Le mécanisme de défense fonctionne correctement
- La transaction malveillante a été refusée
- Le système est sécurisé contre ce type d'attaque

### Badge Orange (Attaque Non Bloquée ⚠️)
```
⚠️ ATTENTION
L'attaque n'a pas été bloquée (normal pour certains cas)
```

**Cela signifie** :
- Généralement pour l'injection de code
- Les données sont acceptées mais traitées comme du texte
- Aucun code malveillant n'est exécuté

---

## 🔍 Détails Affichés pour Chaque Test

### Informations Générales
- **Résultat** : Succès ou échec de la transaction
- **Message** : Raison du refus ou de l'acceptation
- **Mécanisme de Défense** : Quelle protection a été activée
- **Explication** : Détails techniques du blocage

### Informations Spécifiques par Type

#### Attaque par Rejeu
- Premier envoi : statut + message
- Deuxième envoi : statut + message

#### Modification de Montant
- Montant original
- Montant modifié
- Différence visible

#### Timestamp Expiré
- Âge de la transaction (minutes)
- Limite autorisée (5 minutes)

#### Fonds Insuffisants
- Solde disponible
- Montant demandé
- Différence

#### Certificat Révoqué
- Numéro du certificat révoqué

#### Usurpation d'Identité
- Client cible de l'usurpation

#### Carte Invalide
- Numéro de carte utilisé

#### Injection de Code
- Liste des données malveillantes injectées
- Code malveillant en format JSON

---

## 💡 Conseils d'Utilisation

### Pour une Présentation

1. **Commencez par expliquer** :
   - Qu'est-ce qu'une attaque ?
   - Pourquoi c'est important de la bloquer ?

2. **Montrez l'interface** :
   - Design moderne et intuitif
   - Cartes colorées par niveau de criticité

3. **Testez en direct** :
   - Sélectionnez une attaque
   - Modifiez les paramètres si disponibles
   - Lancez le test
   - Commentez le résultat affiché

4. **Expliquez la défense** :
   - Lisez la section "Mécanisme de Défense"
   - Montrez comment le système détecte l'attaque

### Pour Comprendre le Code

Après chaque test, vous pouvez :

1. Ouvrir `app.py` et chercher la fonction correspondante :
   - `test_attaque_rejeu()`
   - `test_attaque_modification_montant()`
   - etc.

2. Ouvrir `projet.py` et voir les méthodes de vérification :
   - `verifier_anti_rejeu()`
   - `verifier_signature()`
   - `verifier_certificat()`

3. Comprendre le flux complet de la transaction

---

## 🎯 Cas d'Usage

### Étudiant / Présentation
- Démontrez votre compréhension du protocole SET/CDA
- Montrez les failles de sécurité classiques
- Prouvez que votre implémentation est robuste

### Enseignant / Formation
- Utilisez l'interface pour enseigner la sécurité
- Montrez visuellement les attaques et défenses
- Comparez avec d'autres protocoles

### Développeur / Audit
- Testez manuellement les cas limites
- Vérifiez que toutes les défenses fonctionnent
- Identifiez des améliorations potentielles

---

## 🚨 Problèmes Courants

### "Client ou marchand invalide"
**Cause** : Vous avez essayé un test avec un nom inexistant
**Solution** : Utilisez uniquement les clients/marchands du menu déroulant

### "Erreur 500"
**Cause** : Problème serveur
**Solution** : Vérifiez que Flask est bien démarré et rechargez la page

### Résultat inattendu
**Cause** : Paramètres incorrects
**Solution** : Vérifiez les valeurs saisies (nombres positifs, timestamps valides)

---

## 📚 Ressources Complémentaires

- **Code source** : `app.py` (routes API des tests)
- **Template** : `templates/attaques.html` (interface utilisateur)
- **Logique métier** : `projet.py` (classes et méthodes)
- **Script CLI** : `test_securite.py` (version automatique)
- **Documentation** : `README_TESTS_SECURITE.md` (script automatique)

---

## ✨ Fonctionnalités Avancées

### Personnalisation des Paramètres

Certaines attaques permettent de personnaliser les paramètres :

- **Modification de Montant** : Testez avec différents montants
- **Timestamp Expiré** : Ajustez l'âge de la transaction
- **Fonds Insuffisants** : Changez le solde et le montant

### Enchaînement de Tests

Vous pouvez tester plusieurs attaques de suite :
1. Sélectionnez une attaque
2. Testez-la
3. Cliquez sur "Annuler"
4. Sélectionnez une autre attaque

### Comparaison Avant/Après

Pour les tests avec 2 envois (Rejeu) :
- Le premier envoi est toujours accepté
- Le deuxième est bloqué
- Comparez les deux résultats affichés

---

## 🎓 Explications pour votre Professeur

Quand vous présentez à votre professeur :

1. **Montrez l'interface** d'abord (design professionnel)
2. **Expliquez chaque carte** d'attaque (niveau de criticité)
3. **Sélectionnez "Modification de Montant"** :
   - "Voici une attaque où je change le montant après signature"
   - "Je signe une transaction de 100€, puis je la modifie à 1€"
   - "Regardez ce qui se passe..."
4. **Lancez le test**
5. **Commentez le résultat** :
   - "Le système refuse : Signature cryptographique invalide"
   - "Pourquoi ? Car la signature couvre hash(OI + PI + ID)"
   - "Toute modification du montant change le hash"
   - "La signature ne correspond plus → REFUSÉ"
6. **Montrez le code** correspondant dans `projet.py`

---

Profitez de cette interface interactive pour comprendre et démontrer la sécurité du protocole SET/CDA ! 🚀
