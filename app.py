from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from projet import *
import threading
import secrets
from datetime import datetime
import json as json_lib

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
socketio = SocketIO(app, cors_allowed_origins="*")

ca = None
banque = None
marchands = {}
clients = {}
logs_globaux = []
logs_securite = []  # Nouveau : logs des tentatives d'attaque

def log_technical_process(title, process_type, steps=None, crypto=None, result=None, status='info'):
    """Enregistrer un processus technique détaillé pour le moniteur"""
    import base64
    
    print(f"\n{'='*60}")
    print(f"[MONITOR] Préparation processus technique")
    print(f"  Titre: {title}")
    print(f"  Type: {process_type}")
    print(f"  Status: {status}")
    print(f"  Nombre d'étapes: {len(steps) if steps else 0}")
    print(f"  Crypto présent: {'Oui' if crypto else 'Non'}")
    print(f"  Résultat présent: {'Oui' if result else 'Non'}")
    
    technical_log = {
        'timestamp': datetime.now().isoformat(),
        'title': title,
        'type': process_type,
        'status': status,
        'steps': steps or [],
        'crypto': crypto or {},
        'result': result
    }
    
    # Convertir les bytes en hex pour l'affichage
    if crypto:
        if 'keys' in crypto:
            for key_name, key_value in crypto['keys'].items():
                if isinstance(key_value, bytes):
                    crypto['keys'][key_name] = key_value.hex()
        if 'encrypted' in crypto and isinstance(crypto['encrypted'], bytes):
            crypto['encrypted'] = crypto['encrypted'].hex()
        if 'signature' in crypto and isinstance(crypto['signature'], bytes):
            crypto['signature'] = crypto['signature'].hex()
    
    print(f"[MONITOR] 📡 Émission WebSocket 'technical_process'...")
    socketio.emit('technical_process', technical_log)
    print(f"[MONITOR] ✅ Événement émis avec succès")
    print(f"{'='*60}\n")
    
    return technical_log

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

def log_security_event(attack_type, blocked, message, details=None):
    """Enregistrer une tentative d'attaque"""
    security_log = {
        'timestamp': datetime.now().isoformat(),
        'attack_type': attack_type,
        'blocked': blocked,
        'message': message,
        'details': details or {},
        'severity': 'critical' if attack_type in ['usurpation', 'injection'] else 'high' if attack_type in ['modification_montant', 'certificat_revoque'] else 'medium'
    }
    logs_securite.append(security_log)
    socketio.emit('security_alert', security_log)
    
    # Aussi dans les logs globaux
    log_event('security', 'Système de Sécurité', 
              f"🚨 Attaque détectée : {message}", 
              {'attack_type': attack_type, 'blocked': blocked})
    
    return security_log

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

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/client')
def client_interface():
    if not ca:
        init_system()
    return render_template('client.html', clients=clients, marchands=marchands)

@app.route('/marchand')
def marchand_interface():
    if not ca:
        init_system()
    return render_template('marchand.html', marchands=marchands)

@app.route('/banque')
def banque_interface():
    if not ca:
        init_system()
    return render_template('banque.html')

@app.route('/certificats')
def certificats_interface():
    if not ca:
        init_system()
    return render_template('certificats.html')

@app.route('/attaques')
def attaques_interface():
    if not ca:
        init_system()
    # Passer uniquement les noms, pas les objets complets
    return render_template('attaques.html', 
                         clients=list(clients.keys()), 
                         marchands=list(marchands.keys()))

@app.route('/processus')
def processus_technique():
    """Interface de monitoring des processus techniques"""
    if not ca:
        init_system()
    return render_template('processus.html')

@app.route('/api/acheter', methods=['POST'])
def api_acheter():
    try:
        data = request.json
        client_nom = data['client']
        marchand_nom = data['marchand']
        items = data['items']
        montant = float(data['montant'])
        
        if client_nom not in clients:
            return jsonify({'success': False, 'message': 'Client inconnu'}), 400
        
        if marchand_nom not in marchands:
            return jsonify({'success': False, 'message': 'Marchand inconnu'}), 400
        
        client = clients[client_nom]
        marchand = marchands[marchand_nom]
        
        log_event('transaction', client_nom, f'Tentative d\'achat chez {marchand_nom}', {
            'items': items,
            'montant': montant
        })
        
        # NOUVEAU : Acheter avec logging technique détaillé
        succes, message = acheter_avec_details(client, marchand, items, montant)
        
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
        
        return jsonify({
            'success': succes,
            'message': message,
            'nouveau_solde': banque.get_solde(client.carte)
        })
        
    except Exception as e:
        log_event('error', 'Système', f'Erreur lors de l\'achat: {str(e)}')
        return jsonify({'success': False, 'message': str(e)}), 500

