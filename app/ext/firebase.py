import json
import os

import firebase_admin
from firebase_admin import credentials, storage


def setup() -> None:
    cert = json.loads(os.getenv("FIREBASE_CREDENTIALS_JSON"), strict=False)
    cred = credentials.Certificate(cert)
    firebase_admin.initialize_app(
        cred,
        {"storageBucket": "trabajo-profesional-51243.appspot.com"},
    )
    bucket = storage.bucket()
    bucket.make_public()


def upload_image(folder, content_type, file, id) -> str:
    bucket = storage.bucket()
    blob = bucket.blob(f"{folder}/{id}")
    blob.upload_from_file(file_obj=file, content_type=content_type)
    blob.make_public()

    return blob.public_url


def delete_image(folder, id):
    bucket = storage.bucket()
    blob = bucket.blob(f"{folder}/{id}")
    blob.delete()
