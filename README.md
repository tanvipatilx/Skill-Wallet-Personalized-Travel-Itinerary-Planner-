# VoyageAI - Personalized Travel Itinerary Planner SaaS

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Gemini LLM](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

An intelligent, autonomous travel decision-support and trip architecture SaaS platform. **VoyageAI** algorithmically generates day-by-day vacation itineraries, eliminates travel transit fatigue via geographic clustering, provides vibe-based destination recommendations, enables single-slot dynamic swaps, and exports offline-ready PDF travel guides.

---

## 🌟 Key Features

1. **Intelligent Destination Recommender (Epic 3)**
   - Vibe-based destination matching (Beach & Coastal, Mountain & Alpine, Cultural & Heritage, Urban Skylines).
   - Season and budget-aware recommendations with real-time match scores and highlight tags.
   - One-click transfer from recommendation directly into the itinerary planner.

2. **Day-by-Day Clustered Route Optimization (Epic 4)**
   - **Geographic Clustering Logic**: Automatically groups attractions within the same municipal zone/district per day to eliminate transit fatigue and prevent backtracking.
   - 4 sequential slots per day: Morning Sightseeing, Lunch Recommendation, Afternoon Leisure, and Evening Dining & Entertainment.
   - Itemized estimated costs per activity in both USD ($) and INR (₹).
   - Real-time transit fatigue reduction index computation (94%+ efficiency).

3. **Vibe Customization & Dynamic Activity Swap (Epic 4)**
   - Swap individual slots (e.g., "Find vegetarian lunch spot", "Swap museum for outdoor street market") without wiping or regenerating the rest of the trip.
   - Seamless cost recalculation and in-place slot updating.

4. **Trip Management & Offline PDF Export (Epic 5)**
   - **Simulated Database Persistence**: Built-in SQLite persistence (`trips.db`) with zero external database configuration. Save, view, reload, and manage multiple past itineraries.
   - **1-Click Offline PDF Export**: Powered by `ReportLab`, producing clean, print-ready travel itinerary guides with emergency contacts, safety checklists, and packing essentials.

---

## 🏗️ System Architecture & Tech Stack

| Component | Technology | Description |
|-----------|------------|-------------|
| **Frontend & UI** | Streamlit | Modern SaaS interface with custom CSS styling and responsive layout |
| **Generative AI** | Google Gemini (REST API) | Multi-model fallback (`gemini-3.5-flash-lite`, `gemini-3.5-flash`, `gemini-3.8-flash`) |
| **PDF Engine** | ReportLab Platypus | High-resolution PDF document generation |
| **Local Persistence** | SQLite3 | Embedded zero-dependency relational storage for saved trips |
| **Data Processing** | Pandas / Python | Cost aggregation and budget tracking |

---

## 🚀 Quickstart & Local Installation

### 1. Clone the Repository
```bash
git clone https://github.com/tanvipatilx/Skill-Wallet-Personalized-Travel-Itinerary-Planner-.git
cd Skill-Wallet-Personalized-Travel-Itinerary-Planner-
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure Gemini API Key
You can set an environment variable or enter it directly in the application sidebar:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your-gemini-api-key"

# Linux / macOS
export GEMINI_API_KEY="your-gemini-api-key"
```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```
The app will launch automatically in your browser at `http://localhost:8501`.

---

## 🌐 1-Click Cloud Deployment (Streamlit Community Cloud)

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "feat: complete Personalized Travel Itinerary Planner SaaS"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Community Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click **"New app"**
   - Select your repository, branch (`main`), and set the main file path to `app.py`
   - In Advanced Settings, add `GEMINI_API_KEY` under Secrets (or enter it in the UI)
   - Click **Deploy**

3. Your live application will be instantly accessible at `https://<your-app-name>.streamlit.app`.

---

## 📂 Project Structure

```
├── app.py              # Main Streamlit SaaS application & UI layout
├── ai_service.py       # Gemini API client, route optimizer & fallback generator
├── database.py         # SQLite relational storage for saved trips
├── pdf_generator.py    # ReportLab offline PDF guide generator
├── requirements.txt    # Project dependencies
├── .env.example        # Environment variable sample configuration
├── .gitignore          # Git exclusion rules
└── README.md           # Product documentation & deployment guide
```

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
