import logging

from flask import Flask

from haidm.api.questions import api
from haidm.model import db
from haidm.views.index import views

app = Flask(__name__, static_url_path="/haidm/static")
app.config.from_object("haidm.config")
db.init_app(app)
app.register_blueprint(views, url_prefix="/haidm")
app.register_blueprint(api, url_prefix="/haidm")

with app.app_context():
    db.create_all()
    db.session.commit()


if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers.extend(gunicorn_logger.handlers)
    app.logger.setLevel(gunicorn_logger.level)
