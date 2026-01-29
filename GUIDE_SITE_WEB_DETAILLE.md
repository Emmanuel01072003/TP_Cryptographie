# 🌐 GUIDE DÉTAILLÉ DE L'INTERFACE WEB - Protocole SET/CDA
## Comprendre le site web de A à Z pour l'expliquer à votre professeur

---

## 🎯 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture Flask](#architecture-flask)
3. [Backend (app.py)](#backend-apppy)
4. [Frontend (Templates HTML)](#frontend-templates-html)
5. [Communication Temps Réel (WebSockets)](#communication-temps-réel-websockets)
6. [Pages du Site](#pages-du-site)
7. [Design et Interface](#design-et-interface)
8. [Flux de Données](#flux-de-données)

---

## 📖 Vue d'Ensemble

### Qu'est-ce qu'une Application Web ?

Une application web, c'est comme un **restaurant** :

| Partie | Analogie Restaurant | Application Web |
|--------|-------------------|-----------------|
| **Frontend** | La salle, le menu, les serveurs | HTML, CSS, JavaScript |
| **Backend** | La cuisine | Flask (Python) |
| **Base de données** | Le frigo, le stock | Variables Python (comptes, transactions) |
| **API** | Les serveurs qui prennent commandes | Routes Flask (/api/...) |

### Architecture 3-Tiers

```
┌─────────────────┐
│   NAVIGATEUR    │ ← Vous voyez le site
│   (Frontend)    │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   FLASK SERVER  │ ← Traite les requêtes
│   (Backend)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PROJET.PY     │ ← Logique métier SET
│   (Business)    │
└─────────────────┘
```

### Technologies Utilisées

#### Backend
- **Flask** : Framework web Python (comme Express.js pour JavaScript)
- **Flask-SocketIO** : Communication temps réel (WebSockets)
- **Python** : Langage de programmation

#### Frontend
- **HTML** : Structure des pages
- **CSS** : Style et design
- **JavaScript** : Interactivité
- **Bootstrap 5** : Framework CSS (design prêt à l'emploi)
- **Chart.js** : Graphiques
- **Socket.IO** : WebSockets côté client

---

## 🏗️ Architecture Flask

### Qu'est-ce que Flask ?

**Flask** est un **framework web** pour Python. Il permet de :
- Créer des pages web
- Gérer des routes (URLs)
- Traiter des requêtes HTTP
- Envoyer des réponses JSON

### Analogie

Flask c'est comme un **standard téléphonique** :
- Quand quelqu'un appelle `/dashboard` → Transférer à la fonction `dashboard()`
- Quand quelqu'un appelle `/api/acheter` → Transférer à la fonction `api_acheter()`

### Structure de Base

```python
from flask import Flask

# Créer l'application
app = Flask(__name__)

# Définir une route
@app.route('/')
def index():
    return "Bonjour !"

# Lancer le serveur
app.run()
```

**Explication** :
1. `Flask(__name__)` : Créer l'application
2. `@app.route('/')` : Dire "si quelqu'un va sur /..."
3. `def index():` : ...exécuter cette fonction
4. `return "Bonjour !"` : Renvoyer ce texte

---

## 🔧 Backend (app.py)

### Imports

```python
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from projet import *
import threading
import secrets
from datetime import datetime
import json as json_lib
```

**Explication** :

| Import | Rôle | Analogie |
|--------|------|----------|
| `Flask` | Framework web | Le restaurant |
| `render_template` | Afficher des pages HTML | Le menu |
| `request` | Recevoir des données du client | La commande du client |
| `jsonify` | Envoyer du JSON | L'addition au format lisible |
| `SocketIO` | Communication temps réel | Téléphone direct avec la cuisine |
| `emit` | Envoyer un message WebSocket | Appeler un serveur |
| `projet import *` | Importer nos classes SET | Utiliser nos recettes |

### Initialisation de l'Application

```python
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
socketio = SocketIO(app, cors_allowed_origins="*")
```

**Ligne par ligne** :

#### `app = Flask(__name__)`
Créer l'application Flask.

#### `app.secret_key = secrets.token_hex(32)`
Clé secrète pour chiffrer les sessions.
- `secrets.token_hex(32)` : Génère 32 octets aléatoires en hexadécimal
- **Pourquoi ?** : Sécuriser les cookies de session

#### `socketio = SocketIO(app, cors_allowed_origins="*")`
Activer les WebSockets.
- `cors_allowed_origins="*"` : Autoriser toutes les origines (pour le dev)
- **Production** : Mettre l'URL précise du site

### Variables Globales

```python
ca = None
banque = None
marchands = {}
clients = {}
logs_globaux = []
```

**Pourquoi globales ?**
- Partagées entre toutes les requêtes
- Simule une "base de données" en mémoire
- **Attention** : En production, utiliser une vraie BDD (PostgreSQL, MongoDB, etc.)

### Fonction : `log_event()`

```python
def log_event(event_type, actor, message, details=None):
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'type': event_type,
        'actor': actor,
        'message': message,
        'details': details or {}
    }
    logs_globaux.append(log_entry)
    socketio.emit('nouveau_log', log_entry)
    return log_entry
```

**Rôle** : Enregistrer et diffuser un événement en temps réel

**Étapes** :
1. Créer un dictionnaire avec les infos de l'événement
2. Ajouter à la liste `logs_globaux`
3. **Émettre** via WebSocket à tous les clients connectés
4. Retourner le log

**Exemple d'utilisation** :
```python
log_event('transaction', 'Alice', 'Achat effectué', {'montant': 45})
```

### Fonction : `init_system()`

```python
def init_system():
    global ca, banque, marchands, clients
    
    log_event('system', 'Système', 'Initialisation du système SET/CDA')
    
    ca = AutoriteCertification()
    banque = Banque(ca)
    
    marchands['Amazon'] = Marchand("Amazon", ca, banque)
    marchands['FNAC'] = Marchand("FNAC", ca, banque)
    marchands['Darty'] = Marchand("Darty", ca, banque)
    
    clients['Alice'] = Client("Alice", "4970-1111-2222-3333", ca)
    clients['Bob'] = Client("Bob", "4970-4444-5555-6666", ca)
    clients['Charlie'] = Client("Charlie", "4970-7777-8888-9999", ca)
    
    log_event('system', 'Système', f'Système initialisé avec {len(ca.certificats_emis)} certificats')
```

**Rôle** : Initialiser le système SET au démarrage

**Utilise `global`** : Car on modifie les variables globales

### Routes : Pages Web

#### Route `/`

```python
@app.route('/')
def index():
    return render_template('index.html')
```

**Explication** :
- `@app.route('/')` : Quand on va sur `http://localhost:5001/`
- `def index():` : Exécuter cette fonction
- `render_template('index.html')` : Afficher le fichier `templates/index.html`

**Analogie** : Quand quelqu'un entre dans le restaurant, lui donner le menu.

#### Route `/dashboard`

```python
@app.route('/dashboard')
def dashboard():
    if not ca:
        init_system()
    
    stats = {
        'total_certificats': len(ca.certificats_emis),
        'certificats_actifs': len([c for c in ca.certificats_emis.values() if not c.revoque]),
        'certificats_revoques': len(ca.certificats_revoques),
        'total_transactions': len(banque.historique_transactions),
        'transactions_reussies': len([t for t in banque.historique_transactions if t['statut'] == 'approuvé']),
        'montant_total': sum(t['montant'] for t in banque.historique_transactions),
        'total_marchands': len(marchands),
        'total_clients': len(clients)
    }
    
    return render_template('dashboard.html', stats=stats)
```

**Étapes** :
1. Si le système n'est pas initialisé → l'initialiser
2. Calculer les statistiques :
   - Nombre de certificats
   - Nombre de transactions
   - Montant total
3. Passer ces stats au template HTML
4. Afficher `dashboard.html` avec ces données

**Passage de données au template** :
```python
render_template('dashboard.html', stats=stats)
```
→ Dans le HTML, on peut utiliser `{{ stats.total_certificats }}`

### Routes : API

#### Route `/api/acheter`

```python
@app.route('/api/acheter', methods=['POST'])
def api_acheter():
    try:
        # 1. Récupérer les données JSON envoyées
        data = request.json
        client_nom = data['client']
        marchand_nom = data['marchand']
        items = data['items']
        montant = float(data['montant'])
        
        # 2. Vérifier que le client existe
        if client_nom not in clients:
            return jsonify({'success': False, 'message': 'Client inconnu'}), 400
        
        # 3. Vérifier que le marchand existe
        if marchand_nom not in marchands:
            return jsonify({'success': False, 'message': 'Marchand inconnu'}), 400
        
        # 4. Récupérer les objets
        client = clients[client_nom]
        marchand = marchands[marchand_nom]
        
        # 5. Logger l'événement
        log_event('transaction', client_nom, f'Tentative d\'achat chez {marchand_nom}', {
            'items': items,
            'montant': montant
        })
        
        # 6. Effectuer l'achat
        succes, message = client.acheter(marchand, items, montant)
        
        # 7. Logger le résultat
        if succes:
            log_event('transaction', client_nom, f'Achat réussi chez {marchand_nom}', {
                'items': items,
                'montant': montant,
                'message': message
            })
        else:
            log_event('transaction', client_nom, f'Achat refusé chez {marchand_nom}', {
                'items': items,
                'montant': montant,
                'raison': message
            })
        
        # 8. Retourner le résultat en JSON
        return jsonify({
            'success': succes,
            'message': message,
            'nouveau_solde': banque.get_solde(client.carte)
        })
        
    except Exception as e:
        log_event('error', 'Système', f'Erreur lors de l\'achat: {str(e)}')
        return jsonify({'success': False, 'message': str(e)}), 500
```

**Explication détaillée** :

##### Étape 1 : Recevoir les données
```python
data = request.json
```
- `request` : Objet Flask qui contient la requête HTTP
- `.json` : Les données JSON envoyées par le client

**Exemple de données reçues** :
```json
{
  "client": "Alice",
  "marchand": "Amazon",
  "items": ["Livre Python"],
  "montant": 45
}
```

##### Étape 2-3 : Validation
```python
if client_nom not in clients:
    return jsonify({'success': False, 'message': 'Client inconnu'}), 400
```
- Vérifier que le client existe
- Si non → Retourner une erreur 400 (Bad Request)
- `jsonify()` : Convertir un dict Python en JSON

##### Étape 6 : Appeler la logique métier
```python
succes, message = client.acheter(marchand, items, montant)
```
- Appelle la méthode du fichier `projet.py`
- Exécute toute la logique SET (chiffrement, signature, etc.)

##### Étape 8 : Retourner le résultat
```python
return jsonify({
    'success': succes,
    'message': message,
    'nouveau_solde': banque.get_solde(client.carte)
})
```

**Exemple de réponse** :
```json
{
  "success": true,
  "message": "Commande validée (ARQC: a3f2d9e1...)",
  "nouveau_solde": 4955
}
```

#### Route `/api/stats`

```python
@app.route('/api/stats')
def api_stats():
    if not ca:
        init_system()
    
    return jsonify({
        'certificats': {
            'total': len(ca.certificats_emis),
            'actifs': len([c for c in ca.certificats_emis.values() if not c.revoque]),
            'revoques': len(ca.certificats_revoques)
        },
        'transactions': {
            'total': len(banque.historique_transactions),
            'reussies': len([t for t in banque.historique_transactions if t['statut'] == 'approuvé']),
            'montant_total': sum(t['montant'] for t in banque.historique_transactions)
        },
        'marchands': {
            'total': len(marchands),
            'liste': list(marchands.keys())
        },
        'clients': {
            'total': len(clients),
            'liste': list(clients.keys())
        }
    })
```

**Rôle** : Retourner toutes les statistiques du système en JSON

**Utilisé par** : Dashboard pour afficher les chiffres en temps réel

#### Route `/api/certificats`

```python
@app.route('/api/certificats')
def api_certificats():
    if not ca:
        init_system()
    
    certs_data = []
    for cert in ca.certificats_emis.values():
        valide, raison = cert.est_valide()
        certs_data.append({
            'numero_serie': cert.numero_serie,
            'sujet': cert.sujet,
            'emetteur': cert.emetteur,
            'date_creation': cert.date_creation.isoformat(),
            'date_expiration': cert.date_expiration.isoformat(),
            'valide': valide,
            'raison': raison,
            'revoque': cert.revoque
        })
    
    return jsonify(certs_data)
```

**Rôle** : Retourner la liste de tous les certificats

**Transformation** :
- Objet Python `Certificat` → Dictionnaire → JSON

**Pourquoi `.isoformat()` ?**
- Les dates Python ne sont pas sérialisables en JSON
- `.isoformat()` : Convertir en texte (ex: `"2026-01-22T14:30:00"`)

---

## 🎨 Frontend (Templates HTML)

### Qu'est-ce qu'un Template ?

Un **template** est un fichier HTML avec des **variables** et de la **logique**.

**Analogie** : C'est comme un **formulaire à remplir** :
- `Bonjour {{ nom }} !` → Template
- `Bonjour Alice !` → Résultat après remplissage

### Syntaxe Jinja2

Flask utilise **Jinja2** pour les templates.

#### Variables

```html
<h1>Bonjour {{ nom }} !</h1>
```

Si `nom = "Alice"` → Affiche `<h1>Bonjour Alice !</h1>`

#### Conditions

```html
{% if solde > 100 %}
    <p>Vous êtes riche !</p>
{% else %}
    <p>Vous êtes pauvre...</p>
{% endif %}
```

#### Boucles

```html
<ul>
{% for client in clients %}
    <li>{{ client }}</li>
{% endfor %}
</ul>
```

Si `clients = ["Alice", "Bob"]` → Affiche :
```html
<ul>
    <li>Alice</li>
    <li>Bob</li>
</ul>
```

### Héritage de Templates

#### Template de Base (`base.html`)

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Mon Site{% endblock %}</title>
</head>
<body>
    <nav>Menu de navigation</nav>
    
    {% block content %}
    <!-- Le contenu sera inséré ici -->
    {% endblock %}
    
    <footer>Pied de page</footer>
</body>
</html>
```

#### Template Enfant (`dashboard.html`)

```html
{% extends "base.html" %}

{% block title %}Dashboard - Mon Site{% endblock %}

{% block content %}
    <h1>Tableau de Bord</h1>
    <p>Contenu spécifique au dashboard</p>
{% endblock %}
```

**Résultat** : Le contenu de `dashboard.html` est **inséré** dans `base.html`

**Avantage** : On définit la structure une seule fois (menu, footer) et chaque page hérite de cette structure.

---

## 📡 Communication Temps Réel (WebSockets)

### Qu'est-ce que WebSocket ?

**HTTP classique** :
```
Client → "Donne-moi les nouvelles données" → Serveur
Client ← "Voilà les données" ← Serveur
(répéter toutes les secondes)
```

**WebSocket** :
```
Client ⇄ Canal permanent ⇄ Serveur
```

Dès qu'il y a une nouvelle donnée, le serveur **pousse** au client automatiquement.

**Analogie** :
- **HTTP** : Téléphoner toutes les 5 secondes pour demander "Y a-t-il du courrier ?"
- **WebSocket** : Le facteur vous appelle dès qu'il y a du courrier

### Côté Backend (Python)

#### Connexion

```python
@socketio.on('connect')
def handle_connect():
    if not ca:
        init_system()
    emit('connected', {'message': 'Connecté au serveur SET'})
```

**Quand ?** : Dès qu'un client ouvre la page web

**Action** :
1. Initialiser le système si besoin
2. Envoyer un message de confirmation au client

#### Émission d'événements

```python
socketio.emit('nouveau_log', log_entry)
```

**Rôle** : Envoyer `log_entry` à **tous** les clients connectés

**Événement** : `'nouveau_log'`

### Côté Frontend (JavaScript)

#### Connexion

```javascript
const socket = io();

socket.on('connect', function() {
    console.log('Connecté au serveur WebSocket');
});
```

**Explication** :
- `io()` : Se connecter au serveur WebSocket
- `socket.on('connect', ...)` : Quand connecté, exécuter cette fonction

#### Réception d'événements

```javascript
socket.on('nouveau_log', function(log) {
    console.log('Nouveau log:', log);
    // Afficher le log sur la page
});
```

**Quand ?** : Dès que le serveur émet un événement `'nouveau_log'`

**Action** : Afficher le log en temps réel sur la page

### Exemple Complet

**Scénario** : Alice achète un livre

1. **Alice clique sur "Acheter"**
   ```javascript
   // Frontend envoie une requête POST
   fetch('/api/acheter', {
       method: 'POST',
       body: JSON.stringify({client: 'Alice', ...})
   })
   ```

2. **Backend traite l'achat**
   ```python
   succes, message = client.acheter(marchand, items, montant)
   log_event('transaction', 'Alice', 'Achat réussi', {...})
   ```

3. **Backend émet un événement WebSocket**
   ```python
   socketio.emit('nouveau_log', log_entry)
   ```

4. **Frontend reçoit l'événement**
   ```javascript
   socket.on('nouveau_log', function(log) {
       // Afficher le log dans la page Dashboard
   })
   ```

5. **Tous les utilisateurs** connectés au Dashboard voient le log **instantanément** !

---

## 📄 Pages du Site

### 1. Page d'Accueil (`index.html`)

**URL** : `http://localhost:5001/`

**Contenu** :
- Présentation du protocole SET/CDA
- Cartes avec fonctionnalités
- Architecture du système
- Analyse de sécurité
- Liens vers les autres pages

**Code clé** :

```html
{% extends "base.html" %}

{% block content %}
<div class="row justify-content-center mt-5">
    <div class="col-lg-10">
        <div class="text-center mb-5">
            <h1 class="display-3 fw-bold text-white mb-4">
                <i class="bi bi-shield-lock-fill"></i>
                Simulation Protocole SET/CDA
            </h1>
        </div>
        
        <!-- Cartes de fonctionnalités -->
        <div class="row g-4 mb-5">
            <div class="col-md-4">
                <div class="card h-100 text-center">
                    <div class="card-body p-4">
                        <div class="stat-icon mx-auto">
                            <i class="bi bi-shield-check text-white"></i>
                        </div>
                        <h3>Sécurité Renforcée</h3>
                        <p>Chiffrement RSA 2048 bits...</p>
                    </div>
                </div>
            </div>
            <!-- 2 autres cartes similaires -->
        </div>
    </div>
</div>
{% endblock %}
```

**Éléments importants** :

- `{% extends "base.html" %}` : Hérite du template de base
- `{% block content %}` : Contenu spécifique à cette page
- Classes Bootstrap : `row`, `col-md-4`, `card`, etc.
- Icônes Bootstrap : `<i class="bi bi-shield-lock-fill"></i>`

### 2. Dashboard (`dashboard.html`)

**URL** : `http://localhost:5001/dashboard`

**Contenu** :
- 4 cartes de statistiques (certificats, transactions, volume, entités)
- Graphique des transactions (Chart.js)
- Graphique répartition marchands (Chart.js)
- Soldes des comptes
- Logs en temps réel
- Tableau des dernières transactions

**Code clé : Cartes de Statistiques**

```html
<div class="col-md-3">
    <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #667eea, #764ba2);">
            <i class="bi bi-award-fill text-white"></i>
        </div>
        <h6 class="text-muted text-uppercase small mb-2">Certificats Actifs</h6>
        <h2 class="fw-bold mb-0" id="stat-certificats-actifs">{{ stats.certificats_actifs }}</h2>
        <small class="text-muted">/ {{ stats.total_certificats }} total</small>
    </div>
</div>
```

**Explication** :
- `{{ stats.certificats_actifs }}` : Variable passée depuis Python
- `id="stat-certificats-actifs"` : Pour mettre à jour avec JavaScript
- Classes CSS : `stat-card`, `stat-icon`, etc. (définies dans `base.html`)

**Code clé : Graphique Chart.js**

```html
<canvas id="transactionsChart" height="100"></canvas>

<script>
function updateTransactionsChart(transactions) {
    const ctx = document.getElementById('transactionsChart');
    
    // Préparer les données
    const dates = {};
    transactions.forEach(trans => {
        const date = new Date(trans.timestamp).toLocaleDateString('fr-FR');
        dates[date] = (dates[date] || 0) + trans.montant;
    });
    
    const labels = Object.keys(dates).slice(-7);
    const data = labels.map(label => dates[label]);
    
    // Créer le graphique
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Volume (€)',
                data: data,
                borderColor: 'rgb(99, 102, 241)',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}
</script>
```

**Explication** :

1. `<canvas>` : Élément HTML où le graphique sera dessiné
2. Récupérer les transactions
3. Grouper par date et sommer les montants
4. Créer un graphique de type `'line'` (ligne)
5. Définir les données et les options

**Code clé : Logs Temps Réel**

```html
<div id="logs-container"></div>

<script>
socket.on('nouveau_log', function(log) {
    loadStats();
    loadTransactions();
    loadSoldes();
    loadLogs();
});

function loadLogs() {
    fetch('/api/logs')
        .then(response => response.json())
        .then(logs => {
            const container = document.getElementById('logs-container');
            container.innerHTML = '';
            
            logs.slice(-15).reverse().forEach(log => {
                const logHtml = `
                    <div class="log-item">
                        <div class="d-flex justify-content-between">
                            <div>
                                <span class="badge bg-${log.type === 'error' ? 'danger' : 'info'}">
                                    ${log.type}
                                </span>
                                <strong>${log.actor}</strong>
                                <p>${log.message}</p>
                            </div>
                            <small>${new Date(log.timestamp).toLocaleTimeString('fr-FR')}</small>
                        </div>
                    </div>
                `;
                container.innerHTML += logHtml;
            });
        });
}
</script>
```

**Étapes** :
1. Écouter l'événement `'nouveau_log'` via WebSocket
2. Dès qu'un nouveau log arrive → Recharger toutes les données
3. Récupérer les logs via `/api/logs`
4. Créer le HTML pour chaque log
5. Injecter dans le container

### 3. Interface Client (`client.html`)

**URL** : `http://localhost:5001/client`

**Contenu** :
- Formulaire d'achat sécurisé
- Sélection client/marchand
- Ajout dynamique d'articles
- Affichage du solde
- Explications du processus

**Code clé : Formulaire**

```html
<form id="achat-form">
    <div class="row g-3">
        <!-- Sélection client -->
        <div class="col-md-6">
            <select class="form-select" id="client-select" required>
                <option value="">Sélectionnez un client...</option>
                {% for nom in clients.keys() %}
                <option value="{{ nom }}">{{ nom }}</option>
                {% endfor %}
            </select>
        </div>
        
        <!-- Sélection marchand -->
        <div class="col-md-6">
            <select class="form-select" id="marchand-select" required>
                <option value="">Sélectionnez un marchand...</option>
                {% for nom in marchands.keys() %}
                <option value="{{ nom }}">{{ nom }}</option>
                {% endfor %}
            </select>
        </div>
        
        <!-- Articles -->
        <div class="col-12">
            <div id="items-container">
                <div class="input-group mb-2">
                    <input type="text" class="form-control item-input" 
                           placeholder="Ex: Livre Python..." required>
                    <button class="btn btn-outline-danger remove-item-btn" type="button">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
            <button type="button" class="btn btn-outline-primary" id="add-item-btn">
                <i class="bi bi-plus-circle"></i> Ajouter un article
            </button>
        </div>
        
        <!-- Montant -->
        <div class="col-md-6">
            <input type="number" class="form-control" id="montant-input" 
                   min="0.01" step="0.01" placeholder="0.00" required>
        </div>
        
        <!-- Bouton d'achat -->
        <div class="col-12">
            <button type="submit" class="btn btn-primary btn-lg w-100">
                <i class="bi bi-lock-fill"></i>
                Effectuer l'Achat Sécurisé
            </button>
        </div>
    </div>
</form>
```

**Explication** :

- `{% for nom in clients.keys() %}` : Boucle sur les clients
- `<option value="{{ nom }}">{{ nom }}</option>` : Créer une option pour chaque client
- `id="achat-form"` : Pour capturer la soumission en JavaScript
- `required` : Champ obligatoire

**Code clé : Ajout Dynamique d'Articles**

```javascript
document.getElementById('add-item-btn').addEventListener('click', function() {
    const container = document.getElementById('items-container');
    
    // Créer un nouvel élément
    const newItem = document.createElement('div');
    newItem.className = 'input-group mb-2';
    newItem.innerHTML = `
        <input type="text" class="form-control item-input" placeholder="Nom de l'article" required>
        <button class="btn btn-outline-danger remove-item-btn" type="button">
            <i class="bi bi-trash"></i>
        </button>
    `;
    
    // Ajouter au container
    container.appendChild(newItem);
    
    // Ajouter l'événement de suppression
    newItem.querySelector('.remove-item-btn').addEventListener('click', function() {
        newItem.remove();
    });
});
```

**Étapes** :
1. Écouter le clic sur "Ajouter un article"
2. Créer un nouvel `<div>` avec un input et un bouton supprimer
3. Ajouter au container
4. Permettre de supprimer cet article

**Code clé : Soumission du Formulaire**

```javascript
document.getElementById('achat-form').addEventListener('submit', function(e) {
    e.preventDefault();  // Empêcher le rechargement de la page
    
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span> Transaction en cours...';
    
    // Récupérer les données
    const client = document.getElementById('client-select').value;
    const marchand = document.getElementById('marchand-select').value;
    const montant = parseFloat(document.getElementById('montant-input').value);
    
    const items = Array.from(document.querySelectorAll('.item-input'))
        .map(input => input.value.trim())
        .filter(item => item !== '');
    
    // Envoyer la requête POST
    fetch('/api/acheter', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            client: client,
            marchand: marchand,
            items: items,
            montant: montant
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('✅ Transaction réussie ! ' + data.message, 'success');
            // Mettre à jour le solde affiché
            // Réinitialiser le formulaire
        } else {
            showToast('❌ Transaction refusée : ' + data.message, 'danger');
        }
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-lock-fill"></i> Effectuer l\'Achat Sécurisé';
    });
});
```

**Étapes** :
1. Capturer la soumission du formulaire
2. `e.preventDefault()` : Empêcher le comportement par défaut (rechargement)
3. Désactiver le bouton et afficher un loader
4. Récupérer toutes les valeurs des champs
5. Envoyer une requête POST à `/api/acheter`
6. Traiter la réponse (succès ou échec)
7. Afficher un toast (notification)
8. Réactiver le bouton

### 4. Interface Marchand (`marchand.html`)

**URL** : `http://localhost:5001/marchand`

**Contenu** :
- Sélection du marchand
- Statistiques (total commandes, CA, panier moyen)
- Liste des commandes avec détails

**Code clé : Chargement des Commandes**

```javascript
function loadCommandes(marchand) {
    fetch(`/api/commandes/${marchand}`)
        .then(response => response.json())
        .then(commandes => {
            const tbody = document.getElementById('commandes-tbody');
            tbody.innerHTML = '';
            
            // Calculer les stats
            const ca = commandes.reduce((sum, cmd) => sum + cmd.montant, 0);
            document.getElementById('stat-ca').textContent = ca.toFixed(2) + '€';
            
            // Afficher chaque commande
            commandes.forEach(cmd => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><code>${cmd.id.substring(0, 13)}...</code></td>
                    <td><strong>${cmd.client}</strong></td>
                    <td>
                        <span class="badge bg-light text-dark">${cmd.items.length} article(s)</span>
                        <br><small>${cmd.items.join(', ')}</small>
                    </td>
                    <td><strong>${cmd.montant}€</strong></td>
                    <td>${new Date(cmd.timestamp).toLocaleString('fr-FR')}</td>
                    <td><code>${cmd.arqc.substring(0, 16)}...</code></td>
                    <td><span class="badge bg-success">✓ ${cmd.statut}</span></td>
                `;
                tbody.appendChild(tr);
            });
        });
}
```

**Explication** :
1. Récupérer les commandes du marchand via l'API
2. Calculer le chiffre d'affaires avec `reduce()`
3. Pour chaque commande, créer une ligne de tableau `<tr>`
4. Formater les dates, montants, etc.
5. Ajouter au tableau

### 5. Interface Banque (`banque.html`)

**URL** : `http://localhost:5001/banque`

**Contenu** :
- Statistiques transactions (total, approuvées, refusées, volume)
- Liste des comptes clients avec soldes
- Mesures de sécurité actives
- Historique complet des transactions

**Code clé : Affichage des Comptes**

```javascript
fetch('/api/soldes')
    .then(response => response.json())
    .then(soldes => {
        const container = document.getElementById('comptes-container');
        container.innerHTML = '';
        
        for (const [nom, info] of Object.entries(soldes)) {
            const compteHtml = `
                <div class="compte-card">
                    <div>
                        <h6><i class="bi bi-person-circle"></i> ${nom}</h6>
                        <small><i class="bi bi-credit-card"></i> ${info.carte_masquee}</small>
                    </div>
                    <div>
                        <div class="text-muted small">Solde</div>
                        <h4 class="text-primary">${info.solde}€</h4>
                    </div>
                </div>
            `;
            container.innerHTML += compteHtml;
        }
    });
```

### 6. Gestion Certificats (`certificats.html`)

**URL** : `http://localhost:5001/certificats`

**Contenu** :
- Statistiques certificats (total, valides, révoqués)
- Formulaire de création de nouveau client
- Liste de tous les certificats
- Modal avec détails complets d'un certificat
- Bouton de révocation

**Code clé : Affichage des Certificats**

```javascript
fetch('/api/certificats')
    .then(response => response.json())
    .then(certs => {
        const tbody = document.getElementById('certs-tbody');
        tbody.innerHTML = '';
        
        certs.forEach(cert => {
            const expiration = new Date(cert.date_expiration);
            const isExpired = expiration < new Date();
            
            // Badge de statut
            let statusBadge = '';
            if (cert.revoque) {
                statusBadge = '<span class="badge bg-danger">❌ Révoqué</span>';
            } else if (isExpired) {
                statusBadge = '<span class="badge bg-warning">⚠️ Expiré</span>';
            } else if (cert.valide) {
                statusBadge = '<span class="badge bg-success">✓ Valide</span>';
            }
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${cert.sujet}</strong></td>
                <td><code>${cert.numero_serie.substring(0, 13)}...</code></td>
                <td>${cert.emetteur}</td>
                <td>${expiration.toLocaleDateString('fr-FR')}</td>
                <td>${statusBadge}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewCert('${cert.numero_serie}')">
                        <i class="bi bi-eye"></i>
                    </button>
                    ${!cert.revoque ? `
                    <button class="btn btn-sm btn-outline-danger" onclick="revokeCert('${cert.numero_serie}')">
                        <i class="bi bi-x-circle"></i>
                    </button>
                    ` : ''}
                </td>
            `;
            tbody.appendChild(tr);
        });
    });
