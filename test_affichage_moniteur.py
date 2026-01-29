#!/usr/bin/env python3
"""
Test simple pour vérifier que le moniteur affiche les processus
"""
import time
import requests

BASE_URL = "http://localhost:5001"

print("\n" + "="*70)
print("🧪 TEST D'AFFICHAGE DU MONITEUR TECHNIQUE")
print("="*70 + "\n")

# Vérifier que le serveur est actif
print("1️⃣ Vérification du serveur...")
try:
    r = requests.get(f"{BASE_URL}/", timeout=5)
    if r.status_code == 200:
        print("   ✅ Serveur actif sur http://localhost:5001")
    else:
        print(f"   ❌ Serveur répond avec code {r.status_code}")
        exit(1)
except requests.exceptions.ConnectionError:
    print("   ❌ Serveur non accessible")
    print("   💡 Lancez d'abord : python start.py")
    exit(1)

print("\n2️⃣ Vérification de la page /processus...")
try:
    r = requests.get(f"{BASE_URL}/processus", timeout=5)
    if r.status_code == 200:
        print("   ✅ Page /processus accessible")
    else:
        print(f"   ❌ Erreur {r.status_code}")
        exit(1)
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    exit(1)

print("\n3️⃣ Déclenchement d'un achat test...")
achat = {
    'client': 'Alice',
    'marchand': 'Amazon',
    'items': ['Test Moniteur Debug'],
    'montant': 25
}

try:
    r = requests.post(
        f"{BASE_URL}/api/acheter",
        json=achat,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    if r.status_code == 200:
        result = r.json()
        if result['success']:
            print(f"   ✅ Achat réussi : {result['message']}")
            print(f"   💰 Nouveau solde : {result['nouveau_solde']}€")
        else:
            print(f"   ⚠️  Achat refusé : {result['message']}")
    else:
        print(f"   ❌ Erreur HTTP {r.status_code}")
        print(f"   Réponse : {r.text}")
        exit(1)
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    exit(1)

print("\n" + "="*70)
print("📋 RÉSULTAT DU TEST")
print("="*70)

print("\n✅ Backend opérationnel !\n")

print("🔍 VÉRIFICATIONS À FAIRE MAINTENANT :\n")

print("A. Dans le TERMINAL où tourne le serveur :")
print("   Vous DEVEZ voir des blocs comme celui-ci :")
print("   " + "="*60)
print("   [MONITOR] Préparation processus technique")
print("     Titre: 💳 Achat de Alice chez Amazon - 25€")
print("     Type: transaction")
print("     Status: info")
print("     Nombre d'étapes: 5")
print("   [MONITOR] 📡 Émission WebSocket 'technical_process'...")
print("   [MONITOR] ✅ Événement émis avec succès")
print("   " + "="*60)
print()

print("B. Sur http://localhost:5001/processus avec F12 ouvert :")
print("   Dans l'onglet Console, vous DEVEZ voir :")
print("   📨 Processus technique reçu: {...}")
print("   ✅ Affichage du processus")
print("   🎨 Début affichage processus: 💳 Achat de Alice...")
print("   📊 Données du processus: {...}")
print("   📦 État du logDiv AVANT: {...}")
print("   🗑️ Suppression du message initial \"En attente\"")
print("   🆕 Création de l'entrée: process-1")
print("   📝 HTML généré, taille: ... caractères")
print("   ✅ Entrée insérée AVANT le premier enfant")
print("   ✅ displayProcess terminé. Total entrées: 1")
print()

print("C. Sur la page /processus (partie visible) :")
print("   Vous DEVEZ voir une grande carte avec :")
print("   - Le titre : 💳 Achat de Alice chez Amazon - 25€")
print("   - Les 5 étapes (Génération ID, OI, PI, Chiffrement, Signature)")
print("   - Des sections pliables (Clés, Données chiffrées, etc.)")
print()

print("="*70)
print("🎯 INSTRUCTIONS DÉTAILLÉES :")
print("="*70)
print()
print("1. Ouvrez http://localhost:5001/processus")
print("2. Appuyez sur F12 pour ouvrir la console")
print("3. Allez dans l'onglet 'Console'")
print("4. Rafraîchissez la page (F5)")
print("5. Vérifiez que vous voyez 'Connecté au moniteur technique'")
print("6. Dans un autre onglet, allez sur http://localhost:5001/client")
print("7. Faites un achat (Alice -> Amazon, 50€)")
print("8. Retournez sur /processus")
print("9. Vérifiez la console ET la page")
print()
print("📖 Pour plus de détails : TEST_MONITEUR_DEBUG.md")
print()
print("="*70 + "\n")
