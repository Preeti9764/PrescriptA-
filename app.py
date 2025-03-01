import streamlit as st
import base64
import requests
from PIL import Image
from io import BytesIO
from pdf2image import convert_from_bytes
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
import threading
import json
import re
import pandas as pd
import io
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

import pandas as pd


# Check if Firebase is already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("C:\prescripta\prescripta-34da5-firebase-adminsdk-fbsvc-60860691f7.json")  # Use the correct path
    firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

def fetch_all_medicines():
    """Fetch all medicines from Firestore and return as a Pandas DataFrame."""
    medications = db.collection("medications").stream()

    data = []
    for med in medications:
        med_dict = med.to_dict()
        data.append(med_dict)

    # Convert to Pandas DataFrame
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=["name", "brand", "price", "stock"])  # Ensure no error if DB is empty


# Configuration - Replace with your API key
GEMINI_API_KEY = "AIzaSyC56Rakq6bf6hCPTwExkwctgU2kSfVjPEo"
GEMINI_MODEL = "gemini-2.0-flash"  # For document processing
GEMINI_PRO_MODEL = "gemini-2.0-pro"  # For general knowledge queries


def check_medicine_exists(med_name):
    """Check if a medicine exists in Firestore and return its details."""
    doc_ref = db.collection("medications").document(med_name.lower())
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None

def place_order(order_list):
    """Place an order and reduce stock in Firestore."""
    if not order_list:
        st.warning("Order is empty. Please add medicines first!")
        return

    for item in order_list:
        med_name = item["name"]
        quantity = item["quantity"]
        
        # Fetch medicine details again to ensure stock is updated
        med_details = check_medicine_exists(med_name)
        if med_details and med_details["stock"] >= quantity:
            # ✅ Reduce stock in Firestore
            new_stock = med_details["stock"] - quantity
            db.collection("medications").document(med_name.lower()).update({"stock": new_stock})
        else:
            st.error(f"Not enough stock for {med_name}. Only {med_details['stock']} available!")
            return  # Stop order if any item is out of stock

    # ✅ Clear order after placing
    st.session_state.order_list = []
    st.success("Order placed successfully! ✅")


def add_medicine(name, brand, price, stock):
    """Add a new medicine to Firestore."""
    doc_ref = db.collection("medications").document(name.lower())
    doc_ref.set({
        "name": name,
        "brand": brand,
        "price": price,
        "stock": stock
    })

def search_medication(query):
    """Search for a medication in Firestore by name (partial match)."""
    query = query.lower().strip()

    # Ensure we are querying the "medications" collection
    medications_ref = db.collection("medications")
    
    medications = medications_ref.order_by("name").start_at([query]).end_at([query + "\uf8ff"]).stream()
    
    results = []
    for med in medications:
        data = med.to_dict()
        results.append({
            "name": data["name"],
            "brand": data["brand"],
            "price": data["price"],
            "stock": data["stock"]
        })
    
    return results

def remove_medicine(med_name):
    """Remove a medicine from Firestore."""
    try:
        db.collection("medications").document(med_name.lower()).delete()
        st.success(f"{med_name} removed from stock!")
        st.experimental_rerun()  # Refresh UI after deletion
    except Exception as e:
        st.error(f"Error removing medicine: {e}")



# Pharmacy-specific document types
DOCUMENT_TYPES = [
    "Handwritten Prescription", 
    "Electronic Prescription", 
    "Pharmacy Order", 
    "Insurance Card",
    "Medical History", 
    "Allergy Information",
    "Prior Authorization Form",
    "Medication List", 
    "Patient ID", 
    "Others"
]

