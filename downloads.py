import streamlit as st
from google.cloud import storage

# Initialize Firebase Storage
bucket_name = st.secrets["firebase_credentials"]["project_id"] + ".appspot.com"
bucket = storage.Client().bucket(bucket_name)

# Parse query parameters
query_params = st.query_params
session_id = query_params.get("session_id", [None])[0]
payment_status = query_params.get("paid", [None])[0]

if session_id and payment_status == "true":
    try:
        # Debug output
        st.write("Session ID:", session_id)
        st.write("Paid:", payment_status)

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
            st.error("Error: ZIP file not found.")
    except Exception as e:
        st.error(f"Error accessing Firebase: {str(e)}")
else:
    st.error("Invalid or incomplete payment information.")
