import boto3 
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from google.cloud import firestore


#configure Amazone polly   
polly_client = boto3.Session(
    aws_access_key_id = 'AKIASU566MJXIJLXNJXQ',
    aws_secret_access_key = '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',
    region_name = 'ap-northeast-1'
).client('polly')

#configure firestore database
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'storageBucket': 'app-5-5b64a.firebasestorage.app'  
})
db = firestore.Client()
bucket = storage.bucket()

#configure firebase firestore
from firebase_functions.firestore_fn import (
  on_document_deleted,
  Event,
  DocumentSnapshot,
)

def delete_audio(store_id: str, announcement_id: str) -> None:
    try:
        blob = bucket.blob(f'audio/{store_id}/{announcement_id}.mp3')
        blob.delete()
    except Exception as e:
        print(f"Error deleting audio for announcement {announcement_id}: {e}")

@on_document_deleted(document="store_data/{storeId}/announcement_audio/{announcementId}")
def on_announcement_deleted(event: Event[DocumentSnapshot]) -> None:
    store_id = event.params["storeId"]
    announcement_id = event.params["announcementId"]
    delete_audio(store_id, announcement_id)
