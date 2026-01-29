# 🔧 Guide de Diagnostic - Moniteur Technique

## ❌ Problème : "Je ne vois rien dans le moniteur"

### ✅ Solutions par Étapes

---

## ÉTAPE 1 : Vérifications de Base

### 1.1 Le serveur est-il lancé ?
```bash
python start.py
```

Vous devez voir :
```
✅ Système initialisé avec succès !
🌐 INTERFACE WEB DISPONIBLE
```

### 1.2 La page /processus charge-t-elle ?
Ouvrez : `http://localhost:5001/processus`

Vous devez voir :
```
🔬 Moniteur de Processus Techniques
Mode Développeur Activé
```

Si la page ne charge pas → **PROBLÈME SERVEUR**
Si la page charge → Passez à l'ÉTAPE 2

---

## ÉTAPE 2 : Vérifier le WebSocket

### 2.1 Ouvrir la Console du Navigateur
1. Sur la page `/processus`
2. Appuyez sur **F12**
3. Allez dans l'onglet **Console**

### 2.2 Vérifier la Connexion
Vous devez voir :
```
Connecté au moniteur technique
Moniteur technique initialisé
```

**Toast (notification)** : "Moniteur technique connecté" (vert)

❌ Si vous voyez **des erreurs** → **PROBLÈME WEBSOCKET**
✅ Si tout est OK → Passez à l'ÉTAPE 3

---

## ÉTAPE 3 : Tester une Action

### 3.1 Faire un Achat
1. **GARDEZ** l'onglet `/processus` ouvert avec la console (F12)
2. Ouvrez **un nouvel onglet** : `http://localhost:5001/client`
3. Effectuez un achat :
   - Client : Alice
   - Marchand : Amazon
   - Article : Test
   - Montant : 10
4. Cliquez sur **"Acheter"**

### 3.2 Vérifier les Logs Serveur
Dans le **terminal où tourne le serveur**, vous devez voir :
```
[ACHAT DÉTAILLÉ] Début pour Alice chez Amazon - 10€
[MONITOR] Émission processus technique: 💳 Achat de Alice chez Amazon - 10€
```

❌ Si vous ne voyez PAS ces messages → **PROBLÈME CODE**
✅ Si vous les voyez → Passez à 3.3

### 3.3 Vérifier la Console du Navigateur
Dans l'onglet `/processus`, console (F12), vous devez voir :
```
📨 Processus technique reçu: {title: "💳 Achat de Alice...", ...}
✅ Affichage du processus
🎨 Début affichage processus: 💳 Achat de Alice chez Amazon - 10€
```

❌ Si vous ne voyez PAS ces messages → **PROBLÈME WEBSOCKET**
✅ Si vous les voyez → Passez à 3.4

### 3.4 Vérifier l'Affichage
Dans la page `/processus`, vous devez voir apparaître une carte :
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 Achat de Alice chez Amazon - 10€
12:34:56
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

❌ Si rien ne s'affiche → **PROBLÈME JAVASCRIPT**

---

## 🔍 Diagnostics Détaillés

### PROBLÈME : Le serveur ne démarre pas
**Erreur** : `Address already in use`

**Solution** :
```bash
# Tuer le processus qui utilise le port 5001
lsof -ti:5001 | xargs kill -9

# Relancer
python start.py
```

---

### PROBLÈME : WebSocket ne se connecte pas
**Console du navigateur** : Erreur WebSocket

**Solutions** :

1. **Vérifier Socket.IO dans base.html** :
```javascript
const socket = io();
```

2. **Rafraîchir la page** (F5)

3. **Vider le cache** :
   - Chrome : Ctrl+Shift+R
   - Safari : Cmd+Shift+R

4. **Vérifier le firewall** (macOS) :
   ```bash
   # Autoriser les connexions locales
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/python3
   ```

---

### PROBLÈME : Les messages ne s'affichent pas dans le moniteur
**Console** : Messages reçus mais rien ne s'affiche

