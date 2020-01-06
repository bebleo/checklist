-- DROP EXISTING TABLES IF THEY'RE ALREADY PRESENT
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS password_tokens;
DROP TABLE IF EXISTS checklists;
DROP TABLE IF EXISTS checklist_history;
DROP TABLE IF EXISTS checklist_items;
DROP TABLE IF EXISTS config;

-- CREATE NEW TABLES AS NECESSARY

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    given_name TEXT,
    family_name TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    deactivated INTEGER NOT NULL DEFAULT 0,
    password TEXT NOT NULL,
    row_version TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE password_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    token_type TEXT NOT NULL,
    expires TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE checklists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    description TEXT,
    is_complete BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by INTEGER NOT NULL,
    assigned_to INTEGER NOT NULL,
    FOREIGN KEY (created_by) REFERENCES users (id),
    FOREIGN KEY (assigned_to) REFERENCES users (id)
);

CREATE TABLE checklist_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_text TEXT NOT NULL,
    done BOOLEAN DEFAULT FALSE,
    checklist_id INTEGER NOT NULL,
    FOREIGN KEY (checklist_id) REFERENCES checklists (id)
);

CREATE TABLE checklist_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    change_description TEXT NOT NULL,
    change_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    checklist_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (checklist_id) REFERENCES checklists (id)
);

CREATE TABLE config (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    config_key TEXT UNIQUE NOT NULL,
    config_value TEXT NOT NULL
);

INSERT INTO users (
    email, 
    given_name, 
    family_name, 
    is_admin, 
    deactivated, 
    password)
VALUES (
    'admin@bebleo.url', 
    'Administrator', 
    'Built-In', 
    1, 
    0, 
    'pbkdf2:sha256:150000$0iM7kfzV$8a112f27b8b261f65e93b236fda47ceed69ee3f0696a5d435be516568d4a946d');