# Common medications database - would be replaced with a real database
MEDICATION_DATABASE = {
    "lisinopril": {
        "dosages": ["5mg", "10mg", "20mg", "40mg"],
        "forms": ["tablet"],
        "instructions": ["Take once daily", "Take with or without food"],
        "interactions": ["potassium supplements", "spironolactone"],
        "category": "ACE inhibitor"
    },
    "metformin": {
        "dosages": ["500mg", "850mg", "1000mg"],
        "forms": ["tablet", "extended-release"],
        "instructions": ["Take with meals", "Swallow whole if extended-release"],
        "interactions": ["alcohol", "contrast dyes"],
        "category": "Antidiabetic"
    },
    "atorvastatin": {
        "dosages": ["10mg", "20mg", "40mg", "80mg"],
        "forms": ["tablet"],
        "instructions": ["Take at bedtime", "Avoid grapefruit"],
        "interactions": ["clarithromycin", "itraconazole"],
        "category": "Statin"
    },
    "augmentin": {
    "dosages": ["250mg", "500mg", "625mg", "1g"],
    "forms": ["tablet", "oral suspension"],
    "instructions": ["Take with food", "Complete the full course"],
    "interactions": ["alcohol", "probenecid"],
    "category": "Antibiotic"
}
}

# Initialize session state
def initialize_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "processed_doc" not in st.session_state:
        st.session_state.processed_doc = None
    if "doc_preview" not in st.session_state:
        st.session_state.doc_preview = None
    if "reminder_set" not in st.session_state:
        st.session_state.reminder_set = False
    if "prescription_data" not in st.session_state:
        st.session_state.prescription_data = None
    if "order_created" not in st.session_state:
        st.session_state.order_created = False
    if "medication_database" not in st.session_state:
        st.session_state.medication_database = MEDICATION_DATABASE
    if "patient_orders" not in st.session_state:
        st.session_state.patient_orders = []

# File encoding optimized for speed
def encode_file(uploaded_file):
    """Convert file to base64 encoding (optimized)."""
    try:
        file_bytes = uploaded_file.getvalue()

        if uploaded_file.type == "application/pdf":
            images = convert_from_bytes(file_bytes, first_page=1, last_page=1)
            img_byte_arr = BytesIO()
            images[0].save(img_byte_arr, format='JPEG')
            return base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
        elif uploaded_file.type.startswith("image/"):
            return base64.b64encode(file_bytes).decode("utf-8")
        return None
    except Exception as e:
        st.error(f"File processing error: {str(e)}")
        return None               

# Faster API request handling for document analysis
def query_gemini(prompt, image_b64=None, model=GEMINI_MODEL):
    """Query Gemini API efficiently with reduced response time."""
    try:
        url = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        parts = [{"text": prompt}]
        if image_b64:
            parts.append({"inline_data": {"mime_type": "image/jpeg", "data": image_b64}})

        response = requests.post(
            url, json={"contents": [{"parts": parts}]}, timeout=15
        )
        response.raise_for_status()
        return response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

# Process prescription document
def process_prescription():
    """Process uploaded prescription document and extract medication details."""
    uploaded_file = st.session_state.uploaded_file
    if not uploaded_file:
        return

    with st.spinner("Processing prescription..."):
        image_b64 = encode_file(uploaded_file)
        if not image_b64:
            st.error("Could not process this file type. Please upload an image or PDF.")
            return

        # Generate preview
        if uploaded_file.type == "application/pdf":
            images = convert_from_bytes(uploaded_file.getvalue(), first_page=1, last_page=1)
            st.session_state.doc_preview = images[0]
        else:
            st.session_state.doc_preview = Image.open(uploaded_file)

        # Classify document type
        doc_type_prompt = f"Classify this document into: {DOCUMENT_TYPES}. Respond with only the category name."
        doc_type = query_gemini(doc_type_prompt, image_b64)
        
        # Generate detailed prescription extraction prompt
        extraction_prompt = """
        Extract the following information from this prescription:
        1. Patient Name
        2. Patient Date of Birth or Age
        3. Patient ID (if available)
        4. Doctor Name
        5. Date of Prescription
        6. Medication Name(s)
        7. Dosage(s)
        8. Instructions
        9. Quantity
        10. Refills
        
        Format the response as a JSON object with these fields. If information is not available, use null.
        """
        
        # Extract prescription data
        prescription_raw = query_gemini(extraction_prompt, image_b64)
        
        # Process the extraction to ensure it's valid JSON
        try:
            # Extract the JSON part if the response contains explanatory text
            json_match = re.search(r'```json\n(.*?)\n```', prescription_raw, re.DOTALL)
            if json_match:
                prescription_json = json_match.group(1)
            else:
                prescription_json = prescription_raw
                
            prescription_data = json.loads("prescription_json")
            
            # Create a simplified summary for display
            if isinstance(prescription_data, dict):
                summary = f"**Patient**: {prescription_data.get('Patient Name', 'Unknown')}\n"
                summary += f"**Medication**: {prescription_data.get('Medication Name(s)', 'Unknown')}\n"
                summary += f"**Dosage**: {prescription_data.get('Dosage(s)', 'Unknown')}\n"
                summary += f"**Instructions**: {prescription_data.get('Instructions', 'Unknown')}\n"
                summary += f"**Quantity**: {prescription_data.get('Quantity', 'Unknown')}\n"
                summary += f"**Refills**: {prescription_data.get('Refills', 'Unknown')}"
            else:
                summary = "Could not parse prescription data correctly."
                prescription_data = {}
            
            st.session_state.processed_doc = {
                "type": doc_type or "Unknown Document", 
                "content": image_b64, 
                "summary": summary
            }
            st.session_state.prescription_data = prescription_data
        except json.JSONDecodeError:
            # If JSON parsing fails, try a simpler approach
            summary_prompt = "Summarize this prescription with patient name, medication, dosage, and instructions."
            summary = query_gemini(summary_prompt, image_b64)
            st.session_state.processed_doc = {
                "type": doc_type or "Unknown Document", 
                "content": image_b64, 
                "summary": summary
            }
            st.session_state.prescription_data = {"Summary": summary}

