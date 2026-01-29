# 💰 GUIDE D'UTILISATION - Système de Rechargement de Compte

## 🎯 Fonctionnalité Ajoutée

Un **système de rechargement de compte** a été ajouté pour permettre aux clients de recharger leur solde lorsqu'il devient faible ou nul.

---

## 📋 Table des Matières

1. [Utilisation via l'Interface Web](#utilisation-via-linterface-web)
2. [Utilisation en Ligne de Commande](#utilisation-en-ligne-de-commande)
3. [Règles et Limitations](#règles-et-limitations)
4. [Code Ajouté](#code-ajouté)
5. [Questions Fréquentes](#questions-fréquentes)

---

## 🌐 Utilisation via l'Interface Web

### Étapes pour Recharger un Compte

1. **Accédez à la page Client**
   - Ouvrez votre navigateur sur : `http://localhost:5001/client`

2. **Localisez la carte "Recharger mon Compte"**
   - Elle se trouve dans la colonne de droite, sous "Informations"

3. **Remplissez le formulaire**
   - **Client** : Sélectionnez le client dont vous voulez recharger le compte
   - **Montant à Recharger** : Entrez le montant (entre 1€ et 10 000€)
   - Le **solde actuel** s'affiche automatiquement

4. **Cliquez sur "Recharger le Compte"**
   - Une notification verte apparaît si le rechargement réussit
   - Le solde est mis à jour instantanément

### Exemple Visuel

```
┌─────────────────────────────────┐
│ 💰 Recharger mon Compte         │
├─────────────────────────────────┤
│                                 │
│ Client: [Alice ▼]               │
│                                 │
│ Montant à Recharger (€): 500   │
│ Maximum: 10 000€                │
│                                 │
│ Solde Actuel: 100€              │
│                                 │
│ [💰 Recharger le Compte]        │
└─────────────────────────────────┘
```

---

## 💻 Utilisation en Ligne de Commande

### Via Python

```python
from projet import *

# Initialiser le système
ca = AutoriteCertification()
banque = Banque(ca)
alice = Client("Alice", "4970-1111-2222-3333", ca)

# Vérifier le solde actuel
print(f"Solde actuel: {banque.get_solde(alice.carte)}€")
# → Solde actuel: 5000€

# Recharger le compte
succes, message = banque.recharger_compte(alice.carte, 1000)
print(message)
# → Compte rechargé de 1000€. Nouveau solde: 6000€

# Vérifier le nouveau solde
print(f"Nouveau solde: {banque.get_solde(alice.carte)}€")
# → Nouveau solde: 6000€
```

### Via l'API REST

```bash
# Recharger le compte d'Alice avec 500€
curl -X POST http://localhost:5001/api/recharger_compte \
  -H "Content-Type: application/json" \
  -d '{
    "client": "Alice",
    "montant": 500
  }'
```

**Réponse JSON** :
```json
{
  "success": true,
  "message": "Compte rechargé de 500€. Nouveau solde: 5500€",
  "nouveau_solde": 5500
}
```

---

## 📏 Règles et Limitations

### Règles de Validation

| Règle | Détail |
|-------|--------|
| **Montant minimum** | 1€ |
| **Montant maximum** | 10 000€ par rechargement |
| **Client** | Doit exister dans le système |
| **Carte** | Doit être valide et connue |

### Messages d'Erreur

| Erreur | Message | Solution |
|--------|---------|----------|
| Carte inconnue | `"Carte inconnue"` | Vérifier le numéro de carte |
| Montant négatif ou nul | `"Le montant doit être positif"` | Entrer un montant > 0€ |
| Montant trop élevé | `"Montant maximum de rechargement: 10000€"` | Faire plusieurs rechargements |
| Client inconnu | `"Client inconnu"` | Créer le client d'abord |

### Exemples de Validation

```python
# ✅ VALIDE
banque.recharger_compte("4970-1111-2222-3333", 500)
# → Compte rechargé de 500€

# ❌ INVALIDE - Montant négatif
banque.recharger_compte("4970-1111-2222-3333", -100)
# → Le montant doit être positif

# ❌ INVALIDE - Montant trop élevé
banque.recharger_compte("4970-1111-2222-3333", 15000)
# → Montant maximum de rechargement: 10000€

# ❌ INVALIDE - Carte inconnue
banque.recharger_compte("9999-9999-9999-9999", 100)
# → Carte inconnue
```

---

## 🔧 Code Ajouté

### 1. Méthode dans la Classe Banque (`projet.py`)

```python
def recharger_compte(self, carte: str, montant: float) -> Tuple[bool, str]:
    """
    Recharge un compte bancaire.
    
    Args:
        carte (str): Numéro de carte bancaire
        montant (float): Montant à ajouter au solde
    
    Returns:
        Tuple[bool, str]: (succès, message)
    """
    # Vérifier que la carte existe
    if carte not in self.comptes:
        return False, "Carte inconnue"
    
    # Vérifier que le montant est positif
    if montant <= 0:
        return False, "Le montant doit être positif"
    
    # Vérifier la limite maximale (sécurité)
    if montant > 10000:
        return False, "Montant maximum de rechargement: 10000€"
    
    # Ajouter le montant au solde
    self.comptes[carte]['solde'] += montant
    
    print(f"[Banque] ✅ Compte {carte} rechargé de {montant}€")
    print(f"[Banque] Nouveau solde: {self.comptes[carte]['solde']}€")
    
    return True, f"Compte rechargé de {montant}€. Nouveau solde: {self.comptes[carte]['solde']}€"
```

### 2. Route API Flask (`app.py`)

```python
@app.route('/api/recharger_compte', methods=['POST'])
def api_recharger_compte():
    """
    API REST pour recharger un compte.
    
    Requête POST JSON:
        {
            "client": "Alice",
            "montant": 500
        }
    
    Réponse JSON:
        {
            "success": true,
            "message": "Compte rechargé de 500€. Nouveau solde: 5500€",
            "nouveau_solde": 5500
        }
    """
    try:
        data = request.json
        client_nom = data['client']
        montant = float(data['montant'])
        
        # Vérifier que le client existe
        if client_nom not in clients:
            return jsonify({'success': False, 'message': 'Client inconnu'}), 400
        
        client = clients[client_nom]
        
        # Appeler la méthode de rechargement
        succes, message = banque.recharger_compte(client.carte, montant)
        
        # Logger l'événement si succès
        if succes:
            log_event('system', 'Banque', f'Compte rechargé pour {client_nom}', {
                'montant': montant,
                'nouveau_solde': banque.get_solde(client.carte)
            })
        
        # Retourner la réponse
        return jsonify({
            'success': succes,
            'message': message,
            'nouveau_solde': banque.get_solde(client.carte)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
```

### 3. Interface HTML (`templates/client.html`)

Une nouvelle carte a été ajoutée dans la page client avec :
- Un formulaire de rechargement
- Sélection du client
- Input pour le montant (1€ - 10 000€)
- Affichage du solde actuel
- Bouton de rechargement

---

## ❓ Questions Fréquentes

### Q1 : Pourquoi y a-t-il une limite de 10 000€ ?

**Réponse** : Pour des raisons de sécurité, on limite les rechargements à 10 000€ par opération. C'est une protection contre :
- Les erreurs de saisie (ex: oublier une virgule → 100000 au lieu de 1000,00)
- Les tentatives de blanchiment d'argent
- Les bugs qui pourraient créditer des montants énormes

**Solution** : Pour recharger plus, faites plusieurs opérations.

### Q2 : Le rechargement est-il sécurisé ?

**Réponse** : Oui, le rechargement passe par :
1. Validation du client
2. Validation du montant
3. Logs système
4. Mise à jour atomique du solde

Dans un système réel, il faudrait aussi :
- Authentification du client (mot de passe, 2FA)
- Vérification de l'origine des fonds
- Traçabilité bancaire complète

### Q3 : Peut-on recharger le compte de quelqu'un d'autre ?

**Réponse** : Oui, dans cette simulation. N'importe qui peut recharger n'importe quel compte (comme un virement bancaire).

Dans un système réel :
- Seul le propriétaire du compte pourrait recharger
- Ou il faudrait une autorisation explicite
- Avec authentification forte (carte + PIN)

### Q4 : Les rechargements sont-ils tracés ?

**Réponse** : Oui, chaque rechargement :
- Génère un log système
- Est visible dans le Dashboard (si WebSocket actif)
- Peut être consulté dans `/api/logs`

**Exemple de log** :
```json
{
  "timestamp": "2026-01-22T15:30:45",
  "type": "system",
  "actor": "Banque",
  "message": "Compte rechargé pour Alice",
  "details": {
    "montant": 500,
    "nouveau_solde": 5500
  }
}
```

### Q5 : Que se passe-t-il si le solde est déjà élevé ?

**Réponse** : Le rechargement s'ajoute au solde existant. Il n'y a pas de limite maximale de solde total.

**Exemple** :
- Solde actuel : 50 000€
- Rechargement : 5 000€
- Nouveau solde : 55 000€

---

## 🎯 Scénarios d'Utilisation

### Scénario 1 : Client avec Solde Faible

**Situation** : Bob a 100€ et veut acheter pour 200€

```python
# 1. Vérifier le solde de Bob
print(banque.get_solde("4970-4444-5555-6666"))  # → 100€

# 2. Tenter un achat de 200€
bob.acheter(amazon, ["Casque Audio"], 200)
# → ❌ Transaction refusée: Fonds insuffisants

# 3. Recharger le compte
banque.recharger_compte("4970-4444-5555-6666", 150)
# → ✅ Compte rechargé de 150€. Nouveau solde: 250€

# 4. Réessayer l'achat
bob.acheter(amazon, ["Casque Audio"], 200)
# → ✅ Transaction réussie !
```

### Scénario 2 : Rechargement via l'Interface Web

**Étapes utilisateur** :

1. Alice voit son solde : 50€
2. Elle veut acheter pour 100€
3. Elle clique sur "Recharger mon Compte"
4. Elle sélectionne "Alice"
5. Elle entre 100€
6. Elle clique sur "Recharger le Compte"
7. Notification verte : "✅ Compte rechargé de 100€. Nouveau solde: 150€"
8. Son solde est maintenant 150€
9. Elle peut faire son achat !

### Scénario 3 : Rechargement Préventif

**Situation** : Charlie veut s'assurer d'avoir assez pour plusieurs achats

```python
# Solde initial
print(banque.get_solde("4970-7777-8888-9999"))  # → 50000€

# Rechargement préventif de 5000€
banque.recharger_compte("4970-7777-8888-9999", 5000)
# → Nouveau solde: 55000€

# Maintenant Charlie peut faire plusieurs gros achats sans souci
```

---

## 📊 Statistiques de Rechargement

Tous les rechargements apparaissent dans :

### 1. Dashboard
- Section "Logs Système (Temps Réel)"
- Mise à jour automatique via WebSocket

### 2. API Logs
```bash
curl http://localhost:5001/api/logs
```

### 3. Console Serveur
```
[Banque] ✅ Compte 4970-1111-2222-3333 rechargé de 500€
[Banque] Nouveau solde: 5500€
```

---

## ✅ Checklist d'Utilisation

Avant de recharger un compte, vérifiez :

- [ ] Le client existe dans le système
- [ ] Le montant est entre 1€ et 10 000€
- [ ] Vous êtes sur la bonne page (`/client`)
- [ ] L'interface web fonctionne (`python start.py`)

Après le rechargement :

- [ ] Notification de succès affichée
- [ ] Solde mis à jour dans l'interface
- [ ] Log visible dans le Dashboard
- [ ] Possibilité de faire un achat avec le nouveau solde

---

## 🚀 Pour Aller Plus Loin

### Améliorations Possibles

1. **Historique des Rechargements**
   - Créer une liste dédiée dans la classe Banque
   - Afficher l'historique par client

2. **Limites Personnalisées**
   - Limite journalière par client
   - Limite mensuelle

3. **Notifications**
   - Email ou SMS lors d'un rechargement
   - Alerte si le solde est < 50€

4. **Modes de Paiement**
   - Carte bancaire
   - Virement
   - Chèque
   - PayPal

5. **Authentification**
   - Exiger un mot de passe pour recharger
   - Code de confirmation par SMS

---

## 📞 Support

Si vous rencontrez un problème :

1. Vérifiez que le serveur Flask est lancé (`python start.py`)
2. Vérifiez les logs dans la console
3. Testez d'abord en ligne de commande Python
4. Consultez `/api/logs` pour voir les erreurs

---

**Le système de rechargement est maintenant opérationnel ! 💰**
