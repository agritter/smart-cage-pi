import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore import Client as FirestoreClient
import os


class Firestore:
    # todo can relative?
    _CREDENTIALSPATH = "/home/goldfinch8/smart-cage/smartcage8-firebase-adminsdk-m8ex1-146e511469.json"

    def __init__(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self._CREDENTIALSPATH
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
        self.db: FirestoreClient = firestore.client()

    def getLightDocument(self):
        return self.db.collection("status").document("light")

    def getAudioDocument(self):
        return self.db.collection("status").document("audio")
