#!/bin/sh
alembic upgrade b9497af71930
alembic upgrade 1b3fadd0c80b

exec python src/main.py