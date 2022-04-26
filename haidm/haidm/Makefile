init:
	@pip install -e .
	@npm install

front:
	@npm run watch

back:
	@gunicorn --reload -c gunicorn.conf.py wsgi:app

build:
	@npm run build

.PHONY: init front back build