# Create a medication order from prescription
def create_medication_order():
    """Create a medication order from prescription data."""
    if not st.session_state.prescription_data:
        st.error("No prescription data available. Please upload a prescription first.")
        return
    
    # Extract medication information
    prescription = st.session_state.prescription_data
    medication_name = prescription.get("Medication Name(s)", "")
    
    # Match against medication database (would integrate with a real pharmacy system)
    medication_details = {}
    if medication_name:
        # Convert to lowercase and remove common suffixes for matching
        normalized_name = re.sub(r'\s+\d+mg|\s+\d+mcg|\s+\d+ml', '', medication_name.lower())
        
        # Look for partial matches in the database
        for med_name, details in st.session_state.medication_database.items():
            if med_name in normalized_name or normalized_name in med_name:
                medication_details = details
                break
    
    # Create order details
    order = {
        "patient_name": prescription.get("Patient Name", "Unknown"),
        "patient_id": prescription.get("Patient ID", "Unknown"),
        "medication": medication_name,
        "dosage": prescription.get("Dosage(s)", "Unknown"),
        "instructions": prescription.get("Instructions", "Unknown"),
        "quantity": prescription.get("Quantity", "Unknown"),
        "refills": prescription.get("Refills", "0"),
        "status": "Ready for Review",
        "created_date": time.strftime("%Y-%m-%d"),
    }
    
    # Add medication details from database if available
    if medication_details:
        order["alternatives"] = medication_details.get("forms", [])
        order["interactions"] = medication_details.get("interactions", [])
        order["category"] = medication_details.get("category", "Unknown")
    
    # Add the order to the list
    st.session_state.patient_orders.append(order)
    st.session_state.order_created = True
    
    return order

# Handle both document-specific and general queries
def handle_chat_query():
    """Process user queries with enhanced capabilities."""
    user_input = st.session_state.chat_input
    if not user_input:
        return
    
    st.session_state.chat_history.append(("user", user_input))
    
    # Determine query type and context
    if st.session_state.processed_doc and any(keyword in user_input.lower() for keyword in 
                                           ["prescription", "document", "medicine", "dosage", "patient", "this"]):
        # Query related to the uploaded document
        prompt = f"""
        Context: You are a pharmacist assistant.
        Document Type: {st.session_state.processed_doc['type']}
        Document Summary: {st.session_state.processed_doc['summary']}
        
        Question: {user_input}
        
        Answer the question providing specific information from the prescription if available.
        If asked about drug interactions, dosing, or side effects, provide accurate pharmaceutical information.
        """
        response = query_gemini(prompt, st.session_state.processed_doc['content'], model=GEMINI_PRO_MODEL)
    else:
        # General pharmacy or medication query
        prompt = f"""
        Context: You are a pharmacist assistant with expertise in medications, drug interactions, 
        dosing guidelines, and pharmacy procedures.
        
        Question: {user_input}
        
        Provide a helpful, accurate response from a pharmaceutical perspective.
        """
        response = query_gemini(prompt, model=GEMINI_PRO_MODEL)
    
    st.session_state.chat_history.append(("assistant", response or "Could not generate response"))

