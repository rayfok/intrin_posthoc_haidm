import json

import requests


def get_config():
    with open("secret.json", "r") as f:
        return json.load(f)


def get_account_details(config):
    resp = requests.get(
        "https://api.prolific.co/api/v1/users/me/",
        headers={"Authorization": f"Token {config['api_token']}"},
    )
    return resp.json() if resp.status_code == 200 else None


def list_studies(config):
    resp = requests.get(
        "https://api.prolific.co/api/v1/studies/",
        headers={"Authorization": f"Token {config['api_token']}"},
    )
    return resp.json() if resp.status_code == 200 else None


def create_study(config, name):
    with open(f"{name}.json", "r") as f:
        study_config = json.load(f)
    resp = requests.post(
        "https://api.prolific.co/api/v1/studies/",
        headers={"Authorization": f"Token {config['api_token']}"},
        data=study_config,
    )
    return resp.json() if resp.status_code == 201 else None


def publish_study(config, id):
    resp = requests.post(
        f"https://api.prolific.co/api/v1/studies/{id}/transition/",
        headers={"Authorization": f"Token {config['api_token']}"},
        data={"action": "PUBLISH"},
    )
    return resp.status_code == 200


def pause_study(config, id):
    resp = requests.post(
        f"https://api.prolific.co/api/v1/studies/{id}/transition/",
        headers={"Authorization": f"Token {config['api_token']}"},
        data={"action": "PAUSE"},
    )
    return resp.status_code == 200


def restart_paused_study(config, id):
    resp = requests.post(
        f"https://api.prolific.co/api/v1/studies/{id}/transition/",
        headers={"Authorization": f"Token {config['api_token']}"},
        data={"action": "START"},
    )
    return resp.status_code == 200


def stop_study(config, id):
    resp = requests.post(
        f"https://api.prolific.co/api/v1/studies/{id}/transition/",
        headers={"Authorization": f"Token {config['api_token']}"},
        data={"action": "STOP"},
    )
    return resp.status_code == 200


def get_study(config, id):
    resp = requests.get(
        f"https://api.prolific.co/api/v1/studies/{id}/",
        headers={"Authorization": f"Token {config['api_token']}"},
    )
    return resp.json() if resp.status_code == 200 else None


def update_study(config, id):
    # url = "https://api.prolific.co/api/v1/studies/{id}/"
    raise NotImplementedError


def list_study_submissions(config, id):
    resp = requests.get(
        f"https://api.prolific.co/api/v1/studies/{id}/submissions/",
        headers={"Authorization": f"Token {config['api_token']}"},
    )
    return resp.json()["results"] if resp.status_code == 200 else None


def get_study_cost(config, name):
    with open(f"{name}.json", "r") as f:
        study_config = json.load(f)
    resp = requests.post(
        "https://api.prolific.co/api/v1/study-cost-calculator/",
        headers={"Authorization": f"Token {config['api_token']}"},
        data={"reward": study_config["reward"], "total_available_places": 5},
    )
    return resp.json()["total_cost"] if resp.response_code == 200 else None


def list_all_requirements(config):
    resp = requests.get(
        "https://api.prolific.co/api/v1/eligibility-requirements/",
        headers={"Authorization": f"Token {config['api_token']}"},
    )
    return resp.json()["results"] if resp.status_code == 200 else None


def count_eligible_participants(config, name):
    with open(f"{name}.json", "r") as f:
        study_config = json.load(f)
    resp = requests.post(
        "https://api.prolific.co/api/v1/eligibility-count/",
        headers={"Authorization": f"Token {config['api_token']}"},
        data={"eligibility_requirements": study_config["eligibility_requirements"]},
    )
    return resp.json()["count"] if resp.response_code == 200 else None


def list_submissions(config, study_id=None):
    url = "https://api.prolific.co/api/v1/submissions/"
    if study_id:
        url += f"?study={study_id}"
    resp = requests.get(url, headers={"Authorization": f"Token {config['api_token']}"},)
    return resp.json()["results"] if resp.status_code == 200 else None


def get_submission_details(config, submission_id):
    resp = requests.get(
        f"https://api.prolific.co/api/v1/submissions/{submission_id}/",
        headers={"Authorization": f"Token {config['api_token']}"},
    )
    return resp.json() if resp.status_code == 200 else None


def approve_submission(config, id):
    resp = requests.post(
        f"https://api.prolific.co/api/v1/submissions/{id}/transition/",
        headers={"Authorization": f"Token {config['api_token']}"},
        data={"action": "APPROVE"},
    )
    return resp.status_code == 200


def reject_submission(config, id, message, rejection_category):
    resp = requests.post(
        f"https://api.prolific.co/api/v1/submissions/{id}/transition/",
        headers={"Authorization": f"Token {config['api_token']}"},
        data={
            "action": "REJECT",
            "message": message,
            "rejection_category": rejection_category,
        },
    )
    return resp.status_code == 200


def bulk_approve_submissions(config, study_id, participant_ids):
    resp = requests.post(
        "https://api.prolific.co/api/v1/submissions/bulk-approve/",
        headers={"Authorization": f"Token {config['api_token']}"},
        data={"study_id": study_id, "participant_ids": participant_ids},
    )
    return resp.status_code == 200


def setup_bonus(config, study_id, csv_bonuses):
    resp = requests.post(
        "https://api.prolific.co/api/v1/submissions/bonus-payments/",
        headers={"Authorization": f"Token {config['api_token']}"},
        data={"study_id": study_id, "csv_bonuses": csv_bonuses},
    )
    return resp.json() if resp.status_code == 201 else None


def pay_bonus(config, bonus_id):
    resp = requests.post(
        f"https://api.prolific.co/api/v1/bulk-bonus-payments/{bonus_id}/pay/",
        headers={"Authorization": f"Token {config['api_token']}"},
    )
    return resp.status_code == 202
