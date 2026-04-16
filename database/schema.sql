-- SQL Schema for Recipe Collection System
-- Compatible with SQLite

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(50) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recipe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    difficulty VARCHAR(10),
    cook_time INTEGER,
    cover_image VARCHAR(255),
    category VARCHAR(50),
    author_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(author_id) REFERENCES user(id)
);

CREATE TABLE ingredient (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    quantity VARCHAR(50) NOT NULL,
    unit VARCHAR(20),
    FOREIGN KEY(recipe_id) REFERENCES recipe(id) ON DELETE CASCADE
);

CREATE TABLE step (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    step_order INTEGER NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY(recipe_id) REFERENCES recipe(id) ON DELETE CASCADE
);

CREATE TABLE favorite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY(recipe_id) REFERENCES recipe(id) ON DELETE CASCADE,
    UNIQUE(user_id, recipe_id)
);
