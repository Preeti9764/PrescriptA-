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
    <img src="Screenshots/flowchart.PrescriptA.jpg" alt="Architecture"  width="600" height="329">
</p>

HealSmart offers a comprehensive healthcare solution by leveraging modern technologies and user-friendly design principles. The architecture is built around three main divisions:

1. **Symptom Analysis:** HealSmart diagnoses diseases based on symptoms using a Flask API connected to a trained ML model. The predicted disease is received as a response from the API, and then it guides users to the appropriate specialist doctor for further consultation. Additionally, there's an AI-driven chatbot, developed using the Gemini API, which offers preliminary suggestions based on the symptoms and disease.
2. **Mind-Bot:** To address mental health concerns, I developed a chat application powered by the Gemini API from Google AI Studio. The Gemini 1.5 pro model is feeded with system instructions and trained with some conversations to provide empathetic consultations. This chatbot provides support for mental health issues like loneliness and anxiety and also offers suggestions on how to handle them effectively.

3. **Consult Doctor:** HealSmart enables users to find and book appointments with doctors across various specialties. Data is fetched from Firebase Firestore, where dummy healthcare provider datas are maintained. Users can explore doctors' profiles, view their basic details and ratings, and check for their availability. This feature streamlines the process of finding and scheduling appointments, enhancing the overall healthcare experience for users.


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

- **Symptom Analysis and Diagnosis:** Input symptoms to get potential diagnoses and find relevant specialist doctors.


- **Mental Health Support:** Engage in empathetic conversations for mental health guidance and professional help suggestions.


- **Doctor Consultation:** Find, view profiles, and proceed for booking healthcare providers.


- **Preventive Healthcare:** Receive timely recommendations for screenings, vaccinations, and lifestyle changes.


- **Disease Management:** Track symptoms and receive personalized recommendations for effective management.


- **Remote Healthcare Access:** Access healthcare guidance and support remotely without physical visits.


- **Post-Appointment Follow-up:** Track symptoms, medication adherence, and access support after appointments.


- **Healthcare Provider Collaboration:** Collaborate with healthcare providers for personalized recommendations and progress monitoring.




## Social Impact


- **Enhanced Accessibility:** Easier access to healthcare, reducing disparities.

- **Mental Health Support:** Destigmatizes issues, promotes help-seeking.
- **Improved Quality:** Personalized care, streamlined processes.
- **Preventive Care:** Promotes proactive health management.
- **Crisis Response:** Immediate support during emergencies.




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
