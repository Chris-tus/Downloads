import streamlit as st
from firebase_admin import credentials, storage
import firebase_admin

# Initialize Firebase Admin SDK using credentials from Streamlit secrets
if not firebase_admin._apps:
    firebase_creds = dict(st.secrets["firebase_credentials"])  # Convert AttrDict to a regular dictionary
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'diamond-dotgenerator.firebasestorage.app'
    })

# Firebase Storage Bucket
bucket = storage.bucket()

# Get query parameters from the redirect URL
query_params = st.query_params
redirect_session_id = query_params.get("session_id")
if isinstance(redirect_session_id, list):  # Handle case where session_id is a list
    redirect_session_id = redirect_session_id[0]

# Debugging: Display the query parameters for troubleshooting
st.write("Redirect Session ID:", redirect_session_id)

if redirect_session_id:
    # Check if the ZIP file exists in Firebase
    zip_file_key = f"zips/{redirect_session_id}.zip"
    zip_blob = bucket.blob(zip_file_key)

    if zip_blob.exists():
        # Success message and download button
        st.success("Your payment has been confirmed! Download your file below:", icon="✅")
        st.download_button(
            label="Download Your File",
            data=zip_blob.download_as_bytes(),
            file_name="diamond_dot_template.zip",
            mime="application/zip",
        )
    else:
        st.error("Error: ZIP file not found. Please contact support.")
else:
    st.error("Invalid or missing session ID. Please ensure you followed the correct payment process.")
