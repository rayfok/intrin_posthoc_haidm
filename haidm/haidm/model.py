from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.String(80), nullable=True)
    hit_id = db.Column(db.String(80), nullable=True)
    assignment_id = db.Column(db.String(80), nullable=True)
    task = db.Column(db.String(80), nullable=False)
    condition = db.Column(db.String(80), nullable=True)
    question_id = db.Column(db.String(80), nullable=False)
    initial_human_decision = db.Column(db.String(80), nullable=True)
    final_human_decision = db.Column(db.String(80), nullable=False)
    ai_decision = db.Column(db.String(80), nullable=True)
    initial_decision_time = db.Column(db.Integer, nullable=False)
    final_decision_time = db.Column(db.Integer, nullable=False)
    ground_truth = db.Column(db.String(80), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Response {self.worker_id} - {self.task} - {self.condition}>"


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workerId = db.Column(db.String(80), nullable=True)
    hitId = db.Column(db.String(80), nullable=True)
    assignmentId = db.Column(db.String(80), nullable=True)
    task = db.Column(db.String(80), nullable=True)
    condition = db.Column(db.String(80), nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Worker {self.workerId} - {self.hitId} - {self.assignmentId}>"