# Medicine reminder email
def send_email_reminder(email, message):
    """Send an email reminder."""
    try:
        sender_email = "pharmacyreminder@example.com"  # Replace with actual email
        sender_password = "password"  # Replace with actual password

        msg = MIMEMultipart()
        msg["From"], msg["To"], msg["Subject"] = sender_email, email, "Medication Reminder"
        msg.attach(MIMEText(message, "plain"))

        # This would be replaced with actual SMTP server details
        with smtplib.SMTP("127.0.0.1", 1025) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)
            smtp.sendmail(sender_email, email, msg.as_string())

        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

# Schedule medicine reminder
def schedule_reminder(email, time_str, message, medication=None):
    """Schedule a medication reminder email."""
    try:
        if medication:
            message = f"Reminder to take your {medication}: {message}"
            
        schedule.every().day.at(time_str).do(send_email_reminder, email, message)

        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        # Start scheduler in background thread
        threading.Thread(target=run_scheduler, daemon=True).start()
        st.session_state.reminder_set = True
        return True
    except Exception as e:
        st.error(f"Failed to set reminder: {str(e)}")
        return False

# Search medications in database
def search_medication(query):
    """Search for medication in the database."""
    results = []
    query = query.lower()
    
    for name, details in st.session_state.medication_database.items():
        if query in name.lower():
            results.append({
                "name": name,
                "category": details["category"],
                "dosages": ", ".join(details["dosages"]),
                "forms": ", ".join(details["forms"])
            })
    
    return results

# Export orders to CSV
def export_orders_to_csv():
    """Export all patient orders to a CSV file."""
    if not st.session_state.patient_orders:
        st.error("No orders to export.")
        return None
        
    df = pd.DataFrame(st.session_state.patient_orders)
    csv = df.to_csv(index=False)
    return csv

# UI Layout


