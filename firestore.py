import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore import Client as FirestoreClient
import os


class Firestore:
    """
        Handles connecting to Firestore
    """
    _CREDENTIALS_PATH = "./smartcage8-firebase-adminsdk-m8ex1-146e511469.json"

    def __init__(self):
        """
            Initialize the Firestore app
        """
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self._CREDENTIALS_PATH
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
        self._db: FirestoreClient = firestore.client()

    def get_light_document(self):
        """
            Returns a reference to the document with light information
        """
        return self._db.collection("status").document("light")

    def get_audio_document(self):
        """
            Returns a reference to the document with audio information
        """
        return self._db.collection("status").document("audio")

    def cleanup(self):
        """
            Cleans up resources used by Firestore
        """
        self._db.close()
