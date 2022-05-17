import dataclasses
import json
import os
from datetime import datetime

from haidm.app import app
from haidm.model import ExitSurveyResponse, Response, db


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)

def export_data():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with app.app_context():
        with open(os.path.join(dir_path, "haidm_task_responses.json"), "w") as out:
            json.dump([dataclasses.asdict(r) for r in Response.query.all()], out, cls=DateTimeEncoder, indent=2)

        with open(os.path.join(dir_path, "haidm_survey_responses.json"), "w") as out:
            json.dump([dataclasses.asdict(r) for r in ExitSurveyResponse.query.all()], out, cls=DateTimeEncoder, indent=2)


if __name__ == "__main__":
    export_data()
