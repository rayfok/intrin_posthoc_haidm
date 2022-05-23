import flask
from haidm.model import db, Session

views = flask.Blueprint(
    "views", __name__, template_folder="templates", static_folder="static"
)


@views.route("/", methods=["GET"])
@views.route("/task", methods=["GET"])
def show_index():
    context = {}
    participant_id = flask.request.args.get("participantId", None)
    study_id = flask.request.args.get("studyId", None)
    session_id = flask.request.args.get("sessionId", None)
    task = flask.request.args.get("task", None)
    condition = flask.request.args.get("condition", None)
    if participant_id and study_id and session_id and task and condition:
        session = Session(
            participant_id=participant_id,
            study_id=study_id,
            session_id=session_id,
            task=task,
            condition=condition,
        )
        db.session.add(session)
        db.session.commit()
    title = "HAIDM"
    if task:
        title += f" | {task.upper()}"
    return flask.render_template("index.html", title=f"{title}", **context)
