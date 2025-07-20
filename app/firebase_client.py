# app/firebase_client.py  (create if you don't have one yet)
import os
import firebase_admin
from firebase_admin import credentials, auth   # pip install firebase-admin

# Path injected by Cloud Run
sa_path = os.environ["FIREBASE_SA"]            # '/var/secrets/google/firebase-sa'

cred = credentials.Certificate(sa_path)
firebase_admin.initialize_app(cred)
