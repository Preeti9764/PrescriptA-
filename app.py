import streamlit as st
import random
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

# Configuration - Replace with your API key
GEMINI_API_KEY = "AIzaSyAXbWZl8H5qyqXtqi5Be1G6xyfJW3ES__A"
GEMINI_MODEL = "gemini-2.0-flash"  # For document processing
GEMINI_PRO_MODEL = "gemini-2.0-pro"  # For general knowledge queries

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

# Common medications database - with added medications
MEDICATION_DATABASE = {
    "augmentin": {
        "dosages": ["625mg"],
        "forms": ["tablet"],
        "instructions": ["Take twice a day after meals"],
        "interactions": ["alcohol", "probenecid"],
        "category": "Antibiotic"
    },
    "enzoflam": {
        "dosages": ["tablet"],
        "forms": ["tablet"],
        "instructions": ["Take twice daily (morning and night) after meals for 5 days"],
        "interactions": ["alcohol", "NSAIDs"],
        "category": "Analgesic/Anti-inflammatory"
    },
    "pan-d": {
        "dosages": ["40mg"],
        "forms": ["tablet"],
        "instructions": ["Take once daily (morning) before meals for 5 days"],
        "interactions": ["ketoconazole", "atazanavir"],
        "category": "Proton Pump Inhibitor + Prokinetic"
    },
    "hexigel": {
        "dosages": ["gum paint"],
        "forms": ["gel"],
        "instructions": ["Massage twice daily (morning and night) for 1 week"],
        "interactions": ["none known"],
        "category": "Oral Antiseptic"
    }
}

# Initialize random pharmacy stock with the new medications
PHARMACY_STOCK = {med: {"available": random.randint(10, 100), "threshold": random.randint(1, 10)} for med in MEDICATION_DATABASE}

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
        2. Medication Name(s)
        3. Dosage(s)
        4. Instructions
        5. Quantity
        
        Format the response as a JSON object with these fields. If information is not available, use null.
        """
        
        # Extract prescription data
        prescription_raw = query_gemini(extraction_prompt, image_b64)
        
        # Process the extraction to ensure it's valid JSON
        try:
            # Extract the JSON part if the response contains explanatory text
            json_match = re.search(r"```json\n(.*?)\n```", prescription_raw, re.DOTALL)
            if json_match:
                prescription_json = json_match.group(1)
            else:
                prescription_json = prescription_raw
                
            prescription_data = json.loads("prescription_json")
            
            # Create a simplified summary for display
            if isinstance(prescription_data, dict):
                summary = f"**Patient**: {prescription_data.get('Patient Name', 'Unknown')}\n"
                summary += f"**Medications**: {prescription_data.get('Medication Name(s)', 'Unknown')}\n"
                summary += f"**Dosage**: {prescription_data.get('Dosage(s)', 'Unknown')}\n"
                summary += f"**Instructions**: {prescription_data.get('Instructions', 'Unknown')}\n"
                summary += f"**Quantity**: {prescription_data.get('Quantity', 'Unknown')}"
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
    """"Create a medication order from prescription data."""
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
                                               ["prescription", "ocument", "edicine", "osage", "atient", "this"]):
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
        sender_email = "prishitashukla@gmail.com"  # Replace with actual email
        sender_password = "Prishita#8932"  # Replace with actual password

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

# Improved check stock function
def check_stock(medication, quantity):
    """Check if the medication is in stock with improved matching."""
    # Normalize medication name for better matching
    if isinstance(medication, list):
        medication = ' '.join(medication)  # Convert list to string if it's a list
    med_name = medication.lower()
    
    # Try direct match first
    if med_name in PHARMACY_STOCK:
        stock_info = PHARMACY_STOCK[med_name]
        if stock_info["available"] >= int(quantity):
            return "Stock Available"
        elif stock_info["available"] > 0:
            return "Stock Low - Order Needed"
        else:
            return "Out of Stock"
    
    # Try partial match if direct match fails
    for stock_med in PHARMACY_STOCK:
        if stock_med in med_name or med_name in stock_med:
            stock_info = PHARMACY_STOCK[stock_med]
            if stock_info["available"] >= int(quantity):
                return f"Stock Available (matched with {stock_med})"
            elif stock_info["available"] > 0:
                return f"Stock Low - Order Needed (matched with {stock_med})"
            else:
                return f"Out of Stock (matched with {stock_med})"
    
    return "Medication not found in inventory"

