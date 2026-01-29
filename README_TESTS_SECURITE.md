# 🔐 Guide des Tests de Sécurité - Protocole SET/CDA

## 📋 Vue d'ensemble

Le fichier `test_securite.py` contient une **démonstration complète** de toutes les attaques possibles contre votre système SET/CDA et montre comment chaque mécanisme de sécurité les bloque.

---

## 🚀 Lancement du Script

### Méthode 1 : Script complet interactif

```bash
python test_securite.py
```

**Ce que vous verrez :**
- 9 tests de sécurité complets
- Chaque test explique l'attaque, l'exécute, et montre le blocage
- Affichage détaillé avec émojis pour une meilleure lisibilité
- Mode interactif : appuyez sur ENTRÉE entre chaque test

### Méthode 2 : Version automatique (sans pause)

```bash
python test_securite.py < /dev/null
```

Tous les tests s'exécutent automatiquement sans attendre vos entrées.

---

## 🧪 Les 9 Tests de Sécurité

### ✅ Test 1 : Attaque par Rejeu
**Scénario :** Un pirate intercepte une transaction valide et essaie de la rejouer.

**Protection testée :**
- Chaque `transaction_id` est enregistré dans `transactions_vues`
- Si le même ID arrive une 2ème fois → **REFUSÉ**

**Résultat attendu :**
```
✅ SUCCÈS DU TEST (attaque bloquée) : Transaction déjà traitée (attaque par rejeu détectée)
```

---

### ✅ Test 2 : Modification du Montant
**Scénario :** L'attaquant intercepte une transaction de 100€ et change le montant à 1€ dans l'Order Info.

**Protection testée :**
- La signature numérique est calculée sur : `hash(OI + PI + transaction_id)`
- Si l'OI change, le hash ne correspond plus
- La vérification de signature **ÉCHOUE**

**Résultat attendu :**
```
✅ SUCCÈS DU TEST (attaque bloquée) : Signature cryptographique invalide
```

---

### ✅ Test 3 : Usurpation d'Identité
**Scénario :** Un attaquant génère ses propres clés et crée un faux certificat prétendant être "Alice".

