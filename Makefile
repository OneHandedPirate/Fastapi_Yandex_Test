create_env:
	touch .env
	echo 'DB__USER="postgres"\nDB__PASSWORD="postgres"\nDB__NAME="yandex_music_test"\nDB__HOST="postgres"\nDB__OUTER_PORT="5432"\nADMIN_EMAILS=[]\nDEV__HOST="0.0.0.0"\nYANDEX__CLIENT_ID=""\nYANDEX__CLIENT_SECRET=""'> .env

start:
	docker compose up --build