# Improved order generation function
def generate_order(medication, quantity):
    """Generate a medication order with improved matching and error handling."""
    if not medication:
        return "No medication specified"
    
    try:
        quantity = int(quantity) if quantity and str(quantity).isdigit() else 1
    except (ValueError, TypeError):
        quantity = 1
    
    # Normalize medication name
    if isinstance(medication, list):
        medication = ' '.join(medication)  # Convert list to string if it's a list
    med_name = medication.lower()
    matched_med = None
    
    # Try direct match first
    if med_name in PHARMACY_STOCK:
        matched_med = med_name
    else:
        # Try partial match if direct match fails
        for stock_med in PHARMACY_STOCK:
            if stock_med in med_name or med_name in stock_med:
                matched_med = stock_med
                break
    
    if matched_med:
        stock_info = PHARMACY_STOCK[matched_med]
        
        # Create appropriate order based on stock
        if stock_info["available"] >= quantity:
            order = {
                "medication": medication,
                "matched_medication": matched_med,
                "quantity": quantity,
                "status": "Order Created - In Stock",
                "order_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.patient_orders.append(order)
            return f"Order successfully placed for {medication}. Stock available."
            
        elif stock_info["available"] > 0:
            order = {
                "medication": medication,
                "matched_medication": matched_med,
                "quantity": quantity,
                "status": "Order Created - Partial Stock",
                "available": stock_info["available"],
                "backordered": quantity - stock_info["available"],
                "order_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.patient_orders.append(order)
            
            # Create supplier order for restocking
            supplier_order = {
                "medication": matched_med,
                "quantity": max(50, quantity * 2),  # Order restock in bulk
                "status": "Supplier Order Created",
                "order_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.patient_orders.append(supplier_order)
            
            return f"Partial stock available ({stock_info['available']} units). Order placed for all {quantity} units with remaining on backorder. Supplier order created."
            
        else:
            order = {
                "medication": medication,
                "matched_medication": matched_med,
                "quantity": quantity,
                "status": "Order Created - Out of Stock",
                "backordered": quantity,
                "order_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.patient_orders.append(order)
            
            # Create supplier order
            supplier_order = {
                "medication": matched_med,
                "quantity": max(50, quantity * 2),  # Order restock in bulk
                "status": "Supplier Order Created - URGENT",
                "order_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.patient_orders.append(supplier_order)
            
            return f"Medication out of stock. Order placed with {quantity} units on backorder. Urgent supplier order created."
    else:
        # Add a special order for medications not in the database
        order = {
            "medication": medication,
            "quantity": quantity,
            "status": "Special Order - Not in Regular Inventory",
            "order_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.patient_orders.append(order)
        
        return f"Medication '{medication}' not found in regular inventory. Special order created."

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
                color: black;
                font-size: 48px;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)
    
    initialize_session_state()

    st.markdown("<div class='title-text'>PrescriptA💊</div>", unsafe_allow_html=True)

    # Sidebar for chat functionality
    with st.sidebar:
        st.header("MedBot⛑")
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
        st.subheader("Medication Database")
        search_query = st.text_input("Search Medications")
        if search_query:
            results = search_medication(search_query)
            if results:
                st.write(f"Found {len(results)} medications:")
                for med in results:
                    with st.expander(f"{med['name']} ({med['category']})"):
                        st.write(f"**Available Dosages**: {med['dosages']}")
                        st.write(f"**Forms**: {med['forms']}")
                        info_prompt = f"Provide a brief professional summary of {med['name']} including its primary uses, major side effects, and important counseling points for pharmacists."
                        med_info = query_gemini(info_prompt, model=GEMINI_PRO_MODEL)
                        st.markdown(med_info)
            else:
                st.info("No medications found. Try a different search term.")
        # Display medication stock
        st.write("### Medication Stock")
        for med, stock in PHARMACY_STOCK.items():
            st.write(f"**{med}**: {stock['available']} units available")
    with tab3:
       st.subheader("Orders")
    
    # Display existing orders
    st.write("### Current Orders")
    if st.session_state.patient_orders:
        # Create a DataFrame to hold order details
        orders_df = pd.DataFrame(st.session_state.patient_orders)
        
        # Add random prices to the DataFrame
        orders_df['price'] = [random.randint(150,500) for _ in range(len(orders_df))]
        
        # Calculate total amount for each order
        orders_df['total_amount'] = orders_df['quantity'] * orders_df['price']
        
        # Display the DataFrame as a table
        st.write(orders_df[['medication', 'quantity', 'price', 'total_amount']])
        
        # Display the total amount for all orders
        total_amount = orders_df['total_amount'].sum()
        st.write(f"**Total Amount for All Orders:** ${total_amount:.2f}")
        
        if st.button("Export Orders to CSV"):
            csv = export_orders_to_csv()
            if csv:
                st.download_button(
                    "Download CSV",
                    csv,
                    "pharmacy_orders.csv",
                    "text/csv",
                    key="download-csv"
                )
    else:
        st.info("No orders have been created yet.")
        
        # Display medication stock
        # st.write("### Medication Stock")
        # for med, stock in PHARMACY_STOCK.items():
        #     st.write(f"**{med}**: {stock['available']} units available")

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
