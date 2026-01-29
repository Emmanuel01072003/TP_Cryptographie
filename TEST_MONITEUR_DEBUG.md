# 🔍 TEST ET DEBUG DU MONITEUR - Guide Complet

## ✅ Améliorations Apportées

### 1. Correction du Bug d'Affichage
**Problème identifié** : La ligne qui supprimait le message "En attente" effaçait **TOUT** le contenu si un élément `.text-center` était trouvé, même dans les entrées déjà affichées.

**Solution** : Vérification plus robuste qui ne supprime que le message initial quand il n'y a qu'un seul enfant dans le div.

### 2. Logs de Debug Détaillés

#### Côté Client (Console JavaScript - F12)
Vous verrez maintenant :
```
📨 Processus technique reçu: {title: "...", ...}
✅ Affichage du processus
🎨 Début affichage processus: ...
📊 Données du processus: {timestamp: "...", title: "...", ...}
📦 État du logDiv AVANT: {children: 0, innerHTML_length: 123, hasTextCenter: true}
🗑️ Suppression du message initial "En attente"
🆕 Création de l'entrée: process-1
📝 HTML généré, taille: 1234 caractères
📌 Insertion de l'entrée dans le DOM...
✅ Entrée insérée AVANT le premier enfant
📦 État du logDiv APRÈS insertion: {children: 1, firstChild_id: "process-1"}
✅ displayProcess terminé. Total entrées: 1
```

#### Côté Serveur (Terminal)
Vous verrez maintenant :
```
============================================================
[MONITOR] Préparation processus technique
  Titre: 💳 Achat de Alice chez Amazon - 45€
  Type: transaction
  Status: info
  Nombre d'étapes: 5
  Crypto présent: Oui
  Résultat présent: Non
[MONITOR] 📡 Émission WebSocket 'technical_process'...
[MONITOR] ✅ Événement émis avec succès
============================================================
```

---

## 🚀 Procédure de Test - Étape par Étape

### Étape 1 : Démarrage du Serveur

```bash
cd /Users/koblanemmanuel/Documents/TP_Cyber
python start.py
```

**Vérifications** :
- ✅ Vous voyez "✅ Système initialisé avec succès !"
- ✅ Vous voyez "🌐 INTERFACE WEB DISPONIBLE"
- ✅ Aucune erreur n'apparaît

---

### Étape 2 : Ouvrir le Moniteur

1. Ouvrez votre navigateur
2. Allez sur : `http://localhost:5001/processus`
3. **IMPORTANT** : Appuyez sur **F12** pour ouvrir la console JavaScript
4. Allez dans l'onglet **Console**

**Vérifications** :
- ✅ La page se charge sans erreur
- ✅ Vous voyez "Moniteur technique initialisé" dans la console
- ✅ Vous voyez "Connecté au moniteur technique" dans la console
- ✅ Un toast vert "Moniteur technique connecté" apparaît en haut à droite

---

### Étape 3 : Ouvrir l'Interface Client (Nouvel Onglet)

1. **Sans fermer le moniteur**, ouvrez un **NOUVEL ONGLET**
2. Allez sur : `http://localhost:5001/client`

**Astuce** : Arrangez vos fenêtres pour voir :
- À gauche : `/client` 
- À droite : `/processus` avec la console F12 ouverte

---

### Étape 4 : Effectuer un Achat Test

Sur la page `/client` :
1. Client : **Alice**
2. Marchand : **Amazon**  
3. Articles : `Livre Python`
4. Montant : **45**
5. Cliquez sur **"Acheter"**

---

### Étape 5 : Vérifier les Logs

#### A. Dans le TERMINAL (serveur)

Vous **DEVEZ** voir :
```
============================================================
[MONITOR] Préparation processus technique
  Titre: 💳 Achat de Alice chez Amazon - 45€
  Type: transaction
  Status: info
  Nombre d'étapes: 5
  Crypto présent: Oui
  Résultat présent: Non
[MONITOR] 📡 Émission WebSocket 'technical_process'...
[MONITOR] ✅ Événement émis avec succès
============================================================

[ACHAT DÉTAILLÉ] Début pour Alice chez Amazon - 45€

============================================================
[MONITOR] Préparation processus technique
  Titre: 📊 Résultat de la transaction
  ...
```

**Si vous ne voyez PAS ces logs** → Le problème est dans `acheter_avec_details()` ou `log_technical_process()`

#### B. Dans la CONSOLE JavaScript (F12 sur /processus)

Vous **DEVEZ** voir :
```
📨 Processus technique reçu: {timestamp: "...", title: "💳 Achat de Alice...", ...}
✅ Affichage du processus
🎨 Début affichage processus: 💳 Achat de Alice chez Amazon - 45€
📊 Données du processus: {...}
📦 État du logDiv AVANT: {children: 1, innerHTML_length: 234, hasTextCenter: true}
🗑️ Suppression du message initial "En attente"
🆕 Création de l'entrée: process-1
📝 HTML généré, taille: 3456 caractères
📌 Insertion de l'entrée dans le DOM...
✅ Entrée insérée AVANT le premier enfant
📦 État du logDiv APRÈS insertion: {children: 1, firstChild_id: "process-1"}
✅ displayProcess terminé. Total entrées: 1
```

**Si vous ne voyez PAS ces logs** → Le problème est dans la connexion WebSocket

#### C. Sur la PAGE /processus

Vous **DEVEZ** voir une grande carte avec :
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 Achat de Alice chez Amazon - 45€
14:30:25

Étape 1 ✅ Génération des identifiants de transaction
  Transaction ID: abc123..., Nonce: x9y8z7...
  ⏱️ 2ms

