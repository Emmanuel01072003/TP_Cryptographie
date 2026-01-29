# 🚀 DÉMARRAGE RAPIDE - Moniteur Technique

## 📍 Vous Êtes Ici

Vous avez fait un achat mais **rien ne s'affiche** dans `/processus` ?

**Suivez ce guide étape par étape !**

---

## ✅ ÉTAPE 1 : Lancer le Serveur

```bash
cd /Users/koblanemmanuel/Documents/TP_Cyber
python start.py
```

**Attendez de voir** :
```
✅ Système initialisé avec succès !
📱 Accédez à l'application sur : http://localhost:5001
```

**⚠️ Si erreur "Port 5001 in use"** :
```bash
lsof -ti:5001 | xargs kill -9
python start.py
```

---

## ✅ ÉTAPE 2 : Ouvrir DEUX Onglets

### Onglet 1 (GAUCHE) - Moniteur
```
http://localhost:5001/processus
```

### Onglet 2 (DROITE) - Client
```
http://localhost:5001/client
```

**Placez-les côte à côte !**

---

## ✅ ÉTAPE 3 : Ouvrir la Console (IMPORTANT !)

**Dans l'onglet MONITEUR (gauche)** :
1. Appuyez sur **F12** (ou Cmd+Option+I sur Mac)
2. Cliquez sur l'onglet **"Console"**
3. **LAISSEZ-LA OUVERTE !**

**Vous devez voir** :
```
Connecté au moniteur technique
Moniteur technique initialisé
```

Et une **notification verte** : "Moniteur technique connecté"

**❌ Si vous ne voyez PAS ce message** → Rafraîchissez (F5)

---

## ✅ ÉTAPE 4 : Faire un Achat

**Dans l'onglet CLIENT (droite)** :

1. Client : **Alice**
2. Marchand : **Amazon**
3. Article : `Test Moniteur`
4. Montant : **10**
5. Cliquez sur **"Acheter"**

---

## ✅ ÉTAPE 5 : Vérifier les Résultats

### 5.1 Dans le TERMINAL (où tourne le serveur)

Vous **DEVEZ** voir :
```
[ACHAT DÉTAILLÉ] Début pour Alice chez Amazon - 10€
[MONITOR] Émission processus technique: 💳 Achat de Alice chez Amazon - 10€
```

**❌ Si vous ne voyez PAS** ces messages :
- Le code n'est pas à jour
- Consultez `DIAGNOSTIC_MONITEUR.md`

### 5.2 Dans la CONSOLE du Navigateur (F12)

Vous **DEVEZ** voir :
```
📨 Processus technique reçu: {title: "💳 Achat de Alice...", type: "transaction", ...}
✅ Affichage du processus
🎨 Début affichage processus: 💳 Achat de Alice chez Amazon - 10€
```

**❌ Si vous ne voyez PAS** ces messages :
- Le WebSocket n'est pas connecté
- Rafraîchissez la page (F5)
- Vérifiez que le bouton dit "Pause" (pas "Reprendre")

### 5.3 Dans la PAGE /processus

Vous **DEVEZ** voir apparaître une grande carte :
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💳 Achat de Alice chez Amazon - 10€
12:34:56

Étape 1 ✅ Génération des identifiants
Étape 2 ✅ Création Order Info
...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**❌ Si rien ne s'affiche** :
- Vérifiez étapes 5.1 et 5.2 ci-dessus
- Le problème est identifié là

---

## 🔧 Problèmes Courants

### Problème 1 : Pas de `[ACHAT DÉTAILLÉ]` dans le terminal

**Cause** : Le code n'appelle pas la bonne fonction

**Solution** :
```bash
# Vérifier que les modifications sont bien faites
grep -n "acheter_avec_details" app.py
```

Vous devez voir :
```
210:def acheter_avec_details(client, marchand, items, montant):
184:    succes, message = acheter_avec_details(client, marchand, items, montant)
```

**Si vous voyez ligne 184** :
```python
succes, message = client.acheter(marchand, items, montant)
```

→ **C'EST LE PROBLÈME !** Le code n'est pas à jour.

---

### Problème 2 : Pas de `📨 Processus technique reçu` dans la console

**Cause** : WebSocket pas connecté ou broadcast pas activé

**Solution 1** : Rafraîchir la page (F5)

**Solution 2** : Vérifier dans `app.py` ligne 45 :
```python
socketio.emit('technical_process', technical_log, broadcast=True)
```

Le **`, broadcast=True`** est crucial !

---

### Problème 3 : Le moniteur est en pause

**Symptôme** : Le bouton dit "Reprendre" au lieu de "Pause"

**Solution** : Cliquez sur le bouton "Reprendre"

---

## 🧪 Test Automatique

Lancez le script de test :
```bash
python test_moniteur.py
```

Il va tout vérifier automatiquement et vous dire exactement où est le problème.

---

## 📚 Documentation Complète

Pour plus de détails, consultez :
- **`DIAGNOSTIC_MONITEUR.md`** - Guide de diagnostic complet
- **`README_MONITEUR_TECHNIQUE.md`** - Documentation du moniteur

---

## ✅ Récapitulatif Visuel

```
┌─────────────────────────────────────────────────────┐
│ TERMINAL (serveur)                                  │
│                                                     │
│ [ACHAT DÉTAILLÉ] Début pour Alice...    ← DOIT     │
│ [MONITOR] Émission processus...          VOIR ÇA   │
└─────────────────────────────────────────────────────┘

┌──────────────────────┬──────────────────────────────┐
│ /processus (F12)     │ /client                      │
│                      │                              │
│ Console:             │ [Faire un achat]             │
│ 📨 Processus reçu ✅ │ Client: Alice                │
│ ✅ Affichage        │ Marchand: Amazon             │
│ 🎨 Début affichage   │ Montant: 10                  │
│                      │ [Acheter] ← CLIQUER          │
│ Page:                │                              │
│ ┌─────────────────┐  │                              │
│ │ 💳 Achat de... │  │                              │
│ │ Étape 1 ✅     │  │                              │
│ │ ...            │  │                              │
│ └─────────────────┘  │                              │
└──────────────────────┴──────────────────────────────┘
```

---

**🎉 Si vous voyez tout ça → SUCCÈS !**
**❌ Si quelque chose manque → Consultez `DIAGNOSTIC_MONITEUR.md`**
