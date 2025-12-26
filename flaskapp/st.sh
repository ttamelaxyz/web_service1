#!/bin/bash
cd "$(dirname "$0")"
gunicorn --bind 127.0.0.1:5000 wsgi:app
