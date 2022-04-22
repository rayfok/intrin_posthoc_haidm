import flask
import haidm
from model import db, Session


@haidm.app.route("/", methods=["GET"])
@haidm.app.route("/task", methods=["GET"])
def show_index():
    context = {}
    assignmentId = flask.request.args.get("assignmentId", None)
    hitId = flask.request.args.get("hitId", None)
    workerId = flask.request.args.get("workerId", None)
    task = flask.request.args.get("task", None)
    condition = flask.request.args.get("condition", None)
    if assignmentId and hitId and workerId and task and condition:
        session = Session(
            workerId=workerId,
            hitId=hitId,
            assignmentId=assignmentId,
            task=task,
            condition=condition,
        )
        db.session.add(session)
        db.session.commit()
    title = "HAIDM"
    if task:
        title += f" | {task.upper()}"
    return flask.render_template("index.html", title=f"{title}", **context)


@haidm.app.route("/favicon.ico")
def favicon():
    return flask.send_from_directory("static", "favicon.ico")
