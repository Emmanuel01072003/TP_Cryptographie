#!/usr/bin/env python3
"""
Script de test pour vérifier le moniteur technique
"""

import requests
import time
import json

BASE_URL = "http://localhost:5001"

print("🧪 Test du Moniteur Technique\n")

# 1. Vérifier que le serveur est lancé
print("1. Vérification du serveur...")
try:
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        print("   ✅ Serveur actif")
    else:
        print(f"   ❌ Serveur répond avec code {response.status_code}")
        exit(1)
except requests.exceptions.ConnectionError:
    print("   ❌ Serveur non accessible. Lancez d'abord: python start.py")
    exit(1)

# 2. Vérifier que la page processus existe
print("\n2. Vérification de la page /processus...")
try:
    response = requests.get(f"{BASE_URL}/processus")
    if response.status_code == 200:
        print("   ✅ Page /processus accessible")
    else:
        print(f"   ❌ Erreur {response.status_code}")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 3. Effectuer un achat de test
print("\n3. Test d'achat (Alice chez Amazon)...")
try:
    achat_data = {
        'client': 'Alice',
        'marchand': 'Amazon',
        'items': ['Test Moniteur'],
        'montant': 10
    }
    
    response = requests.post(
        f"{BASE_URL}/api/acheter",
        json=achat_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print(f"   ✅ Achat réussi: {result['message']}")
            print(f"   💰 Nouveau solde: {result['nouveau_solde']}€")
        else:
            print(f"   ⚠️  Achat refusé: {result['message']}")
    else:
        print(f"   ❌ Erreur HTTP {response.status_code}")
        print(f"   Réponse: {response.text}")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print("\n" + "="*60)
print("📊 RÉSULTAT DU TEST")
print("="*60)
print("\n✅ Si vous voyez ce message, le backend fonctionne !")
print("\n📋 Instructions pour voir les détails techniques:")
print("   1. Ouvrez votre navigateur sur: http://localhost:5001/processus")
print("   2. Ouvrez la console (F12) → onglet Console")
print("   3. Faites un achat depuis /client")
print("   4. Regardez la console ET le moniteur")
print("\n🔍 Dans la console, vous devriez voir:")
print("   📨 Processus technique reçu: {...")
print("   ✅ Affichage du processus")
print("   🎨 Début affichage processus: ...")
print("\n💡 Si vous ne voyez rien:")
print("   - Vérifiez que le WebSocket est connecté")
print("   - Regardez les logs du serveur (terminal)")
print("   - Rafraîchissez la page /processus (F5)")
print("\n" + "="*60)
