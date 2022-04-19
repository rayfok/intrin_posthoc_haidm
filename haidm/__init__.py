import logging

import flask

app = flask.Flask(__name__)
app.config.from_object("haidm.config")
app.config.from_envvar("HAIDM_SETTINGS", silent=True)


from model import db, Response, Session

db.create_all()
db.session.commit()

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers.extend(gunicorn_logger.handlers)
    app.logger.setLevel(gunicorn_logger.level)

import haidm.api
import haidm.views
