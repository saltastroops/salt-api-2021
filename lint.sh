black saltapi tests && \
isort saltapi tests && \
flake8 saltapi tests && \
mypy saltapi && \
pytest
