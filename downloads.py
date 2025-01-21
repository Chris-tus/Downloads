import streamlit as st
import firebase_admin
from firebase_admin import credentials, storage
import json

# Firebase Admin Initialization
st.write("Initializing Firebase Admin...")
if not firebase_admin._apps:
    firebase_creds = dict(st.secrets["firebase_credentials"])
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'diamond-dotgenerator.firebasestorage.app',
        'projectId': firebase_creds.get('project_id')  # Ensure project_id is included
    })
    st.write("Firebase Admin initialized successfully.")
else:
    st.write("Firebase Admin already initialized.")

# Google Cloud Storage Bucket Reference
bucket = storage.bucket()
st.write(f"Bucket reference obtained: {bucket.name}")

# Parse query parameters
st.write("Parsing query parameters...")
query_params = st.experimental_get_query_params()  # Correctly handle query parameters

# Extract session_id and payment_status
session_id = query_params.get("session_id", [None])[0]  # Retrieve session_id or set to None
payment_status = query_params.get("paid", [None])[0]  # Retrieve paid status or set to None

st.write("Parsed query parameters:")
st.write("Session ID:", session_id)
st.write("Payment Status:", payment_status)

# Ensure both parameters are not None and payment_status is "true"
if session_id and payment_status == "true":
    try:
        st.write("Validating session in Firebase...")

        # Retrieve session data from Firebase to validate and get the associated ZIP file
        stripe_session_key = f"sessions/{session_id}/stripe_session.json"
        st.write(f"Looking for session data at: {stripe_session_key}")
        session_blob = bucket.blob(stripe_session_key)

        if session_blob.exists():
            st.write("Session data found. Loading session details...")
            session_data = json.loads(session_blob.download_as_string())
            client_reference_id = session_data.get("client_reference_id")

            # Validate that the client_reference_id matches the session_id
            if client_reference_id == session_id:
                st.write("Session ID validated. Locating ZIP file...")
                # Use the session_id (client_reference_id) to locate the ZIP file
                zip_file_key = f"zips/{session_id}.zip"
                st.write(f"Looking for ZIP file at: {zip_file_key}")
                zip_blob = bucket.blob(zip_file_key)

                if zip_blob.exists():
                    st.write("ZIP file found. Preparing download button...")
                    # Offer the file for download
                    st.download_button(
                        label="Download Your File",
                        data=zip_blob.download_as_bytes(),
                        file_name="diamond_dot_template.zip",
                        mime="application/zip",
                    )
                else:
                    st.error(f"Error: ZIP file not found for Session ID: {session_id}")
            else:
                st.error("Session ID mismatch. Unable to validate the payment.")
        else:
            st.error("Session data not found in Firebase. Please ensure the payment was completed successfully.")
    except Exception as e:
        st.error(f"An error occurred while accessing Firebase: {str(e)}")
else:
    st.error("Payment status is invalid or missing.")
