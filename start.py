#!/usr/bin/env python3
"""
Script de démarrage rapide pour la simulation SET/CDA
Lance l'interface web Flask
"""

import sys
import os

try:
    from flask import Flask
    from flask_socketio import SocketIO
    from Crypto.PublicKey import RSA
except ImportError as e:
    print("\n❌ Erreur : Dépendances manquantes !")
    print(f"   {e}")
    print("\n💡 Solution : Installez les dépendances avec :")
    print("   pip install -r requirements.txt\n")
    sys.exit(1)

print("\n" + "="*70)
print("🔐 SIMULATION PROTOCOLE SET/CDA")
print("="*70)
print("\n📦 Vérification des dépendances...")
print("   ✅ Flask installé")
print("   ✅ Flask-SocketIO installé")
print("   ✅ PyCryptodome installé")

print("\n🚀 Démarrage de l'application...")
print("-"*70)

from app import app, socketio, init_system

init_system()

print("\n✅ Système initialisé avec succès !")
print("\n" + "="*70)
print("🌐 INTERFACE WEB DISPONIBLE")
print("="*70)
print("\n📱 Accédez à l'application sur :")
print("   👉 http://localhost:5001")
print("   👉 http://127.0.0.1:5001")
print("\n📋 Pages disponibles :")
print("   • Dashboard      : http://localhost:5001/dashboard")
print("   • Client         : http://localhost:5001/client")
print("   • Marchand       : http://localhost:5001/marchand")
print("   • Banque         : http://localhost:5001/banque")
print("   • Certificats    : http://localhost:5001/certificats")
print("\n💡 Appuyez sur CTRL+C pour arrêter le serveur")
print("="*70 + "\n")

if __name__ == '__main__':
    try:
        socketio.run(app, debug=True, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du serveur...")
        print("✅ Application fermée proprement\n")
        sys.exit(0)
