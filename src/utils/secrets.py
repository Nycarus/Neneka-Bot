import os
import hashlib
from google.cloud import secretmanager

def access_secret_version(secret_id, version_id="latest"):
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{os.getenv('PROJECT_ID')}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(name=name)

    # Return the decoded payload.
    return response.payload.data.decode('UTF-8')

def secret_hash(secret_value): 
  # return the sha224 hash of the secret value
  return hashlib.sha224(bytes(secret_value, "utf-8")).hexdigest()