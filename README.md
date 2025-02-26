#  PrescriptA💊
                    
 <br>
  <p align="center">
    <img src="Screenshots/Priscripta.logo.png" alt="PriscriptA" width="170" height="150">
  </p>

                         
Priscripta is an AI-driven Project designed to enhance pharmacy operations, reducing errors and improving efficiency .This is a project designed for google girl hackathon 2025 which uses the advanced technologies of Machine learning and Generative Ai to read the handwritten priscriptions given by the doctor.The aim of this project is to optimizes prescription handling, enhances patient safety, and streamlines pharmacy management—making healthcare smarter, faster, and more reliable.



## Key Features

<br>
<p align="center">
    <img src="Screenshots/image.pris.jpg" alt="Key Features" width="250" height="200">
</p>

✅ **Prescription Reader** – A Python-based AI model that accurately reads and analyzes handwritten prescriptions, minimizing human errors.

🤖 **PharmBot** – An intelligent chatbot that assists pharmacists and patients by answering queries about prescribed medicines, dosages, and potential interactions.

📦 **Medication Database** – A structured inventory system that tracks medicine availability in real time, ensuring stock is managed effectively.

💳 **Order & Billing** – An automated system that cross-checks prescriptions, processes orders, and generates bills seamlessly, improving workflow efficiency.

⏳ **MediClock**- it ensures that patients never miss a dose by allowing them to schedule medication reminders via email.

## Demo


### Screenshots
<div align="center">
    <img src="Screenshots/Screenshot (355).png" alt="Home Page" width="380" height="225">
    <img src="Screenshots/Screenshot (356).png" alt="Priscription upload" width="380" height="225">
</div>
<div align="center">
    <img src="Screenshots/Screenshot (357).png" alt="Priscription analysis" width="380" height="225">
    <img src="Screenshots/Screenshot (358).png" alt="Medication stock" width="380" height="225">
</div>
<div align="center">
    <img src="Screenshots/Screenshot (358).png" alt="MedBot" width="380" height="225">
    <img src="Screenshots/Screenshot (359).png" alt="Mediclock" width="380" height="225">
</div>
<div align="center">
    <img src="Screenshots/Screenshot (360).png" alt="remainder" width="380" height="225">
    <img src="Screenshots/Screenshot (361).png" alt="medbot" width="380" height="225">
</div>
<div align="center">
    <img src="Screenshots/Screenshot (362).png" alt="mediclock" width="180" height="225">
   <img src="Screenshots/Screenshot orders.png" alt="order" width="180" height="225">
    <img src="Screenshots/Screenshot (363).png" alt="overall" width="380" height="225">
</div>

## Technologies Used
- **Frontend:** React JS, HTML,CSS
- **Backend:** Python (Streamlit)
- **ML Techniquies:** NLP,PAI-driven OCR (Optical Character Recognition)
- **ML Libraries:** Streamlit,Requests,Pillow(PIL),pdf2image,Base64,smtplib,io,re
- **APIs:** Gemini API
- **Database:** Firebase Firestore
- **Tools:** Lightning ai studio, Postman, VS Code

  ## Design Idea & Approach


### Architecture
<p align="center">
    <img src="Screenshots/flowchart.PrescriptA.jpg" alt="Architecture"  width="600" height="450">
</p>

- The frontend is built with **Streamlit** for a simple UI, while the backend leverages **Python, OCR (pdf2image, PIL), and Gemini AI (Google API)** for prescription reading and chatbot responses.  
- **Priscripta** extracts **handwritten and electronic prescription details** using **OCR & AI**, ensuring **accurate medication identification**. The system **validates prescriptions** against a **medication database**, preventing **errors and stock issues**.  
- This **AI-driven chatbot**, powered by **Gemini AI**, provides **instant responses** to **pharmacist and patient queries** regarding **dosage, side effects, drug interactions, and medicine instructions**.  
- Initially designed for **limited concurrent users**, the system will scale using **cloud-based AI models, SQL/NoSQL databases, and server load balancing**. Future enhancements include **local AI models for cost efficiency**.

### Data Set Desciption

After searching online, I discovered a Kaggle dataset that fits our 'Symptom Analysis' recommendation system. The dataset comprises 133 columns: 132 for patient symptoms and 1 for prognosis. It covers 42 different diseases and illnesses. The 'training.csv' file contains a total of 4,920 rows.

### Machine Learning Lifecycle

<p align="center">
    <img src="screenshots/ml_lifecycle.jpeg" alt="ML Lifecycle" width="600" height="379">
</p>

