CREATE TABLE raw (
       id INTEGER PRIMARY KEY AUTOINCREMENT, 
       sentence TEXT NOT NULL,
       sentence_id INTEGER REFERENCES sentences(id)
);

CREATE TABLE sentences (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       word_id INTEGER REFERENCES words(id),
       prev_id INTEGER REFERENCES sentences(id)
);
CREATE INDEX sentences_word_idx ON sentences(word_id);
CREATE INDEX sentences_prev_idx ON sentences(prev_id);

CREATE TABLE words (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       word TEXT NOT NULL,
       UNIQUE(word)
);
CREATE UNIQUE INDEX words_word_idx ON words(word);
