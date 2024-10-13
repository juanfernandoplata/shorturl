up:
	docker compose up

down:
	docker compose down

clean: down
	docker rmi shorturl-pg1 || true
	docker rmi shorturl-pg2 || true
	docker rmi shorturl-url-encoder || true
	docker rmi shorturl-api || true

clean-up: clean
	docker compose up