import os

import truststore
truststore.inject_into_ssl()

import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret')

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase: Client | None = None

if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)


def get_current_user():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None

    token = auth_header.split(' ', 1)[1]
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload.get('email')
    except Exception:
        return None


@app.get('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'crud-service'})


@app.get('/items')
def list_items():
    if supabase is None:
        return jsonify({'error': 'supabase client is not configured'}), 500

    user_email = get_current_user()
    if not user_email:
        return jsonify({'error': 'unauthorized'}), 401

    response = supabase.table('items').select('*').eq('owner_email', user_email).order('created_at', desc=True).execute()
    return jsonify({'items': response.data})


@app.post('/items')
def create_item():
    if supabase is None:
        return jsonify({'error': 'supabase client is not configured'}), 500

    user_email = get_current_user()
    if not user_email:
        return jsonify({'error': 'unauthorized'}), 401

    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    description = (data.get('description') or '').strip()
    if not title or not description:
        return jsonify({'error': 'title and description are required'}), 400

    result = supabase.table('items').insert({
        'owner_email': user_email,
        'title': title,
        'description': description,
    }).execute()

    if not result.data:
        return jsonify({'error': 'item creation failed'}), 500

    return jsonify(result.data[0]), 201


@app.put('/items/<int:item_id>')
def update_item(item_id):
    if supabase is None:
        return jsonify({'error': 'supabase client is not configured'}), 500

    user_email = get_current_user()
    if not user_email:
        return jsonify({'error': 'unauthorized'}), 401

    data = request.get_json() or {}
    new_title = (data.get('title') or '').strip()
    new_description = (data.get('description') or '').strip()

    update_payload = {}
    if new_title:
        update_payload['title'] = new_title
    if new_description:
        update_payload['description'] = new_description

    if not update_payload:
        return jsonify({'error': 'no valid fields supplied'}), 400

    result = supabase.table('items').update(update_payload).eq('id', item_id).eq('owner_email', user_email).execute()
    if not result.data:
        return jsonify({'error': 'item not found'}), 404

    return jsonify(result.data[0])


@app.delete('/items/<int:item_id>')
def delete_item(item_id):
    if supabase is None:
        return jsonify({'error': 'supabase client is not configured'}), 500

    user_email = get_current_user()
    if not user_email:
        return jsonify({'error': 'unauthorized'}), 401

    result = supabase.table('items').delete().eq('id', item_id).eq('owner_email', user_email).execute()
    if not result.data:
        return jsonify({'error': 'item not found'}), 404

    return jsonify({'message': 'item deleted'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('APP_PORT', 5002)), debug=True)
