import json
import os

import flask
import haidm
import http

DATA_DIR = "data"
task_data = {}


def load_data():
    with open(os.path.join(DATA_DIR, "task_recidivism.json"), "r") as f:
        global task_data
        task_data = json.load(f)
        reformatted = {}
        for task, examples in task_data.items():
            q_by_id = {ex["id"]: ex for ex in examples}
            reformatted[task] = q_by_id
        task_data = reformatted


@haidm.app.before_first_request
def before_first_request():
    load_data()


def validate_task(task):
    return task in task_data


def validate_qid(task, qid):
    return qid in task_data[task]


@haidm.app.route("/api/v1/q/", methods=["GET"])
def get_question():
    question_id = flask.request.args.get("q", type=int)
    task = flask.request.args.get("task")
    context = {}
    print(task_data[task][question_id])
    print(task_data.get(task, {}).get(question_id, {}))
    if flask.request.method == "GET":
        if not validate_task(task) or not validate_qid(task, question_id):
            return flask.make_response(
                flask.jsonify(**context), http.HTTPStatus.BAD_REQUEST
            )
        context = task_data[task][question_id]
    return flask.make_response(flask.jsonify(**context), http.HTTPStatus.OK)


@haidm.app.route("/api/v1/submit/", methods=["POST"])
def submit_data():
    conn = haidm.model.get_db()
    responses = flask.request.json["responses"]
    try:
        for r in responses:
            r_data = {
                "worker_id": r["worker_id"],
                "hit_id": r["hit_id"],
                "assignment_id": r["assignment_id"],
                "task": r["task"],
                "question_id": r["question_id"],
                "initial_human_decision": r["initial_human_decision"],
                "final_human_decision": r["final_human_decision"],
                "ai_decision": r["ai_decision"],
                "initial_decision_time": r["initial_decision_time"],
                "final_decision_time": r["final_decision_time"],
                "condition": r["condition"],
            }
            conn.execute(
                f"INSERT INTO responses \
                ({r_data.keys()}) \
                VALUES ({','.join(['?'] * len(r_data))})",
                tuple(r_data.values()),
            )
        conn.commit()
        context = {"success": True}
        return flask.make_response(flask.jsonify(**context), http.HTTPStatus.OK)
    except Exception as e:
        print("Error while submitting:", e, "responses:", responses)
        context = {"success": False}
        return flask.make_response(
            flask.jsonify(**context), http.HTTPStatus.BAD_REQUEST
        )
