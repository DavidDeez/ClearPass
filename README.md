# ClearPass AI

ClearPass is a portable KYC and AI trust-scoring API. It verifies identity using live biometric selfies, profiles financial behavior, runs an ensemble of 3 AI models (XGBoost, Isolation Forest, and Graph-based fraud detection), and returns a unified Trust Score (0–100) along with an actionable verdict.

## 🚀 Quick Setup & Installation

Follow these steps to run ClearPass locally on your machine.

### Prerequisites
- Python 3.8+ installed on your system.
- Git installed.

### 1. Clone the Repository
```bash
git clone https://github.com/DavidDeez/ClearPass.git
cd ClearPass
```

### 2. Set Up a Virtual Environment
It is highly recommended to use a virtual environment to install the dependencies.

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
With the virtual environment activated, install the required packages:
```bash
pip install -r requirements.txt
```

### 4. Run the Server
Start the FastAPI application:
```bash
python main.py
```
> **⏳ Important Note on Startup Time:** The server eagerly loads several heavy machine learning models (like FaceNet for biometrics and XGBoost) into memory upon startup. This means **it may take 15–45 seconds for the server to fully boot up.** Please wait until the console displays that the application is running before opening the browser.

Once you see the startup complete message in your terminal, the server is ready!

## 🧪 Testing the Application

1. **Access the UI**: Open your web browser and navigate to [http://localhost:8000](http://localhost:8000).
2. **KYC Flow**: 
   - Fill in the basic identity details in Step 1.
   - Use your webcam to take a live selfie (the application enforces a live camera feed).
   - Insert transaction history (or just use the built-in "Use Sample Data" tab).
   - Click **Run AI Verification** to see the final Trust Score, AI explanation, and fraud detection verdict.
