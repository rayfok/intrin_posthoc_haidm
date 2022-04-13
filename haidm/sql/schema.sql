CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    questionId INTEGER NOT NULL,
    choice TEXT NOT NULL,
    workerId TEXT,
    assignmentId TEXT,
    hitId TEXT,
    created DATE DEFAULT (datetime('now','localtime')),
    elapsedTime INT,
    explanation TEXT,
    AIPrediction TEXT,
    condition TEXT
);
