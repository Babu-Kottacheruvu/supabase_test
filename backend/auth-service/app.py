import os
from datetime import datetime, timedelta

import truststore
truststore.inject_into_ssl()

import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret')

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase: Client | None = None

if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)


def create_token(email: str):
    payload = {
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=2),
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')


@app.get('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'auth-service'})


@app.post('/auth/register')
def register():
    if supabase is None:
        return jsonify({'error': 'supabase client is not configured'}), 500

    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()

    if not name or not email or not password:
        return jsonify({'error': 'name, email, and password are required'}), 400

    existing = supabase.table('users').select('id').eq('email', email).limit(1).execute()
    if existing.data:
        return jsonify({'error': 'user already exists'}), 409

    result = supabase.table('users').insert({
        'name': name,
        'email': email,
        'password_hash': generate_password_hash(password),
    }).execute()

    if not result.data:
        return jsonify({'error': 'registration failed'}), 500

    return jsonify({'message': 'user registered successfully'}), 201


@app.post('/auth/login')
def login():
    if supabase is None:
        return jsonify({'error': 'supabase client is not configured'}), 500

    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = (data.get('password') or '').strip()

    result = supabase.table('users').select('*').eq('email', email).limit(1).execute()
    user = result.data[0] if result.data else None

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'invalid credentials'}), 401

    token = create_token(user['email'])
    return jsonify({
        'token': token,
        'user': {'name': user['name'], 'email': user['email']},
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('APP_PORT', 5001)), debug=True)
