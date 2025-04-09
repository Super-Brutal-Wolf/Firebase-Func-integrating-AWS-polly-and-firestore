import boto3 
import tempfile
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
  on_document_created,
  Event,
  DocumentSnapshot,
)

def generate_and_upload_audio(store_id: str, announcement_id: str, content: str) -> None:
    try:
        response = polly_client.synthesize_speech(
            Text=content,
            OutputFormat='mp3',
            VoiceId='Joanna',
            Engine='neural'
        )
    except Exception as e:
        print(e)
        exit()

    # Save audio to a temporary file
    temp_file =  tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    temp_file.write(response['AudioStream'].read())
    temp_file.close()

    # Upload audio to Firebase Storage
    blob = bucket.blob(f'audio/{store_id}/{announcement_id}.mp3')
    blob.upload_from_filename(temp_file.name)

@on_document_created(document="store_data/{storeId}/announcement_audio/{announcementId}")
def on_announcement_created(event: Event[DocumentSnapshot]) -> None:
    store_id = event.params["storeId"]
    announcement_id = event.params["announcementId"]
    content = event.data.get("content")
    if content:
        generate_and_upload_audio(store_id, announcement_id, content)