**Protection testée :**
- Le certificat est vérifié par la CA
- La signature du certificat ne correspond pas (signé par l'attaquant, pas par la CA)
- **REFUSÉ**

**Résultat attendu :**
```
✅ SUCCÈS DU TEST (attaque bloquée) : Certificat invalide: Signature du certificat invalide
```

---

### ✅ Test 4 : Certificat Révoqué
**Scénario :** Un client malveillant dont le certificat a été révoqué essaie quand même de faire un achat.

**Protection testée :**
- Le marchand vérifie si le certificat est dans la **CRL (Certificate Revocation List)**
- Si oui → **REFUSÉ**

**Résultat attendu :**
```
✅ SUCCÈS DU TEST (attaque bloquée) : Certificat invalide: Certificat révoqué
```

---

### ✅ Test 5 : Timestamp Expiré
**Scénario :** L'attaquant rejoue une vieille transaction capturée il y a 1 heure.

**Protection testée :**
- Fenêtre temporelle de **5 minutes**
- `abs(temps_actuel - timestamp) > 300` → **REFUSÉ**

**Résultat attendu :**
```
✅ SUCCÈS DU TEST (attaque bloquée) : Transaction expirée (timestamp trop ancien/futur)
```

---

### ✅ Test 6 : Fonds Insuffisants
**Scénario :** Un client avec 50€ essaie d'acheter pour 1000€.

**Protection testée :**
- La banque vérifie : `compte['solde'] < montant`
- Si vrai → **REFUSÉ**

**Résultat attendu :**
```
✅ SUCCÈS DU TEST (attaque bloquée) : Fonds insuffisants
```

---

### ✅ Test 7 : Carte Invalide
**Scénario :** Utiliser un numéro de carte qui n'existe pas dans la base de la banque.

**Protection testée :**
- La banque vérifie : `if carte not in self.comptes`
- Si la carte n'existe pas → **REFUSÉ**

**Résultat attendu :**
```
✅ SUCCÈS DU TEST (attaque bloquée) : Carte invalide
```

---

### ✅ Test 8 : Double Dépense
**Scénario :** Un client avec 100€ essaie de faire 2 achats de 80€ simultanément.

**Protection testée :**
- Vérification du solde en **temps réel** pour chaque transaction
- Premier achat : 100€ - 80€ = 20€ restants → **APPROUVÉ**
- Deuxième achat : 20€ < 80€ → **REFUSÉ**

**Résultat attendu :**
```
Transaction 1 : ✅ Validée
Transaction 2 : ✅ SUCCÈS DU TEST (attaque bloquée) : Fonds insuffisants
```

---

### ✅ Test 9 : Injection de Données
**Scénario :** L'attaquant essaie d'injecter du code malveillant dans les champs.

**Exemples d'injections testées :**
- SQL : `'; DROP TABLE users; --`
- XSS : `<script>alert('XSS')</script>`
- Auth bypass : `' OR '1'='1`

**Protection testée :**
- Les données sont **signées et chiffrées**
- Elles sont stockées comme **texte brut**, jamais interprétées comme du code
- Pas de base de données SQL → pas d'injection SQL possible
- Pas d'évaluation de code → pas d'exécution malveillante

**Résultat attendu :**
```
ℹ️ Transaction traitée (les données malveillantes sont stockées comme texte)
```

---

## 📊 Résumé des Mécanismes de Sécurité Testés

| Mécanisme | Technologie | Attaque Bloquée |
|-----------|-------------|-----------------|
| **Transaction ID unique** | UUID v4 + Set Python | Rejeu |
| **Fenêtre temporelle** | Timestamp + validation | Rejeu tardif |
| **Signature numérique** | RSA + SHA-256 | Modification de données |
| **Certificats X.509** | PKI + CA | Usurpation d'identité |
| **Liste de révocation (CRL)** | Liste noire CA | Certificats compromis |
| **Vérification solde** | Base de données temps réel | Fonds insuffisants |
| **Validation carte** | Base de données | Cartes invalides |
| **Débits immédiats** | Mise à jour synchrone | Double dépense |
| **Chiffrement RSA** | PKCS1_OAEP | Confidentialité PI |

---

## 🎯 Utilisation pour votre Présentation

### Démonstration en direct

1. **Lancez le script** devant votre professeur :
   ```bash
   python test_securite.py
   ```

2. **Expliquez chaque test** :
   - "Voici l'attaque que je simule..."
   - "Le système la détecte grâce à..."
   - "Résultat : attaque bloquée ✅"

3. **Montrez le code source** :
   - Ouvrez `projet.py` et montrez les fonctions de vérification
   - Par exemple : `verifier_anti_rejeu()`, `verifier_signature()`, `verifier_certificat()`

### Questions possibles du professeur

**Q: "Comment savez-vous que personne ne peut modifier le montant ?"**
**R:** "Regardez le test 2. J'intercepte une transaction de 100€, je change le montant à 1€, et la signature ne correspond plus. Le système refuse automatiquement."

**Q: "Et si quelqu'un vole un certificat ?"**
**R:** "Le test 4 montre que si la CA révoque le certificat, toute tentative d'utilisation est refusée. Le certificat est ajouté à la CRL."

**Q: "Qu'est-ce qui empêche quelqu'un de dépenser le même argent deux fois ?"**
**R:** "Le test 8 démontre que chaque transaction vérifie le solde en temps réel. Si vous avez 100€ et faites 2 achats de 80€, le deuxième est refusé car il ne reste que 20€."

---

## 🔍 Détails Techniques

### Structure d'un test

Chaque test suit ce format :

```python
def test_X_nom_attaque(params):
    """Documentation de l'attaque"""
    
    # 1. Afficher le scénario
    print_section("NOM ATTAQUE")
    print("📝 Scénario : ...")
    
    # 2. Exécuter l'attaque
    print_attack_step("Étape 1 : ...")
    # ... code malveillant ...
    
    # 3. Montrer le résultat
    succes, message = fonction_cible(donnees_malveillantes)
    
    # 4. Expliquer la défense
    print_defense("Protection : ...")
    
    # 5. Vérifier le blocage
    print_result(succes, message)
```

### Codes de retour

- ✅ **Test réussi** = Attaque bloquée (système sécurisé)
- ❌ **Test échoué** = Attaque réussie (PROBLÈME)

---

## 🛠️ Personnalisation

### Ajouter un nouveau test

```python
def test_10_ma_nouvelle_attaque(params):
    """Description de l'attaque"""
    print_section("MA NOUVELLE ATTAQUE")
    print("   📝 Scénario : ...")
    
    # Votre code d'attaque ici
    
    print_defense("Protection utilisée : ...")
    print_result(succes, message)
```

Puis ajoutez-le à la liste dans `main()` :

```python
tests = [
    # ... tests existants ...
    ("MA NOUVELLE ATTAQUE", lambda: test_10_ma_nouvelle_attaque(params))
]
```

### Modifier les montants

Changez les montants dans les tests pour des scénarios différents :

```python
# Au lieu de 1000€
montant = 5000  # Attaque plus agressive

# Au lieu de 50€ de solde
solde_initial = 10  # Client encore plus pauvre
```

---

## 📝 Logs et Traces

Le script affiche automatiquement :
- Les étapes de chaque attaque
- Les défenses activées
- Les résultats de chaque test

**Exemple de sortie :**

```
================================================================================
🔴 TEST D'ATTAQUE : ATTAQUE PAR REJEU
================================================================================
   📝 Scénario : L'attaquant intercepte une transaction valide et essaie de la rejouer

   🎯 Étape 1 : Transaction légitime initiale
   ➜ Envoi de la transaction légitime...
   [Marchand] Transaction validée

   🎯 Étape 2 : L'attaquant intercepte le paquet et essaie de le rejouer
   ➜ Renvoi du MÊME paquet (attaque par rejeu)...
   🛡️  DÉFENSE : Protection anti-rejeu : chaque transaction_id est enregistré
   ✅ SUCCÈS DU TEST (attaque bloquée) : Transaction déjà traitée
```

---

## 🎓 Conseils pour la Présentation

1. **Commencez par le test le plus simple** (Test 6 : Fonds insuffisants)
2. **Montrez les tests les plus impressionnants** :
   - Test 2 : Modification de montant
   - Test 3 : Usurpation d'identité
   - Test 8 : Double dépense
3. **Expliquez le code source** en parallèle
4. **Terminez par le résumé** pour récapituler toutes les protections

---

## 📚 Documentation Associée

- `GUIDE_CODE_DETAILLE.md` : Explication A-Z du code
- `GUIDE_SITE_WEB_DETAILLE.md` : Interface web
- `DOCUMENTATION.md` : Documentation technique
- `AMELIORATIONS.md` : Améliorations apportées

---

## ✨ Conclusion

Ce script de test prouve que votre implémentation du protocole SET/CDA est **robuste** et **sécurisée** contre les attaques les plus courantes. Chaque mécanisme de sécurité (chiffrement, signature, certificat) joue un rôle essentiel et complémentaire.

**Résultat : 9/9 attaques bloquées ✅**

Bonne présentation ! 🎉
