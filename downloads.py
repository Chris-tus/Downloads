import streamlit as st
import firebase_admin
from firebase_admin import credentials, storage
from google.cloud import storage as gcs
import json

# Initialize Firebase Admin SDK using credentials from Streamlit secrets
if not firebase_admin._apps:
    firebase_creds = dict(st.secrets["firebase_credentials"])  # Convert AttrDict to a regular dictionary
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'diamond-dotgenerator.firebasestorage.app'
    })

# Reference Firebase storage bucket
bucket = gcs.Client().bucket("diamond-dotgenerator.firebasestorage.app")

# Parse query parameters
query_params = st.query_params
session_id = query_params.get("session_id", [None])[0]
payment_status = query_params.get("paid", [None])[0]

if session_id and payment_status == "true":
    try:
        # Debug output for session details
        st.write("Session ID:", session_id)
        st.write("Payment Status:", payment_status)

        # Retrieve session data from Firebase to validate and get the associated ZIP file
        stripe_session_key = f"sessions/{session_id}/stripe_session.json"
        session_blob = bucket.blob(stripe_session_key)

        if session_blob.exists():
            # Load the session data
            session_data = session_blob.download_as_string()
            client_reference_id = json.loads(session_data).get("client_reference_id")

            if client_reference_id:
                # Use client_reference_id to locate the ZIP file
                zip_file_key = f"zips/{client_reference_id}.zip"
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
                    st.error(f"Error: ZIP file not found for Client Reference ID: {client_reference_id}")
            else:
                st.error("Client Reference ID is missing from the session data.")
        else:
            st.error("Session not found in Firebase. Please ensure the payment was completed successfully.")
    except Exception as e:
        st.error(f"An error occurred while accessing Firebase: {str(e)}")
else:
    st.error("Invalid or incomplete payment information.")
