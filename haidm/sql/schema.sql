CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id TEXT,
    hit_id TEXT,
    assignment_id TEXT,
    task TEXT NOT NULL,
    condition TEXT,
    question_id INTEGER NOT NULL,
    initial_human_decision TEXT NOT NULL,
    final_human_decision TEXT NOT NULL,
    ai_decision TEXT,
    initial_decision_time INTEGER,
    final_decision_time INTEGER,
    created DATE DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workerId TEXT,
    assignmentId TEXT,
    hitId TEXT,
    task TEXT,
    condition TEXT,
    created DATE DEFAULT (datetime('now','localtime'))
);
