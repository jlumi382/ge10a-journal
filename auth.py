from flask_httpauth import HTTPBasicAuth
import os

auth = HTTPBasicAuth()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