**Solutions** :

1. **Vérifier que le moniteur n'est PAS en pause** :
   - Bouton doit dire "Pause" (pas "Reprendre")
   - Si "Reprendre" → Cliquez dessus

2. **Effacer et réessayer** :
   - Cliquez sur "Effacer"
   - Refaites un achat

3. **Vérifier JavaScript** :
   - Console (F12) → Onglet Console
   - Regardez s'il y a des erreurs JavaScript

---

### PROBLÈME : Le code n'appelle pas acheter_avec_details()
**Terminal serveur** : Pas de message `[ACHAT DÉTAILLÉ]`

**Solution** :

Vérifiez dans `app.py` ligne ~184 :
```python
# NOUVEAU : Acheter avec logging technique détaillé
succes, message = acheter_avec_details(client, marchand, items, montant)
```

Si vous voyez à la place :
```python
succes, message = client.acheter(marchand, items, montant)
```

→ Remplacez par la première version !

---

## 🧪 Script de Test Automatique

Lancez le script de test :
```bash
python test_moniteur.py
```

Ce script va :
- ✅ Vérifier que le serveur tourne
- ✅ Tester la page /processus
- ✅ Effectuer un achat de test
- ✅ Vous donner des instructions détaillées

---

## 📋 Checklist de Vérification Complète

Cochez chaque point :

- [ ] Serveur lancé avec `python start.py`
- [ ] Page `/processus` s'affiche correctement
- [ ] Console du navigateur (F12) ouverte
- [ ] Message "Connecté au moniteur technique" dans la console
- [ ] Bouton "Pause" (pas "Reprendre")
- [ ] Achat effectué depuis `/client`
- [ ] Logs `[ACHAT DÉTAILLÉ]` visibles dans le terminal serveur
- [ ] Logs `[MONITOR]` visibles dans le terminal serveur
- [ ] Messages `📨 Processus technique reçu` dans la console navigateur
- [ ] Carte du processus visible dans `/processus`

---

## 🆘 Toujours Pas de Solution ?

### Option 1 : Redémarrage Complet
```bash
# 1. Arrêter le serveur (Ctrl+C)
# 2. Tuer tous les processus Python
killall -9 python3

# 3. Nettoyer le port
lsof -ti:5001 | xargs kill -9

# 4. Relancer
python start.py

# 5. Rafraîchir le navigateur (Ctrl+Shift+R)
```

### Option 2 : Test avec curl
```bash
# Test de l'API d'achat
curl -X POST http://localhost:5001/api/acheter \
  -H "Content-Type: application/json" \
  -d '{"client":"Alice","marchand":"Amazon","items":["Test"],"montant":10}'
```

Regardez les logs du serveur → Vous devez voir `[ACHAT DÉTAILLÉ]`

### Option 3 : Vérifier les Modifications
Assurez-vous que les modifications suivantes sont bien présentes dans `app.py` :

**Ligne ~45** :
```python
socketio.emit('technical_process', technical_log, broadcast=True)
print(f"[MONITOR] Émission processus technique: {title}")
```

**Ligne ~58** :
```python
socketio.emit('nouveau_log', log_entry, broadcast=True)
```

**Ligne ~72** :
```python
socketio.emit('security_alert', security_log, broadcast=True)
```

**Ligne ~184** :
```python
succes, message = acheter_avec_details(client, marchand, items, montant)
```

**Ligne ~215** :
```python
print(f"\n[ACHAT DÉTAILLÉ] Début pour {client.nom} chez {marchand.nom} - {montant}€")
```

---

## ✅ Solution Finale : Fichiers de Log

Si rien ne fonctionne, **envoyez-moi** :

1. **Logs du serveur** (terminal) :
```bash
python start.py > server.log 2>&1
```

2. **Logs de la console navigateur** :
   - F12 → Console → Clic droit → Save as...

3. **Screenshot de la page /processus**

---

**Dernière mise à jour** : 22 janvier 2026