def acheter_avec_details(client, marchand, items, montant):
    """Effectuer un achat en loggant tous les détails techniques"""
    import time
    from Crypto.Hash import SHA256
    
    print(f"\n[ACHAT DÉTAILLÉ] Début pour {client.nom} chez {marchand.nom} - {montant}€")
    
    start_time = time.time()
    
    # Étape 1: Génération transaction ID et timestamp
    transaction_id = str(uuid.uuid4())
    timestamp = time.time()
    nonce = get_random_bytes(16).hex()
    
    steps = []
    steps.append({
        'action': 'Génération des identifiants de transaction',
        'details': f'Transaction ID: {transaction_id[:16]}..., Nonce: {nonce[:16]}...',
        'status': 'success',
        'completed': True,
        'duration': int((time.time() - start_time) * 1000)
    })
    
    # Étape 2: Création Order Info (visible par le marchand)
    oi = {
        "items": items,
        "montant": montant,
        "client": client.nom,
        "timestamp": timestamp
    }
    
    steps.append({
        'action': 'Création de l\'Order Info (OI) - Données visibles par le marchand',
        'details': f'Items: {items}, Montant: {montant}€',
        'status': 'success',
        'completed': True,
        'duration': int((time.time() - start_time) * 1000)
    })
    
    # Étape 3: Création Payment Info (chiffré pour la banque)
    pi = {
        "carte": client.carte,
        "montant": montant,
        "nonce": nonce,
        "transaction_id": transaction_id
    }
    
    pi_json = json_lib.dumps(pi)
    
    steps.append({
        'action': 'Création du Payment Info (PI) - Données sensibles',
        'details': f'Carte: {client.carte[:8]}****, Montant: {montant}€',
        'status': 'success',
        'completed': True,
        'duration': int((time.time() - start_time) * 1000)
    })
    
    # Étape 4: Chiffrement RSA du PI pour la banque
    cle_pub_banque = marchand.banque.get_public_key()
    pi_chiffre = client.chiffrer_pour(pi_json.encode(), cle_pub_banque)
    
    steps.append({
        'action': 'Chiffrement RSA 2048 bits du Payment Info',
        'details': f'Données chiffrées: {len(pi_chiffre)} octets. Seule la banque peut déchiffrer',
        'status': 'success',
        'completed': True,
        'duration': int((time.time() - start_time) * 1000)
    })
    
    # Étape 5: Création de la signature
    donnees_combinees = json_lib.dumps(oi, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
    h = SHA256.new(donnees_combinees)
    hash_donnees = h.hexdigest()
    signature = client.signer_donnee(donnees_combinees)
    
    steps.append({
        'action': 'Signature numérique SHA-256 + RSA',
        'details': f'Hash: {hash_donnees[:32]}..., Signature: {len(signature)} octets',
        'status': 'success',
        'completed': True,
        'duration': int((time.time() - start_time) * 1000)
    })
    
    # Créer le paquet complet
    paquet = {
        "order_info": oi,
        "payment_info_enc": pi_chiffre,
        "signature": signature,
        "certificat_client": client.certificat,
        "transaction_id": transaction_id,
        "timestamp": timestamp
    }
    
    # Logger le processus technique complet
    log_technical_process(
        title=f"💳 Achat de {client.nom} chez {marchand.nom} - {montant}€",
        process_type='transaction',
        steps=steps,
        crypto={
            'keys': {
                'Clé Publique Client (RSA 2048)': client.pub_key.export_key().decode()[:200] + '...',
                'Clé Publique Banque (RSA 2048)': cle_pub_banque.export_key().decode()[:200] + '...'
            },
            'plaintext': pi_json,
            'encrypted': pi_chiffre,
            'hash': hash_donnees,
            'signature': signature,
            'certificate': {
                'numero_serie': client.certificat.numero_serie,
                'sujet': client.certificat.sujet,
                'emetteur': client.certificat.emetteur,
                'date_expiration': client.certificat.date_expiration.isoformat()
            }
        },
        status='info'
    )
    
    # Envoyer au marchand
    succes, message = marchand.traiter_commande(paquet)
    
    # Logger le résultat
    log_technical_process(
        title=f"📊 Résultat de la transaction",
        process_type='transaction',
        steps=[{
            'action': 'Réponse du marchand et de la banque',
            'details': message,
            'status': 'success' if succes else 'error',
            'completed': True
        }],
        result={
            'success': succes,
            'message': message
        },
        status='success' if succes else 'error'
    )
    
    return succes, message

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

@app.route('/api/transactions')
def api_transactions():
    if not ca:
        init_system()
    
    trans_data = []
    for trans in banque.historique_transactions:
        trans_copy = trans.copy()
        trans_copy['timestamp'] = datetime.fromtimestamp(trans['timestamp']).isoformat()
        
        # Masquer la carte seulement si ce n'est pas "inconnu"
        if trans['carte'] != 'inconnu' and len(trans['carte']) >= 8:
            trans_copy['carte_masquee'] = trans['carte'][:4] + '-****-****-' + trans['carte'][-4:]
        else:
            trans_copy['carte_masquee'] = trans['carte']
        
        trans_data.append(trans_copy)
    
    return jsonify(trans_data)

@app.route('/api/commandes/<marchand_nom>')
def api_commandes(marchand_nom):
    if not ca:
        init_system()
    
    if marchand_nom not in marchands:
        return jsonify([])
    
    marchand = marchands[marchand_nom]
    commandes_data = []
    
    for cmd in marchand.commandes:
        cmd_copy = cmd.copy()
        cmd_copy['timestamp'] = datetime.fromtimestamp(cmd['timestamp']).isoformat()
        commandes_data.append(cmd_copy)
    
    return jsonify(commandes_data)

@app.route('/api/soldes')
def api_soldes():
    if not ca:
        init_system()
    
    soldes = {}
    for nom, client in clients.items():
        solde = banque.get_solde(client.carte)
        soldes[nom] = {
            'solde': solde,
            'carte': client.carte,
            'carte_masquee': client.carte[:4] + '-****-****-' + client.carte[-4:]
        }
    
    return jsonify(soldes)

@app.route('/api/logs')
def api_logs():
    return jsonify(logs_globaux[-50:])

@app.route('/api/security_logs')
def api_security_logs():
    """Récupérer les logs de sécurité (tentatives d'attaque)"""
    return jsonify(logs_securite[-100:])  # 100 derniers logs de sécurité

@app.route('/api/revoquer_certificat', methods=['POST'])
def api_revoquer_certificat():
    try:
        data = request.json
        numero_serie = data['numero_serie']
        
        ca.revoquer_certificat(numero_serie)
        
        cert = ca.certificats_emis.get(numero_serie)
        if cert:
            log_event('security', 'CA', f'Certificat révoqué: {cert.sujet}', {
                'numero_serie': numero_serie
            })
        
        return jsonify({'success': True, 'message': 'Certificat révoqué'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/recharger_compte', methods=['POST'])
def api_recharger_compte():
    try:
        data = request.json
        client_nom = data['client']
        montant = float(data['montant'])
        
        if client_nom not in clients:
            return jsonify({'success': False, 'message': 'Client inconnu'}), 400
        
        client = clients[client_nom]
        
        succes, message = banque.recharger_compte(client.carte, montant)
        
        if succes:
            log_event('system', 'Banque', f'Compte rechargé pour {client_nom}', {
                'montant': montant,
                'nouveau_solde': banque.get_solde(client.carte)
            })
        
        return jsonify({
            'success': succes,
            'message': message,
            'nouveau_solde': banque.get_solde(client.carte)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/nouveau_client', methods=['POST'])
def api_nouveau_client():
    try:
        data = request.json
        nom = data['nom']
        carte = data['carte']
        solde_initial = float(data.get('solde_initial', 1000))  # Solde par défaut: 1000€
        
        if nom in clients:
            return jsonify({'success': False, 'message': 'Client déjà existant'}), 400
        
        # Vérifier que la carte n'existe pas déjà
        if banque.get_solde(carte) is not None:
            return jsonify({'success': False, 'message': 'Cette carte bancaire est déjà utilisée'}), 400
        
        # Créer le client
        nouveau_client = Client(nom, carte, ca)
        clients[nom] = nouveau_client
        
        # IMPORTANT: Créer le compte bancaire dans la banque
        succes_compte, message_compte = banque.creer_compte(carte, nom, solde_initial)
        
        if not succes_compte:
            # Si échec de création de compte, annuler la création du client
            del clients[nom]
            return jsonify({'success': False, 'message': message_compte}), 500
        
        log_event('system', 'CA', f'Nouveau client créé: {nom}', {
            'carte_masquee': carte[:4] + '-****-****-' + carte[-4:],
            'solde_initial': solde_initial
        })
        
        return jsonify({
            'success': True,
            'message': f'Client {nom} créé avec succès. {message_compte}',
            'certificat': nouveau_client.certificat.numero_serie,
            'solde': solde_initial
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/test_attaque', methods=['POST'])
def api_test_attaque():
    """API pour tester différentes attaques manuellement"""
    try:
        data = request.json
        type_attaque = data['type']
        params = data.get('params', {})
        
        if type_attaque == 'rejeu':
            return test_attaque_rejeu(params)
        elif type_attaque == 'modification_montant':
            return test_attaque_modification_montant(params)
        elif type_attaque == 'usurpation':
            return test_attaque_usurpation(params)
        elif type_attaque == 'certificat_revoque':
            return test_attaque_certificat_revoque(params)
        elif type_attaque == 'timestamp_expire':
            return test_attaque_timestamp_expire(params)
        elif type_attaque == 'fonds_insuffisants':
            return test_attaque_fonds_insuffisants(params)
        elif type_attaque == 'carte_invalide':
            return test_attaque_carte_invalide(params)
        elif type_attaque == 'injection':
            return test_attaque_injection(params)
        else:
            return jsonify({'success': False, 'message': 'Type d\'attaque inconnu'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'error': True}), 500

def test_attaque_rejeu(params):
    """Tester une attaque par rejeu"""
    client_nom = params.get('client')
    marchand_nom = params.get('marchand')
    
    if client_nom not in clients or marchand_nom not in marchands:
        return jsonify({'success': False, 'message': 'Client ou marchand invalide'})
    
    client = clients[client_nom]
    marchand = marchands[marchand_nom]
    
    # Créer une transaction légitime
    transaction_id = str(uuid.uuid4())
    timestamp = time.time()
    
    oi = {"items": ["Test Rejeu"], "montant": 10, "client": client.nom, "timestamp": timestamp}
    pi = {"carte": client.carte, "montant": 10, "nonce": get_random_bytes(16).hex(), "transaction_id": transaction_id}
    
    pi_chiffre = client.chiffrer_pour(json_lib.dumps(pi).encode(), marchands[marchand_nom].banque.get_public_key())
    donnees_combinees = json_lib.dumps(oi, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
    signature = client.signer_donnee(donnees_combinees)
    
    paquet = {
        "order_info": oi,
        "payment_info_enc": pi_chiffre,
        "signature": signature,
        "certificat_client": client.certificat,
        "transaction_id": transaction_id,
        "timestamp": timestamp
    }
    
    # Premier envoi
    succes1, msg1 = marchand.traiter_commande(paquet)
    
    # Deuxième envoi (rejeu)
    succes2, msg2 = marchand.traiter_commande(paquet)
    
    # Enregistrer la tentative d'attaque
    log_security_event(
        'rejeu',
        not succes2,
        f"Tentative de rejeu par {client_nom} chez {marchand_nom}",
        {
            'client': client_nom,
            'marchand': marchand_nom,
            'transaction_id': transaction_id[:16] + '...',
            'premier_envoi': succes1,
            'deuxieme_envoi': succes2
        }
    )
    
    return jsonify({
        'success': True,
        'attaque_bloquee': not succes2,
        'premier_envoi': {'succes': succes1, 'message': msg1},
        'deuxieme_envoi': {'succes': succes2, 'message': msg2},
        'defense': 'Protection anti-rejeu : chaque transaction_id est enregistré',
        'explication': 'Le premier envoi est accepté, le deuxième est refusé car l\'ID existe déjà'
    })

def test_attaque_modification_montant(params):
    """Tester une modification de montant"""
    client_nom = params.get('client')
    marchand_nom = params.get('marchand')
    montant_original = float(params.get('montant_original', 100))
    montant_modifie = float(params.get('montant_modifie', 1))
    
    if client_nom not in clients or marchand_nom not in marchands:
        return jsonify({'success': False, 'message': 'Client ou marchand invalide'})
    
    client = clients[client_nom]
    marchand = marchands[marchand_nom]
    
    transaction_id = str(uuid.uuid4())
    timestamp = time.time()
    
    # OI original
    oi_original = {"items": ["Test Modification"], "montant": montant_original, "client": client.nom, "timestamp": timestamp}
    pi = {"carte": client.carte, "montant": montant_original, "nonce": get_random_bytes(16).hex(), "transaction_id": transaction_id}
    
    pi_chiffre = client.chiffrer_pour(json_lib.dumps(pi).encode(), marchand.banque.get_public_key())
    donnees_combinees_original = json_lib.dumps(oi_original, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
    signature = client.signer_donnee(donnees_combinees_original)
    
    # Calculer le hash original
    from Crypto.Hash import SHA256
    hash_original = SHA256.new(donnees_combinees_original).hexdigest()
    
    # OI modifié
    oi_modifie = {"items": ["Test Modification"], "montant": montant_modifie, "client": client.nom, "timestamp": timestamp}
    donnees_combinees_modifie = json_lib.dumps(oi_modifie, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
    hash_modifie = SHA256.new(donnees_combinees_modifie).hexdigest()
    
    paquet_malveillant = {
        "order_info": oi_modifie,
        "payment_info_enc": pi_chiffre,
        "signature": signature,
        "certificat_client": client.certificat,
        "transaction_id": transaction_id,
        "timestamp": timestamp
    }
    
    # Étapes de vérification
    verification_steps = []
    
    verification_steps.append({
        'step': 1,
        'action': 'Création du paquet légitime avec montant original',
        'status': 'success',
        'details': f"Montant: {montant_original}€, Hash: {hash_original[:16]}..."
    })
    
    verification_steps.append({
        'step': 2,
        'action': 'L\'attaquant modifie le montant dans Order Info',
        'status': 'warning',
        'details': f"Nouveau montant: {montant_modifie}€, Nouveau hash: {hash_modifie[:16]}..."
    })
    
    verification_steps.append({
        'step': 3,
        'action': 'Le marchand vérifie la signature avec les données modifiées',
        'status': 'error',
        'details': f"Hash attendu ≠ Hash reçu → Signature INVALIDE"
    })
    
    succes, msg = marchand.traiter_commande(paquet_malveillant)
    
    verification_steps.append({
        'step': 4,
        'action': 'Décision du marchand',
        'status': 'error' if not succes else 'success',
        'details': msg
    })
    
    # Enregistrer la tentative d'attaque
    log_security_event(
        'modification_montant',
        not succes,
        f"Tentative de modification de montant par {client_nom} : {montant_original}€ → {montant_modifie}€",
        {
            'client': client_nom,
            'marchand': marchand_nom,
            'montant_original': montant_original,
            'montant_modifie': montant_modifie
        }
    )
    
    return jsonify({
        'success': True,
        'attaque_bloquee': not succes,
        'montant_original': montant_original,
        'montant_modifie': montant_modifie,
        'resultat': {'succes': succes, 'message': msg},
        'defense': 'Signature numérique : hash(OI + PI + ID). Si OI change, la signature est invalide',
        'explication': 'La modification du montant invalide la signature cryptographique',
        'verification_steps': verification_steps,
        'technical_details': {
            'transaction_id': transaction_id,
            'hash_original': hash_original,
            'hash_modifie': hash_modifie,
            'hash_different': hash_original != hash_modifie,
            'signature_taille': len(signature),
            'pi_chiffre_taille': len(pi_chiffre)
        },
        'paquet_recu': {
            'order_info_original': oi_original,
            'order_info_modifie': oi_modifie,
            'payment_info': '🔒 Chiffré RSA pour la banque (' + str(len(pi_chiffre)) + ' octets)',
            'difference': f"Montant changé de {montant_original}€ à {montant_modifie}€"
        }
    })

def test_attaque_usurpation(params):
    """Tester une usurpation d'identité"""
    client_cible = params.get('client_cible')
    marchand_nom = params.get('marchand')
    
    if marchand_nom not in marchands:
        return jsonify({'success': False, 'message': 'Marchand invalide'})
    
    marchand = marchands[marchand_nom]
    
    # Obtenir le vrai certificat si le client existe
    vrai_cert_info = None
    if client_cible in clients:
        vrai_cert = clients[client_cible].certificat
        vrai_cert_info = {
            'numero_serie': vrai_cert.numero_serie,
            'sujet': vrai_cert.sujet,
            'emetteur': vrai_cert.emetteur,
            'cle_publique_n': str(vrai_cert.cle_publique.n)[:50] + '...',
            'cle_publique_e': str(vrai_cert.cle_publique.e),
            'date_creation': vrai_cert.date_creation.isoformat(),
            'signature_valide': vrai_cert.verifier_signature(ca.get_public_key())
        }
    
    # L'attaquant génère ses propres clés
    from Crypto.PublicKey import RSA
    from Crypto.Hash import SHA256
    from Crypto.Signature import pkcs1_15
    
    attaquant_key = RSA.generate(2048)
    attaquant_pub = attaquant_key.publickey()
    
    # Faux certificat
    faux_cert = Certificat(
        sujet=client_cible,
        cle_publique=attaquant_pub,
        emetteur="Fausse CA",
        validite_jours=365
    )
    faux_cert.signer(attaquant_key)
    
    faux_cert_info = {
        'numero_serie': faux_cert.numero_serie,
        'sujet': faux_cert.sujet,
        'emetteur': faux_cert.emetteur,
        'cle_publique_n': str(faux_cert.cle_publique.n)[:50] + '...',
        'cle_publique_e': str(faux_cert.cle_publique.e),
        'date_creation': faux_cert.date_creation.isoformat(),
        'signature_valide_ca': faux_cert.verifier_signature(ca.get_public_key()),
        'auto_signe': True
    }
    
    transaction_id = str(uuid.uuid4())
    timestamp = time.time()
    
    oi = {"items": ["Test Usurpation"], "montant": 100, "client": client_cible, "timestamp": timestamp}
    pi = {"carte": "4970-9999-9999-9999", "montant": 100, "nonce": get_random_bytes(16).hex(), "transaction_id": transaction_id}
    
    from Crypto.Cipher import PKCS1_OAEP
    cipher = PKCS1_OAEP.new(marchand.banque.get_public_key())
    pi_chiffre = cipher.encrypt(json_lib.dumps(pi).encode())
    
    donnees_combinees = json_lib.dumps(oi, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
    h = SHA256.new(donnees_combinees)
    hash_donnees = h.hexdigest()
    fausse_signature = pkcs1_15.new(attaquant_key).sign(h)
    
    paquet = {
        "order_info": oi,
        "payment_info_enc": pi_chiffre,
        "signature": fausse_signature,
        "certificat_client": faux_cert,
        "transaction_id": transaction_id,
        "timestamp": timestamp
    }
    
    # Étapes de vérification
    verification_steps = []
    
    # Étape 1: Réception
    verification_steps.append({
        'step': 1,
        'action': 'Réception du paquet par le marchand',
        'status': 'success',
        'details': f"Transaction ID: {transaction_id[:16]}..., Montant: {oi['montant']}€"
    })
    
    # Étape 2: Vérification certificat
    cert_valide_ca = faux_cert.verifier_signature(ca.get_public_key())
    verification_steps.append({
        'step': 2,
        'action': 'Vérification de la signature du certificat par la CA',
        'status': 'error' if not cert_valide_ca else 'success',
        'details': f"Résultat: {'INVALIDE - Signature non vérifiable' if not cert_valide_ca else 'Valide'}"
    })
    
    # Étape 3: Tentative de traitement
    succes, msg = marchand.traiter_commande(paquet)
    
    verification_steps.append({
        'step': 3,
        'action': 'Décision finale du marchand',
        'status': 'error' if not succes else 'success',
        'details': msg
    })
    
    # Enregistrer la tentative d'attaque
    log_security_event(
        'usurpation',
        not succes,
        f"Tentative d'usurpation d'identité : attaquant se fait passer pour {client_cible} chez {marchand_nom}",
        {
            'client_cible': client_cible,
            'marchand': marchand_nom,
            'transaction_id': transaction_id[:16] + '...',
            'attaque_bloquee': not succes
        }
    )
    
    return jsonify({
        'success': True,
        'attaque_bloquee': not succes,
        'client_cible': client_cible,
        'resultat': {'succes': succes, 'message': msg},
        'defense': 'Vérification de certificat : La CA détecte que la signature du certificat est invalide',
        'explication': 'Le certificat auto-signé par l\'attaquant ne peut pas être vérifié par la CA légitime',
        'technical_details': {
            'vrai_certificat': vrai_cert_info,
            'faux_certificat': faux_cert_info,
            'transaction_id': transaction_id,
            'hash_donnees': hash_donnees,
            'pi_chiffre_taille': len(pi_chiffre),
            'signature_taille': len(fausse_signature)
        },
        'verification_steps': verification_steps,
        'paquet_recu': {
            'order_info': oi,
            'payment_info': '🔒 Chiffré RSA pour la banque (' + str(len(pi_chiffre)) + ' octets)',
            'certificat_emetteur': faux_cert.emetteur,
            'certificat_sujet': faux_cert.sujet
        }
    })

def test_attaque_certificat_revoque(params):
    """Tester l'utilisation d'un certificat révoqué"""
    # Créer un client temporaire
    temp_client = Client("Attaquant", "4970-8888-8888-8888", ca)
    
    # Créer son compte
    banque.creer_compte(temp_client.carte, "Attaquant", 1000)
    
    # Révoquer son certificat
    ca.revoquer_certificat(temp_client.certificat.numero_serie)
    
    marchand_nom = params.get('marchand', 'Amazon')
    marchand = marchands[marchand_nom]
    
    transaction_id = str(uuid.uuid4())
    timestamp = time.time()
    
    oi = {"items": ["Test Certificat Révoqué"], "montant": 50, "client": temp_client.nom, "timestamp": timestamp}
    pi = {"carte": temp_client.carte, "montant": 50, "nonce": get_random_bytes(16).hex(), "transaction_id": transaction_id}
    
    pi_chiffre = temp_client.chiffrer_pour(json_lib.dumps(pi).encode(), banque.get_public_key())
    donnees_combinees = json_lib.dumps(oi, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
    signature = temp_client.signer_donnee(donnees_combinees)
    
    paquet = {
        "order_info": oi,
        "payment_info_enc": pi_chiffre,
        "signature": signature,
        "certificat_client": temp_client.certificat,
        "transaction_id": transaction_id,
        "timestamp": timestamp
    }
    
    succes, msg = marchand.traiter_commande(paquet)
    
    # Enregistrer la tentative d'attaque
    log_security_event(
        'certificat_revoque',
        not succes,
        f"Tentative d'utilisation d'un certificat révoqué par {temp_client.nom} chez {marchand_nom}",
        {
            'attaquant': temp_client.nom,
            'marchand': marchand_nom,
            'certificat_numero': temp_client.certificat.numero_serie[:13] + '...',
            'transaction_id': transaction_id[:16] + '...'
        }
    )
    
    return jsonify({
        'success': True,
        'attaque_bloquee': not succes,
        'certificat_numero': temp_client.certificat.numero_serie[:13] + '...',
        'resultat': {'succes': succes, 'message': msg},
        'defense': 'Liste de révocation (CRL) : Le marchand vérifie si le certificat est révoqué',
        'explication': 'Le certificat révoqué est dans la CRL et ne peut plus être utilisé'
    })

def test_attaque_timestamp_expire(params):
    """Tester un timestamp expiré"""
    client_nom = params.get('client')
    marchand_nom = params.get('marchand')
    minutes_ancien = int(params.get('minutes', 60))
    
    if client_nom not in clients or marchand_nom not in marchands:
        return jsonify({'success': False, 'message': 'Client ou marchand invalide'})
    
    client = clients[client_nom]
    marchand = marchands[marchand_nom]
    
    transaction_id = str(uuid.uuid4())
    timestamp_ancien = time.time() - (minutes_ancien * 60)
    
    oi = {"items": ["Test Timestamp"], "montant": 50, "client": client.nom, "timestamp": timestamp_ancien}
    pi = {"carte": client.carte, "montant": 50, "nonce": get_random_bytes(16).hex(), "transaction_id": transaction_id}
    
    pi_chiffre = client.chiffrer_pour(json_lib.dumps(pi).encode(), marchand.banque.get_public_key())
    donnees_combinees = json_lib.dumps(oi, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
    signature = client.signer_donnee(donnees_combinees)
    
    paquet = {
        "order_info": oi,
        "payment_info_enc": pi_chiffre,
        "signature": signature,
        "certificat_client": client.certificat,
        "transaction_id": transaction_id,
        "timestamp": timestamp_ancien
    }
    
    succes, msg = marchand.traiter_commande(paquet)
    
    # Enregistrer la tentative d'attaque
    log_security_event(
        'timestamp_expire',
        not succes,
        f"Tentative avec timestamp expiré par {client_nom} chez {marchand_nom} (âge: {minutes_ancien} min)",
        {
            'client': client_nom,
            'marchand': marchand_nom,
            'timestamp_age_minutes': minutes_ancien,
            'transaction_id': transaction_id[:16] + '...'
        }
    )
    
    return jsonify({
        'success': True,
        'attaque_bloquee': not succes,
        'timestamp_age_minutes': minutes_ancien,
        'resultat': {'succes': succes, 'message': msg},
        'defense': 'Fenêtre temporelle de 5 minutes : Les transactions trop anciennes sont rejetées',
        'explication': f'La transaction date de {minutes_ancien} minutes, au-delà de la fenêtre de 5 minutes'
    })

def test_attaque_fonds_insuffisants(params):
    """Tester un achat avec fonds insuffisants"""
    # Créer un client pauvre temporaire
    temp_client = Client("ClientPauvre", "4970-0000-0000-0001", ca)
    solde_initial = float(params.get('solde', 50))
    montant_achat = float(params.get('montant', 1000))
    
    banque.creer_compte(temp_client.carte, "ClientPauvre", solde_initial)
    
    marchand_nom = params.get('marchand', 'Amazon')
    marchand = marchands[marchand_nom]
    
    transaction_id = str(uuid.uuid4())
    timestamp = time.time()
    
    oi = {"items": ["Test Fonds Insuffisants"], "montant": montant_achat, "client": temp_client.nom, "timestamp": timestamp}
    pi = {"carte": temp_client.carte, "montant": montant_achat, "nonce": get_random_bytes(16).hex(), "transaction_id": transaction_id}
    
    pi_chiffre = temp_client.chiffrer_pour(json_lib.dumps(pi).encode(), banque.get_public_key())
    donnees_combinees = json_lib.dumps(oi, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
    signature = temp_client.signer_donnee(donnees_combinees)
    
    paquet = {
        "order_info": oi,
        "payment_info_enc": pi_chiffre,
        "signature": signature,
        "certificat_client": temp_client.certificat,
        "transaction_id": transaction_id,
        "timestamp": timestamp
    }
    
    succes, msg = marchand.traiter_commande(paquet)
    
    # Enregistrer la tentative d'attaque
    log_security_event(
        'fonds_insuffisants',
        not succes,
        f"Tentative d'achat avec fonds insuffisants par {temp_client.nom} : {solde_initial}€ disponible, {montant_achat}€ demandé",
        {
            'client': temp_client.nom,
            'marchand': marchand_nom,
            'solde_disponible': solde_initial,
            'montant_demande': montant_achat,
            'transaction_id': transaction_id[:16] + '...'
        }
    )
    
    return jsonify({
        'success': True,
        'attaque_bloquee': not succes,
        'solde_disponible': solde_initial,
        'montant_demande': montant_achat,
        'resultat': {'succes': succes, 'message': msg},
        'defense': 'Vérification du solde par la banque : Transaction refusée si fonds insuffisants',
        'explication': f'Le client a {solde_initial}€ mais essaie d\'acheter pour {montant_achat}€'
    })

def test_attaque_carte_invalide(params):
    """Tester une carte invalide"""
    # Créer un client avec une carte non enregistrée
    temp_client = Client("FauxClient", "4970-9999-9999-9999", ca)
    # Ne PAS créer de compte bancaire
    
    marchand_nom = params.get('marchand', 'Amazon')
    marchand = marchands[marchand_nom]
    
    transaction_id = str(uuid.uuid4())
    timestamp = time.time()
    
    oi = {"items": ["Test Carte Invalide"], "montant": 100, "client": temp_client.nom, "timestamp": timestamp}
    pi = {"carte": temp_client.carte, "montant": 100, "nonce": get_random_bytes(16).hex(), "transaction_id": transaction_id}
    
    pi_chiffre = temp_client.chiffrer_pour(json_lib.dumps(pi).encode(), banque.get_public_key())
    donnees_combinees = json_lib.dumps(oi, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
    signature = temp_client.signer_donnee(donnees_combinees)
    
    paquet = {
        "order_info": oi,
        "payment_info_enc": pi_chiffre,
        "signature": signature,
        "certificat_client": temp_client.certificat,
        "transaction_id": transaction_id,
        "timestamp": timestamp
    }
    
    succes, msg = marchand.traiter_commande(paquet)
    
    # Enregistrer la tentative d'attaque
    log_security_event(
        'carte_invalide',
        not succes,
        f"Tentative d'achat avec carte invalide par {temp_client.nom} chez {marchand_nom} (carte: {temp_client.carte})",
        {
            'client': temp_client.nom,
            'marchand': marchand_nom,
            'carte': temp_client.carte,
            'transaction_id': transaction_id[:16] + '...'
        }
    )
    
    return jsonify({
        'success': True,
        'attaque_bloquee': not succes,
        'carte': temp_client.carte,
        'resultat': {'succes': succes, 'message': msg},
        'defense': 'Vérification de la carte par la banque : Carte non trouvée dans la base de données',
        'explication': 'La carte n\'existe pas dans le système bancaire'
    })

def test_attaque_injection(params):
    """Tester une injection de code"""
    client_nom = params.get('client')
    marchand_nom = params.get('marchand')
    
    if client_nom not in clients or marchand_nom not in marchands:
        return jsonify({'success': False, 'message': 'Client ou marchand invalide'})
    
    client = clients[client_nom]
    marchand = marchands[marchand_nom]
    
    transaction_id = str(uuid.uuid4())
    timestamp = time.time()
    
    # Données malveillantes
    oi_malveillant = {
        "items": ["'; DROP TABLE users; --", "<script>alert('XSS')</script>"],
        "montant": 50,
        "client": client.nom + "' OR '1'='1",
        "timestamp": timestamp
    }
    
    pi = {"carte": client.carte, "montant": 50, "nonce": get_random_bytes(16).hex(), "transaction_id": transaction_id}
    
    pi_chiffre = client.chiffrer_pour(json_lib.dumps(pi).encode(), marchand.banque.get_public_key())
    donnees_combinees = json_lib.dumps(oi_malveillant, sort_keys=True).encode() + pi_chiffre + transaction_id.encode()
    signature = client.signer_donnee(donnees_combinees)
    
    paquet = {
        "order_info": oi_malveillant,
        "payment_info_enc": pi_chiffre,
        "signature": signature,
        "certificat_client": client.certificat,
        "transaction_id": transaction_id,
        "timestamp": timestamp
    }
    
    succes, msg = marchand.traiter_commande(paquet)
    
    # Enregistrer la tentative d'attaque
    log_security_event(
        'injection',
        False,  # L'injection ne "réussit" pas vraiment car les données sont traitées comme du texte
        f"Tentative d'injection de code par {client_nom} chez {marchand_nom}",
        {
            'client': client_nom,
            'marchand': marchand_nom,
            'donnees_malveillantes': oi_malveillant['items'],
            'transaction_id': transaction_id[:16] + '...'
        }
    )
    
    return jsonify({
        'success': True,
        'attaque_bloquee': False,  # L'injection ne "réussit" pas car les données sont traitées comme du texte
        'donnees_malveillantes': oi_malveillant['items'],
        'resultat': {'succes': succes, 'message': msg},
        'defense': 'Les données sont signées et stockées comme texte, jamais interprétées comme code',
        'explication': 'Le système traite toutes les données comme du texte brut, pas comme du code exécutable'
    })

@socketio.on('connect')
def handle_connect():
    if not ca:
        init_system()
    emit('connected', {'message': 'Connecté au serveur SET'})

@socketio.on('demander_stats')
def handle_stats_request():
    if ca:
        stats = {
            'certificats': len(ca.certificats_emis),
            'transactions': len(banque.historique_transactions),
            'marchands': len(marchands),
            'clients': len(clients)
        }
        emit('stats_update', stats)

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🌐 DÉMARRAGE DE L'INTERFACE WEB SET/CDA")
    print("="*70)
    print("\n📱 Accédez à l'application sur: http://localhost:5001")
    print("\n🔐 Fonctionnalités disponibles:")
    print("  - Dashboard général avec statistiques")
    print("  - Interface client pour effectuer des achats")
    print("  - Interface marchand pour gérer les commandes")
    print("  - Interface banque pour les transactions")
    print("  - Gestion des certificats avec révocation")
    print("  - Tests de sécurité interactifs")
    print("  - Logs en temps réel avec WebSockets")
    print("\n" + "="*70 + "\n")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)