```

**Code clé : Révocation d'un Certificat**

```javascript
window.revokeCert = function(numeroSerie) {
    if (!confirm('Êtes-vous sûr de vouloir révoquer ce certificat ?')) return;
    
    fetch('/api/revoquer_certificat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ numero_serie: numeroSerie })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('✅ Certificat révoqué', 'success');
            loadCertificats();  // Recharger la liste
        } else {
            showToast('❌ Erreur : ' + data.message, 'danger');
        }
    });
};
```

---

## 🎨 Design et Interface

### Bootstrap 5

**Bootstrap** est un framework CSS qui fournit :
- Grille responsive (système de colonnes)
- Composants prêts à l'emploi (boutons, cartes, modals, etc.)
- Utilitaires CSS (marges, couleurs, etc.)

#### Système de Grille

```html
<div class="container">
    <div class="row">
        <div class="col-md-6">Colonne 1 (50%)</div>
        <div class="col-md-6">Colonne 2 (50%)</div>
    </div>
</div>
```

- `container` : Conteneur avec marges
- `row` : Ligne
- `col-md-6` : Colonne de 6/12 (50%) sur écrans moyens et plus

#### Composants

**Carte (Card)** :
```html
<div class="card">
    <div class="card-header">Titre</div>
    <div class="card-body">Contenu</div>
