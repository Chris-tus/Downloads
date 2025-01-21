import streamlit as st
import firebase_admin
from firebase_admin import credentials, storage
import stripe

# Initialize Firebase Admin SDK using credentials from Streamlit secrets
if not firebase_admin._apps:
    firebase_creds = dict(st.secrets["firebase_credentials"])  # Convert AttrDict to a regular dictionary
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'diamond-dotgenerator.firebasestorage.app'
    })

# Stripe API key from Streamlit secrets
stripe.api_key = st.secrets["stripe_secret_key"]

# Parse query parameters
query_params = st.query_params
stripe_session_id = query_params.get("session_id", [None])[0]
payment_status = query_params.get("paid", [None])[0]

if stripe_session_id and payment_status == "true":
    try:
        # Retrieve the Stripe Checkout Session
        checkout_session = stripe.checkout.Session.retrieve(stripe_session_id)

        # Extract the client_reference_id from metadata
        client_reference_id = checkout_session.metadata.get("client_reference_id")

        # Debug output
        st.write("Client Reference ID:", client_reference_id)
        st.write("Stripe Session ID:", stripe_session_id)
        st.write("Paid:", payment_status)

        if client_reference_id:
            # Reference the Firebase storage bucket
            bucket = storage.bucket()

            # Use the client_reference_id to retrieve the ZIP file
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
            st.error("Client Reference ID not found in session metadata.")
    except Exception as e:
        st.error(f"Error retrieving session from Stripe: {str(e)}")
else:
    st.error("Invalid or incomplete payment information.")
