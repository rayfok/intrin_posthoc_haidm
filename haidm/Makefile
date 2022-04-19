init:
	@pip install -e .
	@npm install
	@./bin/db.sh create

reset:
	@./bin/db.sh reset

front:
	@npm run watch

back:
	# @pkill -f gunicorn
	@./bin/start_api.sh

build:
	@make ready
	@npm run build

ready:
	@make prettier

prettier:
	@npm run prettier

.PHONY: init reset front back build ready prettier