</div>
```

**Bouton** :
```html
<button class="btn btn-primary">Bouton Primaire</button>
<button class="btn btn-success">Bouton Succès</button>
<button class="btn btn-danger">Bouton Danger</button>
```

**Badge** :
```html
<span class="badge bg-success">✓ Valide</span>
<span class="badge bg-danger">❌ Révoqué</span>
```

### CSS Personnalisé

Dans `base.html`, on a ajouté du CSS personnalisé :

```css
:root {
    --primary: #6366f1;
    --success: #10b981;
    --danger: #ef4444;
}

body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.card {
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    transition: all 0.3s;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
}
```

**Explication** :
- `:root` : Variables CSS réutilisables
- `linear-gradient` : Dégradé de couleurs
- `box-shadow` : Ombre portée
- `transition` : Animation fluide
- `transform: translateY(-5px)` : Lever la carte de 5px au survol

### Animations

```css
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.log-item {
    animation: slideIn 0.5s ease-out;
}
```

**Résultat** : Quand un nouveau log apparaît, il glisse de la gauche avec un effet de fondu.

---

## 🔄 Flux de Données

### Exemple : Achat d'un Livre

#### 1. L'utilisateur remplit le formulaire

```
Interface Web (client.html)
↓
Client sélectionne "Alice"
Marchand sélectionne "Amazon"
Articles: "Livre Python"
Montant: 45€
↓
Clic sur "Effectuer l'Achat Sécurisé"
```

#### 2. JavaScript envoie la requête

```javascript
fetch('/api/acheter', {
    method: 'POST',
    body: JSON.stringify({
        client: 'Alice',
        marchand: 'Amazon',
        items: ['Livre Python'],
        montant: 45
    })
})
```

**Format envoyé** : JSON
```json
{
  "client": "Alice",
  "marchand": "Amazon",
  "items": ["Livre Python"],
  "montant": 45
}
```

#### 3. Flask reçoit la requête

```python
@app.route('/api/acheter', methods=['POST'])
def api_acheter():
    data = request.json
    client_nom = data['client']  # "Alice"
    marchand_nom = data['marchand']  # "Amazon"
    # ...
