# 🌱 Ecosense AI – Intelligent Carbon Footprint Estimator

Ecosense AI is an intelligent web-based application designed to estimate a user's carbon footprint and provide personalized eco-friendly recommendations using Artificial Intelligence. The system analyzes lifestyle factors such as energy usage, transport habits, diet, water consumption, and waste generation to calculate CO₂ emissions and suggest actions to reduce environmental impact.

The platform integrates a Large Language Model (LLM) through the Groq API to generate dynamic sustainability suggestions based on the user’s emission profile.



## 🚀 Features

- Carbon footprint calculation based on lifestyle inputs
- AI-powered eco-friendly suggestions
- Interactive dashboard with emission visualization
- Trend analysis for tracking emission changes over time
- Leaderboard ranking system based on lowest emissions
- Scope 1, Scope 2, Scope 3 emission categorization
- Carbon offset estimation through tree planting
- Multilingual AI suggestions
- Personalized eco-action recommendations



## 🧠 AI Integration

Ecosense AI uses the **Groq API** with the **LLaMA 3.1 (8B Instant Model)** to generate intelligent sustainability suggestions.

The AI analyzes the user's carbon footprint data and provides practical steps to reduce emissions, focusing on the category with the highest carbon impact.



## 🛠 Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript
- Chart.js

### Backend
- Python
- Flask Framework

### Database
- SQLite3

### AI & API
- Groq API
- LLaMA 3.1 (8B Instant Model)



## ⚙️ How the System Works

1. User enters lifestyle information such as transport usage, energy consumption, diet habits, waste generation, and water usage.
2. The system calculates CO₂ emissions using predefined carbon emission factors.
3. Emission data is stored in the SQLite database.
4. The system identifies the category with the highest emissions.
5. The Groq AI model generates personalized eco-friendly suggestions.
6. The dashboard visualizes emission trends and sustainability insights.



## 📊 Algorithms Used

- Carbon emission calculation formulas
- Aggregation queries using SQL
- Ranking algorithm for leaderboard
- Scope-based emission categorization
- AI-based dynamic suggestion generation



## 🌍 Dataset

This project does not use a traditional dataset.  
Carbon emissions are calculated using **standard emission factors** for:

- Transport
- Electricity
- Diet
- Waste
- Water consumption



## 🎯 Project Objective

The main objective of Ecosense AI is to promote environmental awareness and encourage individuals to adopt sustainable lifestyle choices by providing data-driven insights and intelligent recommendations.

