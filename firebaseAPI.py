import os
import firebase_admin
from firebase_admin import credentials, firestore
from store import set_shopify_credentials, set_shiprocket_credentials
import streamlit as st

# Firebase Configuration
firebase_config = {
  "type": os.environ.get("type"),
  "project_id": os.environ.get("project_id"),
  "private_key_id": os.environ.get("private_key_id"),
  "private_key": os.environ.get("private_key"),
  "client_email": os.environ.get("client_email"),
  "client_id": os.environ.get("client_id"),
  "auth_uri": os.environ.get("auth_uri"),
  "token_uri": os.environ.get("token_uri"),
  "auth_provider_x509_cert_url": os.environ.get("auth_provider_x509_cert_url"),
  "client_x509_cert_url": os.environ.get("client_x509_cert_url"),
  "universe_domain": os.environ.get("universe_domain")
}


def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)

@st.cache_data
def fetch_credentials_from_firebase(password):
    db = firestore.client()
    doc_ref = db.collection('Users').document(password)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        set_shopify_credentials(data.get('API_KEY'),data.get('PASSWORD'),data.get('SHOP_NAME'))
        set_shiprocket_credentials(data.get('email'),data.get('password'))
    else:
        raise ValueError("Invalid Password")