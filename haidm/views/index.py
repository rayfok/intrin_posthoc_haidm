import logging
import os

import flask

import haidm
import haidm.model as model


@haidm.app.route('/', methods=['GET'])
def show_index():
    context = {}
    conn = model.get_db()
    assignmentId = flask.request.args.get('assignmentId', None)
    hitId = flask.request.args.get('hitId', None)
    workerId = flask.request.args.get('workerId', None)
    study = flask.request.args.get('study', None)
    conn.execute('INSERT INTO sessions (assignmentId, hitId, workerId, study) VALUES (?,?,?,?)',
                 (assignmentId, hitId, workerId, study))
    conn.commit()
    return flask.render_template("index.html", **context)


@haidm.app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory('static', 'favicon.ico')
