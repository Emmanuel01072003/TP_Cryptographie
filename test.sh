#!/bin/bash
# Script de test automatique pour vérifier l'installation

echo "======================================================================"
echo "🧪 TESTS AUTOMATIQUES - PROTOCOLE SET/CDA"
echo "======================================================================"
echo ""

# Test 1: Vérifier Python
echo "📌 Test 1: Vérification de Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ $PYTHON_VERSION installé"
else
    echo "   ❌ Python 3 non trouvé"
    exit 1
fi

# Test 2: Vérifier les dépendances
echo ""
echo "📌 Test 2: Vérification des dépendances Python..."

dependencies=("Flask" "flask-socketio" "pycryptodome")
all_installed=true

for dep in "${dependencies[@]}"; do
    if python3 -c "import ${dep,,}" 2>/dev/null; then
        echo "   ✅ $dep installé"
    else
        echo "   ❌ $dep manquant"
        all_installed=false
    fi
done

if [ "$all_installed" = false ]; then
    echo ""
    echo "💡 Installez les dépendances manquantes avec:"
    echo "   pip3 install -r requirements.txt"
    exit 1
fi

# Test 3: Vérifier les fichiers
echo ""
echo "📌 Test 3: Vérification des fichiers du projet..."

files=("projet.py" "app.py" "start.py" "requirements.txt" "templates/base.html")
all_files_exist=true

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file trouvé"
    else
        echo "   ❌ $file manquant"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    echo ""
    echo "❌ Certains fichiers sont manquants. Vérifiez l'installation."
    exit 1
fi

# Test 4: Exécuter la simulation
echo ""
echo "📌 Test 4: Exécution de la simulation SET/CDA..."
if python3 projet.py > /dev/null 2>&1; then
    echo "   ✅ Simulation exécutée sans erreur"
else
    echo "   ❌ Erreur lors de l'exécution"
    exit 1
fi

# Résumé
echo ""
echo "======================================================================"
echo "✅ TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS !"
echo "======================================================================"
echo ""
echo "🚀 Vous pouvez maintenant lancer l'application avec :"
echo "   python3 start.py"
echo ""
echo "   OU"
echo ""
echo "   python3 app.py"
echo ""
echo "Puis ouvrez : http://localhost:5000"
echo ""
