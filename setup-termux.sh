pkg upgrade

pkg install git
pkg install python python-pip
pkg install rust
pkg install aria2
pkg install postgresql

export ANDROID_API_LEVEL=24

pip install pipx
pipx install poetry
pipx ensurepath

poetry config installer.max-workers 1

poetry install || true
poetry run pip install psycopg[c]
poetry install --only-root
