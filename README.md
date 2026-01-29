# 🔐 Simulation Protocole SET/CDA

## Démarrage Rapide

### Option 1 : Lancer l'interface web

```bash
python start.py
```

Puis ouvrez votre navigateur sur : **http://localhost:5001**

### Option 2 : Lancer la simulation en ligne de commande

```bash
python projet.py
```

### Option 3 : Lancer l'application Flask directement

```bash
python app.py
```

## Installation des dépendances

Si vous rencontrez des erreurs, installez d'abord les dépendances :

```bash
pip install -r requirements.txt
```

## Structure du Projet

```
TP_Cyber/
├── projet.py              # Code métier du protocole SET/CDA
├── app.py                 # Application Flask
├── start.py               # Script de démarrage rapide
├── requirements.txt       # Dépendances Python
├── DOCUMENTATION.md       # Documentation complète
├── README.md              # Ce fichier
└── templates/             # Templates HTML
    ├── base.html
    ├── index.html
    ├── dashboard.html
    ├── client.html
    ├── marchand.html
    ├── banque.html
    └── certificats.html
```

## Fonctionnalités

✅ **Autorité de Certification** - Gestion des certificats X.509  
✅ **Chiffrement RSA 2048 bits** - Sécurité maximale  
✅ **Double Signature** - Intégrité et authentification  
✅ **Protection Anti-Rejeu** - Nonces et timestamps  
✅ **ARQC Generation** - Cryptogrammes d'application  
✅ **Interface Web Moderne** - Dashboard temps réel  
✅ **WebSockets** - Logs en direct  
✅ **Tests de Sécurité** - Scénarios d'attaque  

## Documentation

Pour plus de détails, consultez **DOCUMENTATION.md**

## Clients Pré-configurés

- **Alice** : Carte 4970-1111-2222-3333, Solde 5000€
- **Bob** : Carte 4970-4444-5555-6666, Solde 100€
- **Charlie** : Carte 4970-7777-8888-9999, Solde 50000€

## Marchands Disponibles

- Amazon
- FNAC
- Darty

## Support

En cas de problème, vérifiez :
1. Python 3.8+ installé : `python --version`
2. Dépendances installées : `pip list | grep -E "Flask|pycryptodome"`
3. Port 5001 disponible (si port 5000 occupé par AirPlay sur macOS)

---

**Bon test ! 🚀**
