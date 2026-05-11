import os
from quart import Quart
from app.routes import main

def create_app():
    app = Quart(__name__)
    app.register_blueprint(main)
    return app

# إنشاء نسخة من التطبيق للتشغيل
app = create_app()

# هذا الجزء ضروري لعمل السيرفر على Render
if __name__ == '__main__':
    # Render يرسل رقم المنفذ (Port) عبر المتغير PORT
    port = int(os.environ.get("PORT", 5555))
    # تشغيل التطبيق على العنوان 0.0.0.0 ليصبح متاحاً للإنترنت
    app.run(host='0.0.0.0', port=port)