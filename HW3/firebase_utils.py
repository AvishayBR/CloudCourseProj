from firebase_admin import storage

# Function to upload file to Firebase Storage
def upload_to_firebase(filename, content):
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_string(content)
    return blob.public_url

# Function to get files from Firebase Storage
def get_files_from_firebase():
    bucket = storage.bucket()
    blobs = bucket.list_blobs()
    files = [blob.name for blob in blobs]
    return files

# Function to download file from Firebase Storage
def download_from_firebase(filename):
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    content = blob.download_as_text()
    return content
