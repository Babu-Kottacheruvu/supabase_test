import importlib.util
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _load_flask_app(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app


auth_app = _load_flask_app('auth_service_app', BASE_DIR / 'auth-service' / 'app.py')
crud_app = _load_flask_app('crud_service_app', BASE_DIR / 'crud-service' / 'app.py')


def application(environ, start_response):
    path = environ.get('PATH_INFO', '')

    if path == '/health':
        body = json.dumps({'status': 'ok', 'services': ['auth-service', 'crud-service']}).encode()
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [body]

    if path.startswith('/items'):
        return crud_app(environ, start_response)

    return auth_app(environ, start_response)


if __name__ == '__main__':
    from werkzeug.serving import run_simple

    port = int(os.getenv('PORT', os.getenv('APP_PORT', 5000)))
    run_simple('0.0.0.0', port, application, use_reloader=False)
