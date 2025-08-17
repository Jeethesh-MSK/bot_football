SHELL := /usr/bin/bash

.PHONY: venv install run init-db test-notify docker-build docker-up docker-down

venv:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

install:
	pip3 install --break-system-packages -r requirements.txt

init-db:
	python3 -m seatwatcher.cli --config configs/seatwatcher.yaml init-db

run:
	python3 -m seatwatcher.cli --config configs/seatwatcher.yaml run

notify:
	python3 -m seatwatcher.cli --config configs/seatwatcher.yaml test-notify --subject "Test" --body "This is a test"

docker-build:
	docker build -f docker/Dockerfile -t seatwatcher:latest .

docker-up:
	docker compose -f docker/docker-compose.yml up --build

docker-down:
	docker compose -f docker/docker-compose.yml down