import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore import Client as FirestoreClient
import os


class Firestore:
    _CREDENTIALS_PATH = "./smartcage8-firebase-adminsdk-m8ex1-146e511469.json"

    def __init__(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self._CREDENTIALS_PATH
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
        self.db: FirestoreClient = firestore.client()

    def get_light_document(self):
        return self.db.collection("status").document("light")

    def get_audio_document(self):
        return self.db.collection("status").document("audio")
