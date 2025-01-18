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

import streamlit as st

# Get query parameters
query_params = st.experimental_get_query_params()

# Extract client_reference_id
client_reference_id = query_params.get("client_reference_id", [None])[0]
session_id = query_params.get("session_id", [None])[0]
paid = query_params.get("paid", ["false"])[0].lower() == "true"

# Debugging output
st.write("Client Reference ID:", client_reference_id)
st.write("Session ID:", session_id)
st.write("Paid:", paid)

if paid and client_reference_id:
    # Validate the client_reference_id with Firebase (optional)
    bucket = storage.bucket()
    stripe_session_key = f"sessions/{client_reference_id}/stripe_session.json"
    blob = bucket.blob(stripe_session_key)
    if blob.exists():
        # Retrieve the stored session data
        session_data = json.loads(blob.download_as_string())
        if session_data.get("session_id") == client_reference_id:
            st.success("Payment confirmed! Your file is ready to download.")
            # Generate download button for the ZIP file
            zip_key = f"zips/{client_reference_id}.zip"
            zip_blob = bucket.blob(zip_key)
            if zip_blob.exists():
                st.download_button(
                    label="Download Your File",
                    data=zip_blob.download_as_bytes(),
                    file_name="diamond_dot_template.zip",
                    mime="application/zip",
                )
            else:
                st.error("Error: ZIP file not found.")
        else:
            st.error("Invalid session ID.")
    else:
        st.error("Session not found. Please contact support.")
else:
    st.error("Payment not confirmed or session ID missing.")
