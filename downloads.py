import streamlit as st
import firebase_admin
from firebase_admin import credentials, storage
import json

# Firebase Admin Initialization
if not firebase_admin._apps:
    firebase_creds = dict(st.secrets["firebase_credentials"])
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'diamond-dotgenerator.firebasestorage.app',
        'projectId': firebase_creds.get('project_id')  # Ensure project_id is included
    })

# Google Cloud Storage Bucket Reference
bucket = storage.bucket()

# Parse query parameters
query_params = st.query_params.to_dict()  # Use the new st.query_params API

# Extract session_id and payment_status
session_id = query_params.get("session_id", None)
payment_status = query_params.get("paid", None)

# Simple user-friendly feedback messages
if session_id and payment_status == "true":
    st.info("Verifying payment...")

    try:
        # Retrieve session data from Firebase to validate and get the associated ZIP file
        stripe_session_key = f"sessions/{session_id}/stripe_session.json"
        session_blob = bucket.blob(stripe_session_key)

        if session_blob.exists():
            session_data = json.loads(session_blob.download_as_string())
            client_reference_id = session_data.get("client_reference_id")

            # Validate that the client_reference_id matches the session_id
            if client_reference_id == session_id:
                st.info("Fetching your file...")

                # Use the session_id (client_reference_id) to locate the ZIP file
                zip_file_key = f"zips/{session_id}.zip"
                zip_blob = bucket.blob(zip_file_key)

                if zip_blob.exists():
                    st.success("Your file is ready for download!")
                    # Offer the file for download
                    st.download_button(
                        label="Download Your File",
                        data=zip_blob.download_as_bytes(),
                        file_name="diamond_dot_template.zip",
                        mime="application/zip",
                    )
                else:
                    st.error("We couldn't find your file. Please contact support.")
            else:
                st.error("We couldn't validate your payment. Please contact support.")
        else:
            st.error("Your session data is missing. Please ensure the payment was successful.")
    except Exception as e:
        st.error("An error occurred while processing your request. Please try again later.")
else:
    st.error("Invalid payment details. Please check your payment and try again.")
