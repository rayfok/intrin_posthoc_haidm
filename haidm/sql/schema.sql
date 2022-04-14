CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id TEXT,
    hit_id TEXT,
    assignment_id TEXT,
    task TEXT NOT NULL,
    question_id INTEGER NOT NULL,
    inital_human_decision TEXT NOT NULL,
    final_human_decision TEXT NOT NULL,
    ai_decision TEXT,
    initial_decision_time INTEGER,
    final_decision_time INTEGER,
    condition TEXT,
    created DATE DEFAULT (datetime('now','localtime'))
);
