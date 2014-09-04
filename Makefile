WORDS_DATABASE = words.db
SCHEMA = schema.sql
PRODUCE_PY = produce.py
SENTENCES_DATA = raw_data.txt
MATRIX_FILE = counts.npy

all: | create-db load-data

.PHONY: create-db
create-db: clean-db
	sqlite3 $(WORDS_DATABASE) <$(SCHEMA)

.PHONY: load-sentences
load-data:
	python $(PRODUCE_PY) LOAD <$(SENTENCES_DATA)

.PHONY: generate-matrix
generate-matrix:
	python $(PRODUCE_PY) MATRIX $(MATRIX_FILE)

.PHONY: clean-db
clean-db:
	rm -f $(WORDS_DATABASE)