The machine learning lifecycle begins with exploratory data analysis (EDA). The dataset, consisting of 132 columns of categorical data (0 or 1), covered 42 diseases, each with 120 balanced samples. We ensured data consistency, corrected naming inconsistencies, and focused on 12 diseases for prototyping.

Utilizing techniques like Tree-based Algorithm for Feature Importance, Recursive Feature Elimination (RFE), and L1 Regularization (Lasso), I reduced features to 60 for simplicity. After excluding irrelevant rows and introducing a new class for uncorrelated symptoms, the dataset contained 1,560 rows and 61 columns.

I divided the dataset into X (60 columns) and Y (1 column) and applied an 80:20 train-test split, stratified to maintain equal class representation. Using Logistic Regression from sklearn, my model achieved a 99% validation accuracy, effectively addressing the multi-class classification problem.




## Getting Started


Click [here](https://heal-smart.vercel.app/) to visit the web app directly.

### Setting up the ML Model API locally

1. Make sure you have the following installed:
   - Python (version 3.x)
   - pip (Python package installer)
   - Virtual environment (optional but recommended)
2. Navigate to the `server` directory in the project.
3. Create a Python virtual environment using the command (optional):
   ```
   virtualenv venv
   ```
4. Activate the virtual environment (only if you have followed step 3):
   - On Unix/Linux:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```
5. Install Python dependencies by running:
   ```
   pip install -r requirements.txt
   ```
6. Run the development server using:
   ```
   flask run
   ```
7. Access the API at `http://localhost:5000/predict`.
   - Method: POST
   - Content-Type: Application/JSON
   - Sample Body:
     ```json
     { "symptoms": ["hip_joint_pain", "joint_pain", "knee_pain", "painful_walking"]}
     ```
   - Sample Response:
     ```json
     {"prediction": "Osteoarthritis"}
     ```


## Use Cases

-  **Automated Prescription Processing** – AI reads and extracts details from **handwritten and electronic prescriptions**.  
-  **Pharmacy Inventory Management** – Tracks **medicine availability** and prevents **stock shortages**.  
-  **AI Chatbot Assistance** – Answers **medicine-related queries** for **pharmacists and patients**.  
-  **Medication Ordering & Billing** – Generates **orders and bills** directly from **prescriptions**.  
-  **Patient Medicine Availability Check** – Allows users to **check stock** before visiting a **pharmacy**.  
-  **Online Medicine Ordering** – Enables **patients** to place **orders** through the **patient interface**.  
-  **Drug Interaction & Dosage Analysis** – Identifies **potential risks** and provides **accurate dosage information**.  
-  **Automated Medication Reminders** – Sends **alerts via MediClock** to improve **patient adherence**.  
-  **Insurance & Prescription Validation** – Helps process **insurance claims** by **validating prescriptions**.  
-  **Hospital & Clinic Integration** – Streamlines **medication management** within **healthcare facilities**.  






### *Social Impact of Priscripta*  

-  *Reduces Prescription Errors* – Minimizes misinterpretation of handwritten prescriptions, preventing medication-related mistakes.  
-  *Improves Patient Safety* – Ensures accurate dosage instructions and identifies potential drug interactions.  
-  *Enhances Medication Adherence* – Sends automated reminders, helping patients take medicines on time.  
-  *Increases Pharmacy Efficiency* – Automates repetitive tasks, allowing pharmacists to focus on patient care.  
-  *Improves Healthcare Accessibility* – Enables patients to check medicine availability and order remotely.  
-  *Reduces Healthcare Costs* – Prevents medication waste and optimizes stock management, lowering expenses.  
-  *Supports Underserved Areas* – Provides digital pharmacy solutions in areas with limited medical access.  
-  *Strengthens Data-Driven Healthcare* – Uses AI to improve prescription tracking and healthcare insights.  
-  *Empowers Patients with Information* – AI chatbot educates users about their medications, improving health awareness.  
-  *Contributes to a Smarter Healthcare System* – Integrates AI and automation to make pharmacies safer and more efficient.




## Scopes of Improvement


- **Enhance Symptom Analysis Accuracy:** Improve ML model accuracy and dataset comprehensiveness.
   
- **User Login:** Create an authentication system for users so that they can store their data always.
- **Integration of Telemedicine:** Facilitate virtual consultations for user convenience.
- **User Experience Refinement:** Gather feedback for intuitive interface enhancements.
- **Personalization and Customization:** Tailor content to individual preferences for better engagement.
- **Comprehensive Data Security:** Strengthen privacy measures for user trust and compliance.
- **Implement Proper Booking System:** Develop a robust booking system leveraging real healthcare database for streamlined appointment scheduling.




## References


- Link to Dataset: https://www.kaggle.com/datasets/kaushil268/disease-prediction-using-machine-learning
