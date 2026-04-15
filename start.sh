#!/bin/bash
PORT=${PORT:-10000}
exec gunicorn --bind 0.0.0.0:$PORT app:app
