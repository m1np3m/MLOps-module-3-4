SHELL := /bin/bash # Use bash syntax

install:
	python3 -m pip install -r requirements.txt

build:
	find . -path "*/component.py" | xargs -n 1 python3

clean:
	find . -path "*/component.yaml" | xargs -n 1 rm

dev: install build
	python3 pipeline.py --dev
