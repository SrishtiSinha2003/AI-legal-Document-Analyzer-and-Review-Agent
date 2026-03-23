# ⚖️ AI Legal Document Analyzer & Review Agent

An AI-powered system that analyzes legal documents, identifies risks, summarizes clauses, and provides actionable insights to help users understand complex legal content quickly and effectively.

---

## 🚀 Features

* 📄 Upload and analyze legal documents (PDF)
* 🧠 AI-powered clause detection & summarization
* ⚠️ Risk analysis with highlighted critical clauses
* 🔍 Clause-level insights for better understanding
* 📊 Visual representation (Risk Heatmap)
* 🤖 LLM integration (Groq / Gemini / OpenAI)

---

## 🛠️ Tech Stack

### Frontend

* React.js
* JavaScript
* CSS / UI Components

### Backend

* Python (FastAPI / Flask)
* LangChain / CrewAI
* Groq API (LLM)

### Other Tools

* PDF processing libraries
* REST APIs
* Environment-based configuration

---

## 📂 Project Structure

```
AI-Legal-Document-Analyzer/
│
├── frontend/          # React frontend
├── backend/           # API & AI processing
│   ├── agents/        # AI agents (analysis, summarization)
│   ├── utils/         # Helper functions
│   ├── main.py        # Entry point
│
├── .env.example       # Environment variables template
├── README.md
└── requirements.txt
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```
git clone https://github.com/SrishtiSinha2003/AI-legal-Document-Analyzer-and-Review-Agent.git
cd AI-legal-Document-Analyzer-and-Review-Agent
```

---

### 2️⃣ Backend Setup

```
cd backend
pip install -r requirements.txt
```

Create a `.env` file:

```
GROQ_API_KEY=your_api_key_here
```

Run backend:

```
uvicorn main:app --reload
```

---

### 3️⃣ Frontend Setup

```
cd frontend
npm install
npm start
```

---

## 🔐 Environment Variables

Create a `.env` file in the backend directory:

```
GROQ_API_KEY=your_api_key_here
```

⚠️ Never commit `.env` to GitHub

---

## 📸 Demo

* Upload a legal document
* Get summarized clauses
* View risk insights and heatmap

---

## 💡 Use Cases

* Legal document review automation
* Contract analysis for startups
* Risk detection in agreements
* Educational tool for legal understanding

---

## 🚀 Future Enhancements

* 📌 Multi-language support
* 📌 Clause comparison
* 📌 Real-time collaboration
* 📌 Advanced risk scoring models
* 📌 Deployment (Docker + CI/CD)

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a new branch
3. Make your changes
4. Submit a PR

---

## 📜 License

This project is open-source and available under the MIT License.

---

## 👩‍💻 Author

**Srishti Sinha**

* GitHub: https://github.com/SrishtiSinha2003

---

## ⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub!
