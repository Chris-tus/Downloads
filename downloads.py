import streamlit as st
import firebase_admin
from firebase_admin import credentials, storage
import json

# Firebase Admin Initialization
if not firebase_admin._apps:
    try:
        firebase_creds = dict(st.secrets["firebase_credentials"])
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'diamond-dotgenerator.firebasestorage.app', 
            'projectId': firebase_creds.get('project_id')  # Ensure project_id is included
        })
        st.write("Firebase initialized successfully.")
    except Exception as e:
        st.error(f"Failed to initialize Firebase: {e}")
        st.stop()

# Google Cloud Storage Bucket Reference
try:
    bucket = storage.bucket()  # Uses the default bucket from Firebase Admin initialization
    st.write("Storage bucket reference acquired.")
except Exception as e:
    st.error(f"Failed to reference Firebase Storage bucket: {e}")
    st.stop()

# Parse query parameters
query_params = st.query_params
session_id = query_params.get("session_id", [None])[0]  # Stripe's session_id from redirect URL
payment_status = query_params.get("paid", [None])[0]  # Paid status from redirect URL

if not session_id or payment_status != "true":
    st.error("Invalid or incomplete payment information.")
    st.stop()

try:
    # Debugging: Display session details
    st.write("Session ID:", session_id)
    st.write("Payment Status:", payment_status)

    # Directly locate the ZIP file using the session_id
    zip_file_key = f"zips/{session_id}.zip"
    st.write(f"Looking for file: {zip_file_key}")
    zip_blob = bucket.blob(zip_file_key)

    if zip_blob.exists():
        st.write(f"File found: {zip_file_key}")
        # Offer the ZIP file for download
        st.download_button(
            label="Download Your File",
            data=zip_blob.download_as_bytes(),
            file_name="diamond_dot_template.zip",
            mime="application/zip",
        )
    else:
        st.error(f"File not found: {zip_file_key}. Double-check if the file exists in Firebase.")
except Exception as e:
    st.error(f"An error occurred while accessing Firebase: {e}")