```

#### 4. Flask appelle la logique métier

```python
client = clients['Alice']
marchand = marchands['Amazon']

succes, message = client.acheter(marchand, items, montant)
```

**Ici, on bascule dans `projet.py`** :
- Génération transaction ID
- Chiffrement PI
- Signature
- Envoi au marchand
- Vérifications
- Autorisation banque
- Génération ARQC

#### 5. Flask retourne la réponse

```python
return jsonify({
    'success': True,
    'message': 'Commande validée (ARQC: a3f2d9e1...)',
    'nouveau_solde': 4955
})
```

**Format renvoyé** : JSON
```json
{
  "success": true,
  "message": "Commande validée (ARQC: a3f2d9e1...)",
  "nouveau_solde": 4955
}
```

#### 6. JavaScript traite la réponse

```javascript
.then(data => {
    if (data.success) {
        showToast('✅ Transaction réussie !', 'success');
        // Mettre à jour le solde affiché
    }
})
```

#### 7. WebSocket diffuse l'événement

```python
log_event('transaction', 'Alice', 'Achat réussi', {...})
↓
socketio.emit('nouveau_log', log_entry)
```

#### 8. Tous les clients reçoivent l'événement

```javascript
socket.on('nouveau_log', function(log) {
    // Dashboard se met à jour automatiquement
    // Nouveau log apparaît en temps réel
})
```

### Diagramme Complet

```
┌─────────────────┐
│   NAVIGATEUR    │
│   (Frontend)    │
└────────┬────────┘
         │
         │ 1. POST /api/acheter
         │    {"client": "Alice", ...}
         │
         ▼
