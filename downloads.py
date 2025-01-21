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
st.write("Firebase Admin initialized successfully.")

# Google Cloud Storage Bucket Reference
bucket = storage.bucket()
st.write("Bucket reference obtained:", bucket.name)

# Parse query parameters
query_params = st.query_params
session_id = query_params.get("session_id", [None])[0]  # Stripe's session_id from redirect URL
payment_status = query_params.get("paid", [None])[0]  # Paid status from redirect URL

st.write("Parsed query parameters:")
st.write("Session ID:", session_id)
st.write("Payment Status:", payment_status)

if session_id and payment_status == "true":
    st.write("Payment status is valid. Proceeding to retrieve session data...")
    try:
        # Retrieve session data from Firebase to validate and get the associated ZIP file
        stripe_session_key = f"sessions/{session_id}/stripe_session.json"
        st.write(f"Looking for session data in Firebase at key: {stripe_session_key}")

        session_blob = bucket.blob(stripe_session_key)

        if session_blob.exists():
            st.write(f"Session data found for key: {stripe_session_key}")
            # Load the session data
            session_data = json.loads(session_blob.download_as_string())
            client_reference_id = session_data.get("client_reference_id")

            st.write("Loaded session data:", session_data)
            st.write("Client Reference ID from session data:", client_reference_id)

            # Validate that the client_reference_id matches the session_id
            if client_reference_id == session_id:
                st.write("Client Reference ID matches Session ID. Proceeding to locate ZIP file...")
                # Use the session_id (client_reference_id) to locate the ZIP file
                zip_file_key = f"zips/{session_id}.zip"
                st.write(f"Looking for ZIP file in Firebase at key: {zip_file_key}")

                zip_blob = bucket.blob(zip_file_key)

                if zip_blob.exists():
                    st.write(f"ZIP file found: {zip_file_key}. Preparing download button...")
                    # Offer the file for download
                    st.download_button(
                        label="Download Your File",
                        data=zip_blob.download_as_bytes(),
                        file_name="diamond_dot_template.zip",
                        mime="application/zip",
                    )
                else:
                    st.error(f"Error: ZIP file not found at key: {zip_file_key}")
            else:
                st.error("Session ID mismatch. Unable to validate the payment.")
        else:
            st.error(f"Session data not found at key: {stripe_session_key}. Please ensure the payment was completed successfully.")
    except Exception as e:
        st.error(f"An error occurred while accessing Firebase: {str(e)}")
else:
    if not session_id:
        st.error("Session ID is missing from the URL.")
    if payment_status != "true":
        st.error("Payment status is invalid or missing.")
