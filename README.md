# BiteCheck 🍎💬

BiteCheck is an AI-powered food ingredient assistant that combines OCR-based label scanning with a chatbot for personalized dietary insights.

## 📂 Folder Structure

- `ChatBot/` – Gemini-powered chatbot backend to answer food-related queries, suggest alternatives, and more.
- `OCR/` – OCR module to extract ingredients from scanned food labels using Tesseract and image processing.

Each module is self-contained with its own requirements and deployment configuration.

## 🚀 Deployment (Render or local)

### 🔹 ChatBot
- **Start File:** `chatBot.py`
- **Directory:** `ChatBot/`
- **Dependencies:** `requirements_CB.txt`

### 🔹 OCR Module
- **Start File:** `app.py`
- **Directory:** `OCR/`
- **Dependencies:** `requirements_OCR.txt`

## 🧑‍💻 Team
- ChatBot – Handled by Yashti
- OCR – Handled by Aparna
- Frontend - Handled by Ashlesha
---

This repo is structured for easy independent deployment of both services without conflicts.

