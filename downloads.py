import streamlit as st
import firebase_admin
from firebase_admin import credentials, storage

# Initialize Firebase Admin SDK using credentials from Streamlit secrets
if not firebase_admin._apps:
    firebase_creds = dict(st.secrets["firebase_credentials"])  # Convert AttrDict to a regular dictionary
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'diamond-dotgenerator.firebasestorage.app'
    })

# Parse query parameters
query_params = st.query_params
session_id = query_params.get("session_id", [None])[0]
payment_status = query_params.get("paid", [None])[0]

if session_id and payment_status == "true":
    try:
        # Debug output
        st.write("Session ID:", session_id)
        st.write("Paid:", payment_status)

        # Reference the Firebase storage bucket
        bucket = storage.bucket()

        # Use the session_id to retrieve the ZIP file from Firebase
        zip_file_key = f"zips/{session_id}.zip"
        zip_blob = bucket.blob(zip_file_key)

        if zip_blob.exists():
            # Offer the file for download
            st.download_button(
                label="Download Your File",
                data=zip_blob.download_as_bytes(),
                file_name="diamond_dot_template.zip",
                mime="application/zip",
            )
        else:
            st.error(f"Error: ZIP file not found for Session ID: {session_id}")
    except Exception as e:
        st.error(f"Error accessing Firebase: {str(e)}")
else:
    st.error("Invalid or incomplete payment information.")
