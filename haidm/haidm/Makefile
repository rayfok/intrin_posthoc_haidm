init:
	@pip install -e .
	@npm install

front:
	@npm run watch

back:
	# @pkill -f gunicorn
	@gunicorn --reload -c gunicorn.conf.py haidm:app

build:
	@npm run build

.PHONY: init front back build
