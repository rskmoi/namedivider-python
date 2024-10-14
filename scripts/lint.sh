set -e
set -x

mypy namedivider
ruff check namedivider tests
black namedivider tests --check