def main():
    st.set_page_config(page_title="Pharmacist's Assistant", layout="wide")
    
    # Apply custom CSS for background and styling
    st.markdown("""
        <style>
            body {
                background: linear-gradient(to right, black, yellow);
            }
            .stButton > button {
                background-color: #FFD700;
                color: black;
                font-size: 16px;
                border-radius: 8px;
                padding: 10px;
            }
            .stButton > button:hover {
                background-color: #FFC107;
            }
            .stTabs [data-baseweb="tab-list"] {
                background-color: #333;
                border-radius: 8px;
                padding: 5px;
            }
            .stTabs [data-baseweb="tab"] {
                color: yellow;
            }
            .title-text {
                text-align: center;
                color: dark blue;
                font-size: 48px;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)
    
    initialize_session_state()

    st.markdown("<div class='title-text'>PrescriptA</div>", unsafe_allow_html=True)

    # Sidebar for chat functionality
    with st.sidebar:
        st.header("PharmBot")
        for role, message in st.session_state.chat_history:
            with st.chat_message(role):
                st.markdown(message)
        st.chat_input("Ask a pharmaceutical question...", key="chat_input", on_submit=handle_chat_query)
    
    # Main area
    tab1, tab2, tab3, tab4 = st.tabs(["Prescription & Analysis", "Medication Database", "Orders", "MediClock"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Upload & Prescription Analysis")
            uploaded_file = st.file_uploader("Upload Prescription", type=["pdf", "png", "jpg", "jpeg"], key="uploaded_file", on_change=process_prescription)
            
            if st.session_state.processed_doc:
                st.subheader("Analysis")
                st.markdown(st.session_state.processed_doc["summary"])
                if st.session_state.prescription_data and isinstance(st.session_state.prescription_data, dict):
                    prescription = st.session_state.prescription_data
                    if "Medication Name(s)" in prescription and prescription["Medication Name(s)"]:
                        med_name = prescription["Medication Name(s)"]
                        interaction_prompt = f"""
                        As a pharmacist, review this prescription for {med_name} with dosage {prescription.get('Dosage(s)', 'unknown')}.
                        Identify any potential issues, interactions, or warnings that should be considered.
                        Focus on practical pharmaceutical concerns.
                        """
                        analysis = query_gemini(interaction_prompt, model=GEMINI_PRO_MODEL)
                        st.subheader("Pharmacist Analysis")
                        st.markdown(analysis)
            else:
                st.info("Please upload a prescription document to begin analysis")
        
        with col2:
            if st.session_state.doc_preview:
                st.subheader("Prescription Preview")
                st.image(st.session_state.doc_preview, use_container_width=True)

    with tab2:
        st.subheader("📋 Medication Database")

        # ✅ Fetch data from Firestore
        df = fetch_all_medicines()

        # ✅ Ensure df is always a DataFrame
        if df is None or df.empty:
            df = pd.DataFrame(columns=["name", "brand", "price", "stock"])
            st.info("No medicines available in the database.")

        # ✅ "Add New Medicine" Section (Always Visible)
        with st.expander("➕ Add New Medicine"):
            med_name = st.text_input("Medicine Name")
            med_brand = st.text_input("Brand Name")
            med_price = st.number_input("Price per unit", min_value=0.0, step=0.1)
            med_stock = st.number_input("Stock Available", min_value=0, step=1)

            if st.button("Add Medicine"):
                add_medicine(med_name, med_brand, med_price, med_stock)

        # ✅ Search Bar (Filters Table)
        search_query = st.text_input("🔍 Search Medications", placeholder="Enter medicine name...")

        if not df.empty and search_query:
            df = df[df["name"].str.contains(search_query, case=False, na=False)]

        # ✅ Display Table with Streamlit Buttons for Deletion
        if not df.empty:
            st.write("### Medicine Stock")
            for index, row in df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 2, 1])  # Adjust column sizes
                col1.write(f"**{row['name']}**")
                col2.write(row["brand"])
                col3.write(f"₹{row['price']:.2f}")
                col4.write(f"{row['stock']} units")

                # ✅ Fix: Use Streamlit Button Instead of HTML
                if col5.button("🗑️", key=f"del_{row['name']}"):
                    remove_medicine(row["name"])

        else:
            st.info("No medicines available in the database.")

 
    with tab3:
        st.subheader("🛒 Orders")

        # ✅ Initialize order list in session state if not exists
        if "order_list" not in st.session_state:
            st.session_state.order_list = []

        # ✅ Medicine Selection Inputs
        med_name = st.text_input("Enter Medicine Name")
        med_quantity = st.number_input("Enter Quantity", min_value=1, step=1)

        if st.button("➕ Add to Order"):
            med_details = check_medicine_exists(med_name)

            if med_details:
                if med_quantity <= med_details["stock"]:
                    # ✅ Add to session state order list
                    st.session_state.order_list.append({
                        "name": med_name,
                        "quantity": med_quantity,
                        "price": med_details["price"] * med_quantity
                    })
                    st.success(f"{med_quantity} units of {med_name} added to order! ✅")
                else:
                    st.error(f"Only {med_details['stock']} units available!")
            else:
                st.error("Medicine not found in stock!")

        # ✅ Display Order Summary
        if st.session_state.order_list:
            st.write("### 📝 Order Summary")
            total_price = sum(item["price"] for item in st.session_state.order_list)

            # ✅ Display Table
            order_df = pd.DataFrame(st.session_state.order_list)
            st.dataframe(order_df, use_container_width=True)

            # ✅ Place Order Button
            if st.button("✅ Place Order"):
                place_order(st.session_state.order_list)

        else:
            st.info("No items in the order. Add medicines to order!")

    
    with tab4:
        st.subheader("MediClock")
        with st.form("reminder_form"):
            st.write("Set Medication Reminder")
            patient_email = st.text_input("Patient Email")
            reminder_time = st.time_input("Reminder Time")
            medication = st.text_input("Medication Name")
            reminder_msg = st.text_area("Additional Instructions")
            submitted = st.form_submit_button("Set Reminder")
            if submitted:
                time_str = reminder_time.strftime("%H:%M")
                success = schedule_reminder(patient_email, time_str, reminder_msg, medication)
                if success:
                    st.success("Reminder scheduled successfully!")

if __name__ == "__main__":
    main()
