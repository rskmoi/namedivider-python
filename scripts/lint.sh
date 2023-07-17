set -e
set -x

mypy namedivider
ruff namedivider tests
black namedivider tests --check