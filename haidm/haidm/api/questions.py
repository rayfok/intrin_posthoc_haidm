import http
import json
import os
import traceback

import flask
from haidm.model import ExitSurveyResponse, Response, db

DATA_DIR = "data"
task_data = {}

api = flask.Blueprint("api", __name__)


def load_data():
    with open(os.path.join(DATA_DIR, "task_data.json"), "r") as f:
        global task_data
        task_data = json.load(f)
        for task, data in task_data.items():
            for id, x in data["instances"].items():
                x["id"] = id
            for id, x in data["training_instances"].items():
                x["id"] = id


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
                "participant_id": r["participant_id"],
                "study_id": r["study_id"],
                "session_id": r["session_id"],
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


@api.route("/api/v1/submit-exit-survey/", methods=["POST"])
def submit_exit_survey_data():
    r = flask.request.json["responses"]
    try:
        db.session.add(
            ExitSurveyResponse(
                participant_id=r["participant_id"],
                study_id=r["study_id"],
                session_id=r["session_id"],
                task=r["task"],
                condition=r["condition"],
                recognizeIncorrect=r["recognizeIncorrect"],
                recognizeCorrect=r["recognizeCorrect"],
                influenceDecisionMaking=r["influenceDecisionMaking"],
                influenceUnderstanding=r["influenceUnderstanding"],
                age=r["age"],
                race=r["race"],
                gender=r["gender"],
                education=r["education"],
            )
        )
        db.session.commit()
        context = {"success": True}
        return flask.make_response(flask.jsonify(**context), http.HTTPStatus.OK)
    except Exception as e:
        traceback.print_exc()
        print("Exit survey responses:", r)
        context = {"success": False}
        return flask.make_response(
            flask.jsonify(**context), http.HTTPStatus.BAD_REQUEST
        )


@api.route("/api/v1/completed/", methods=["GET"])
def has_previously_completed():
    context = {}
    if flask.request.method == "GET":
        test_ids = ["test"]
        pid = flask.request.args.get("participantId")
        completed = [
            r.participant_id
            for r in db.session.query(Response.participant_id).distinct()
        ]
        context["completed"] = pid in completed and pid not in test_ids
    return flask.make_response(flask.jsonify(**context), http.HTTPStatus.OK)
