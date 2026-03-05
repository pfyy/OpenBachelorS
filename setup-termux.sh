set -euo pipefail

pkg upgrade -y

pkg install -y git
pkg install -y python python-pip
pkg install -y rust
pkg install -y binutils
pkg install -y aria2
pkg install -y postgresql

export ANDROID_API_LEVEL=24

pip install pipx
pipx install poetry
pipx ensurepath

poetry config installer.max-workers 1

poetry install || true
poetry run pip install psycopg[c]
poetry install --only-root
