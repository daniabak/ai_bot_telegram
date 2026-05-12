import os
from quart import Quart
from app.routes import main

def create_app():
    app = Quart(__name__)
    app.register_blueprint(main)
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5555))
    app.run(host='0.0.0.0', port=port)