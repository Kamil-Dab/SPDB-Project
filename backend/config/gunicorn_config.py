"""Gunicorn configuration."""
import os

bind = "0.0.0.0:5000"

workers = 1
worker_class = "sync"
timeout = 300

accesslog = "-"
