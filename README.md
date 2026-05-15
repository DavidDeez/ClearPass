# 🛡️ ClearPass AI
### Portable Trust-Scoring & Identity Infrastructure for African Fintech

ClearPass AI is a high-performance identity verification and risk-scoring platform designed to eliminate onboarding friction while maximizing fraud detection. It transforms raw financial and biometric data into a **Multi-Model Trust Score**, acting as a causal gate for high-stakes operations like the **GTCO Squad Payout API**.

---

## 🧠 The AI Architecture

ClearPass uses a proprietary **Triple-Layer Risk Brain** to evaluate every verification request:

### 1. 👁️ Biometric Integrity (Vision Layer)
*   **Active Liveness:** Uses **MediaPipe FaceMesh** to track 468 3D landmarks for real-time **Blink Detection** (Eye Aspect Ratio).
*   **Biometric Matching:** Employs **FaceNet** embeddings to calculate the Euclidean distance between live selfies and government-issued IDs.
*   **Hybrid AI:** Vision tasks are offloaded to the client-side for sub-second performance, reducing server-side CPU bottlenecks.

### 2. 📈 Behavioral Intelligence (Risk Layer)
*   **XGBoost Profiler:** Analyzes financial "rhythms" (income consistency, debit/credit ratios, transaction velocity) to predict borrower reliability.
*   **Isolation Forest Anomaly Detection:** Specifically targets "Ghost Borrowers"—identities that appear legitimate but exhibit outlier spending behaviors indicative of fraud.
*   **Explainable AI (XAI):** Uses **SHAP (SHapley Additive exPlanations)** to provide human-readable reasons for every score, ensuring transparency and regulatory compliance.

### 3. 🔗 Identity Graph (Network Layer)
*   **Network Analysis:** Uses **NetworkX** to build a graph of connected identities (BVNs, Devices, Addresses).
*   **Fraud Ring Detection:** Identifies clusters of identities sharing the same hardware or location, automatically blocking coordinated fraud attempts.

---

## 🛠️ Developer Suite

ClearPass is built as a **Platform**, not just an application.

*   **Identity Search API:** `/api/identity/check/{bvn}` enables the "Verify Once, Use Everywhere" reusable identity model.
*   **Causal Gate Enforcement:** Seamlessly integrates with the **GTCO Squad API** to block payouts for high-risk users.
*   **Monitoring Dashboard:** Real-time logging and fraud analytics at `/dashboard`.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- SQLite (for tokenization persistence)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/DavidDeez/ClearPass.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   python main.py
   ```
4. Access the Demo at `http://localhost:8000` or the Admin Console at `http://localhost:8000/dashboard`.

---

## 🏆 Hackathon 2026 Submission
Built for the **GTCO Squad Hackathon**, ClearPass AI solves the dual problem of onboarding friction and financial fraud using state-of-the-art machine learning and network theory.