Étape 2 ✅ Création de l'Order Info (OI)
  ...

🔑 Clés Cryptographiques (cliquez pour afficher)
🔒 Données Chiffrées/Déchiffrées (cliquez pour afficher)
...
```

**Si vous ne voyez RIEN** → Vérifiez les logs de la console JavaScript

---

## 🐛 Diagnostic des Problèmes

### Problème 1 : Rien dans le Terminal

**Symptôme** : Pas de logs `[MONITOR]` dans le terminal

**Causes possibles** :
- La fonction `acheter_avec_details()` n'est pas appelée
- La fonction `log_technical_process()` n'est pas appelée
- L'achat a échoué avant d'arriver à ces fonctions

**Solution** :
```bash
# Vérifier que app.py appelle bien acheter_avec_details
grep -n "acheter_avec_details" app.py
```

---

### Problème 2 : Logs dans le Terminal mais Rien dans la Console

**Symptôme** : Les logs `[MONITOR]` apparaissent dans le terminal, mais pas de `📨` dans la console JavaScript

**Causes possibles** :
- WebSocket non connecté
- Page `/processus` pas rafraîchie
- Erreur JavaScript (vérifiez l'onglet Console pour les erreurs rouges)

**Solutions** :
1. Rafraîchissez `/processus` avec **Ctrl+Shift+R** (force le rechargement)
2. Vérifiez qu'il n'y a pas d'erreurs rouges dans la console
3. Vérifiez que vous voyez "Connecté au moniteur technique"

---

### Problème 3 : Logs dans la Console mais Rien sur la Page

**Symptôme** : Vous voyez tous les logs dans la console, mais la page reste vide

**Causes possibles** :
- Erreur dans la génération du HTML
- Le div `process-log` n'est pas trouvé
- Le HTML est inséré mais invisible (problème CSS)

**Solutions** :
1. Dans la console, tapez :
```javascript
document.getElementById('process-log').children.length
```
Si le résultat est > 0, les entrées sont là mais invisibles → problème CSS

2. Dans la console, tapez :
```javascript
document.getElementById('process-log').innerHTML
```
Vérifiez si du HTML est présent

---

### Problème 4 : Les Processus Apparaissent puis Disparaissent

**Symptôme** : Vous voyez brièvement une entrée, puis elle disparaît

**Causes possibles** :
- Le message "En attente" est recréé
- Un autre script efface le contenu
- Le div est réinitialisé

**Solution** :
Regardez les logs dans la console. Vous devriez voir :
```
⚠️ Élément .text-center trouvé mais ce n'est pas le message initial, on garde le contenu
```

Si vous voyez :
```
🗑️ Suppression du message initial "En attente"
```
à chaque fois, il y a un problème avec la détection.

---

## 🔧 Commandes de Debug Utiles

### Dans la Console JavaScript (F12)

```javascript
// Vérifier l'état du moniteur
console.log('isPaused:', isPaused);
console.log('processCounter:', processCounter);

// Vérifier le contenu du div
const logDiv = document.getElementById('process-log');
console.log('Nombre d\'entrées:', logDiv.children.length);
console.log('Premier enfant:', logDiv.firstChild);

// Forcer l'affichage d'un processus test
displayProcess({
    timestamp: new Date().toISOString(),
    title: 'Test Manuel',
    type: 'test',
    status: 'info',
    steps: [{action: 'Test', details: 'Ceci est un test', status: 'success', completed: true}],
    crypto: {},
    result: {success: true, message: 'Test OK'}
});
```

### Dans le Terminal (serveur)

```bash
# Vérifier les processus Python
ps aux | grep python

# Vérifier le port
lsof -i :5001

# Tuer et relancer le serveur
lsof -ti:5001 | xargs kill -9
python start.py
```

---

## ✅ Checklist Complète

Avant de conclure que ça ne fonctionne pas, vérifiez :

- [ ] Le serveur est lancé avec `python start.py`
- [ ] Aucune erreur dans le terminal au démarrage
- [ ] La page `/processus` se charge sans erreur
- [ ] La console JavaScript (F12) est ouverte
- [ ] Vous voyez "Connecté au moniteur technique" dans la console
- [ ] Vous avez effectué un achat depuis `/client`
- [ ] Vous voyez les logs `[MONITOR]` dans le terminal
- [ ] Vous voyez les logs `📨` dans la console JavaScript
- [ ] Vous voyez les logs `🎨` dans la console JavaScript
- [ ] Le `logDiv.children.length` est > 0 après un achat

---

## 🎯 Test Final : Script Automatisé

Utilisez le script de test existant :

```bash
cd /Users/koblanemmanuel/Documents/TP_Cyber
python test_moniteur.py
```

Ce script :
1. Vérifie que le serveur est actif
2. Vérifie que `/processus` est accessible
3. Effectue un achat de test
4. Affiche le résultat

---

## 📞 Si Rien ne Fonctionne

1. **Redémarrage complet** :
```bash
# Tuer tous les processus Python
killall python
# Ou plus agressif
lsof -ti:5001 | xargs kill -9

# Relancer
python start.py
```

2. **Vider le cache du navigateur** :
- Chrome/Edge : Ctrl+Shift+Delete
- Firefox : Ctrl+Shift+Delete
- Safari : Cmd+Option+E

3. **Vérifier les versions** :
```bash
python --version  # Devrait être 3.x
pip show flask flask-socketio pycryptodome
```

---

**Bon test !** 🚀🔐

Si vous voyez tous les logs détaillés, le moniteur fonctionne parfaitement ! 🎉
