import http
import json
import os
import traceback

import flask
from haidm.model import Response, db

DATA_DIR = "data"
task_data = {}

api = flask.Blueprint("api", __name__)


def load_data():
    with open(os.path.join(DATA_DIR, "task_recidivism.json"), "r") as f:
        global task_data
        task_data = json.load(f)
        reformatted = {}
        for task, examples in task_data.items():
            q_by_id = {str(ex["id"]): ex for ex in examples}
            reformatted[task] = q_by_id
        task_data = reformatted


def validate_task(task):
    return task in task_data


def validate_qid(task, qid):
    return qid == "-1" or qid in task_data[task]


@api.before_app_first_request
def before_first_request():
    load_data()


@api.route("/api/v1/q/", methods=["GET"])
def get_question():
    question_id = flask.request.args.get("q")
    task = flask.request.args.get("task")
    context = {}
    if flask.request.method == "GET":
        if not validate_task(task) or not validate_qid(task, question_id):
            return flask.make_response(
                flask.jsonify(**context), http.HTTPStatus.BAD_REQUEST
            )
        if question_id == "-1":
            context = task_data[task]
        else:
            context = {question_id: task_data[task][question_id]}
    return flask.make_response(flask.jsonify(**context), http.HTTPStatus.OK)


@api.route("/api/v1/submit/", methods=["POST"])
def submit_data():
    responses = flask.request.json["responses"]
    try:
        mappings = [
            {
                "worker_id": r["worker_id"],
                "hit_id": r["hit_id"],
                "assignment_id": r["assignment_id"],
                "task": r["task"],
                "condition": r["condition"],
                "question_id": r["question_id"],
                "initial_human_decision": r["initial_human_decision"],
                "final_human_decision": r["final_human_decision"],
                "ai_decision": r["ai_decision"],
                "initial_decision_time": r["initial_decision_time"],
                "final_decision_time": r["final_decision_time"],
                "ground_truth": r["ground_truth"],
            }
            for r in responses
        ]
        db.session.bulk_insert_mappings(Response, mappings)
        db.session.commit()
        context = {"success": True}
        return flask.make_response(flask.jsonify(**context), http.HTTPStatus.OK)
    except Exception as e:
        traceback.print_exc()
        print("Responses:", responses)
        context = {"success": False}
        return flask.make_response(
            flask.jsonify(**context), http.HTTPStatus.BAD_REQUEST
        )


@api.route("/api/v1/completed/", methods=["GET"])
def has_previously_completed():
    context = {}
    if flask.request.method == "GET":
        worker_id = flask.request.args.get("workerId")
        workers = [r.worker_id for r in db.session.query(Response.worker_id).distinct()]
        context["completed"] = worker_id in workers
    return flask.make_response(flask.jsonify(**context), http.HTTPStatus.OK)
