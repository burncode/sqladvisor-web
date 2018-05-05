# -*- coding: utf-8 -*-

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host=app.config['LISTEN_IP'],
            port=int(app.config['LISTEN_PORT']),
            debug=app.config['DEBUG'])
