import re
import sqlite3

import flask

import haidm


def dict_factory(cursor, row):
    output = {}
    for idx, col in enumerate(cursor.description):
        output[col[0]] = row[idx]
    return output


def get_db():
    if not hasattr(flask.g, "db"):
        flask.g.db = sqlite3.connect(haidm.app.config["DATABASE_FILENAME"])
        flask.g.db.row_factory = dict_factory
        flask.g.db.execute("PRAGMA foreign_keys = ON")
    return flask.g.db


@haidm.app.teardown_appcontext
def close_db(error):
    if hasattr(flask.g, "db"):
        flask.g.db.commit()
        flask.g.db.close()