┌─────────────────┐
│   FLASK (app.py)│
│                 │
│  @app.route()   │
│  def api_acheter│
└────────┬────────┘
         │
         │ 2. client.acheter()
         │
         ▼
┌─────────────────┐
│  PROJET.PY      │
│                 │
│  Logique SET    │
│  - Chiffrement  │
│  - Signature    │
│  - Vérifications│
└────────┬────────┘
         │
         │ 3. Retour (succes, message)
         │
         ▼
┌─────────────────┐
│   FLASK         │
│                 │
│  jsonify(...)   │
│  emit(...)      │ ─────► WebSocket ────► Tous les clients
└────────┬────────┘
         │
         │ 4. JSON Response
         │
         ▼
┌─────────────────┐
│   NAVIGATEUR    │
│                 │
│  Affiche résultat│
└─────────────────┘
```

---

## ❓ Questions que Votre Prof Peut Poser

### Q1 : Quelle est la différence entre une requête GET et POST ?

**Réponse** :
- **GET** : Récupérer des données (lecture seule)
  - Ex: `/dashboard` affiche la page
  - Pas de modification de données
  
- **POST** : Envoyer des données pour créer/modifier
  - Ex: `/api/acheter` crée une transaction
  - Peut modifier la base de données

### Q2 : C'est quoi un WebSocket et pourquoi c'est mieux qu'AJAX ?

**Réponse** :
- **AJAX** : Le client demande régulièrement (polling)
  - Coûteux (beaucoup de requêtes)
  - Pas vraiment "temps réel"

- **WebSocket** : Canal bidirectionnel permanent
  - Le serveur pousse les données dès qu'elles arrivent
  - Vraiment temps réel
  - Plus efficace

### Q3 : Comment fonctionne le système de templates ?

**Réponse** :
1. Template de base (`base.html`) définit la structure commune
2. Templates enfants (`dashboard.html`, etc.) héritent de la base
3. On insère des variables avec `{{ variable }}`
4. Jinja2 remplace les variables par leurs valeurs
5. Le HTML final est envoyé au navigateur

### Q4 : Pourquoi utiliser des API REST plutôt que des formulaires classiques ?

**Réponse** :
- **Formulaires classiques** : Rechargent toute la page
- **API REST** :
  - Pas de rechargement (meilleure UX)
  - Format JSON (plus moderne)
  - Permet des applications SPA (Single Page Application)
  - Plus flexible (peut être utilisé par mobile, etc.)

### Q5 : Comment Chart.js dessine les graphiques ?

**Réponse** :
1. On crée un élément `<canvas>` dans le HTML
2. JavaScript récupère cet élément
3. On donne les données à Chart.js (labels + valeurs)
4. Chart.js calcule les coordonnées
5. Il dessine sur le canvas avec l'API Canvas HTML5

### Q6 : C'est quoi Bootstrap et pourquoi l'utiliser ?

**Réponse** :
- Framework CSS qui fournit des composants prêts à l'emploi
- **Avantages** :
  - Gain de temps (pas besoin de tout coder)
  - Responsive (s'adapte au mobile)
  - Design cohérent
  - Testé et fiable
- **Inconvénient** : Sites qui se ressemblent (mais personnalisable)

---

## ✅ Checklist de Compréhension

Avant de présenter à votre prof, vérifiez que vous pouvez expliquer :

- [ ] La différence entre frontend et backend
- [ ] Comment fonctionne une route Flask
- [ ] Ce qu'est un template et comment il fonctionne
- [ ] La différence entre GET et POST
- [ ] Comment fonctionne WebSocket
- [ ] Le flux complet d'une transaction (du clic au résultat)
- [ ] Comment Chart.js affiche les graphiques
- [ ] Le rôle de Bootstrap dans le design
- [ ] Comment JavaScript communique avec Flask (fetch)
- [ ] Pourquoi on utilise JSON pour échanger des données

---

**Bonne présentation ! 🚀**
