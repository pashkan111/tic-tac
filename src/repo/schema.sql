CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE INDEX idx_users_username ON users (username);


CREATE TABLE game (
    player1_id INTEGER NOT NULL,
    player2_id INTEGER NOT NULL,
    winner INTEGER,
    game_finished TIMESTAMPTZ NOT NULL,
    board JSON,

    FOREIGN KEY (player1_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (player2_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (winner) REFERENCES users(id) ON DELETE RESTRICT
);

CREATE INDEX idx_game_player1 ON game (player1_id);
CREATE INDEX idx_game_player2 ON game (player2_id);