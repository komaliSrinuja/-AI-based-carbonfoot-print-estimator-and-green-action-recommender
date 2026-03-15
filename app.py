from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import hashlib
from datetime import datetime
import math
import subprocess
import time
from collections import defaultdict
from flask import jsonify
import os
from groq import Groq
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
app = Flask(__name__)
app.secret_key = "carbon_secret_key"
def explain_like_girl(ai_text, username, lang):
    greetings = {
        "en": f"Hi {username}! Let me explain your eco suggestions 😊\n\n",
        "te": f"Hi {username}! Nee eco suggestions nenu simple gaa chepthanu 😊\n\n",
        "hi": f"Hi {username}! Main aapko aapke eco suggestions samjhaati hoon 😊\n\n",
        "ta": f"Hi {username}! Ungal eco suggestions-ai vilakkugiren 😊\n\n",
        "mr": f"Hi {username}! Tumche eco suggestions mi soppe karun sangte 😊\n\n"
    }

    return greetings.get(lang, greetings["en"]) + ai_text
# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect("carbon.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS emissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        energy REAL,
        transport REAL,
        diet REAL,
        waste REAL,
        water REAL,
        total REAL,
        date TEXT
    )""")

    conn.commit()
    conn.close()

init_db()

# ---------------- AI SUGGESTION (UNCHANGED ❤️) ----------------
def get_ai_suggestion(total, period, transport, energy, diet, water, waste):
    try:
        prompt = f"""
Period: {period}
Total CO2: {total:.2f}

Transport: {transport:.2f}
Energy: {energy:.2f}
Diet: {diet:.2f}
Water: {water:.2f}
Waste: {waste:.2f}

Give ONLY 3 short eco-friendly suggestions.
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ✅ WORKING MODEL
            messages=[
                {"role": "system", "content": "You are a sustainability expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=120
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("AI ERROR:", e)
        return "⚠️ AI error occurred."
# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("carbon.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, password) VALUES (?,?)",
            (username, password)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")
#-------------------Login----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("carbon.db")
        c = conn.cursor()

        c.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = c.fetchone()
        conn.close()
        if user:
            session["user_id"] = user[0]
            session["username"] = username
            return redirect(url_for("input_page"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

# ---------------- INPUT PAGE (MANUAL ENTRY ONLY) ----------------
@app.route("/input", methods=["GET", "POST"])
def input_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        # ---------- TRANSPORT ----------
        car_km = float(request.form.get("car_km") or 0)
        bus_km = float(request.form.get("bus_km") or 0)
        bike_km = float(request.form.get("bike_km") or 0)
        bicycle_km = float(request.form.get("bicycle_km") or 0)

        car_emission = car_km * 0.21
        bus_emission = bus_km * 0.05
        bike_emission = bike_km * 0.09
        bicycle_emission = 0

        transport_emission = (
            car_emission +
            bus_emission +
            bike_emission +
            bicycle_emission
        )

        # ---------- FOOD ----------
        veg_qty = float(request.form.get("veg_qty") or 0)
        nonveg_qty = float(request.form.get("nonveg_qty") or 0)
        food_emission = veg_qty * 0.002 + nonveg_qty * 0.01

        # ---------- UTILITIES ----------
        electricity = float(request.form.get("electricity") or 0)
        waste = float(request.form.get("waste") or 0)
        water = float(request.form.get("water") or 0)

        electricity_emission = electricity * 0.82
        waste_emission = waste * 0.5
        water_emission = water * 0.0003

        total = (
            transport_emission +
            food_emission +
            electricity_emission +
            waste_emission +
            water_emission
        )

        # ---------- SAVE TO DB ----------
        conn = sqlite3.connect("carbon.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO emissions
            (user_id, energy, transport, diet, waste, water, total, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            electricity_emission,
            transport_emission,
            food_emission,
            waste_emission,
            water_emission,
            total,
            datetime.now().strftime("%Y-%m-%d")
        ))
        conn.commit()
        conn.close()

        # ❌ AI suggestion removed from here (NO DELAY)

        return render_template(
            "result.html",
            total=total,
            energy=electricity_emission,
            transport=transport_emission,
            diet=food_emission,
            waste=waste_emission,
            water=water_emission,
            period=request.form.get("period", "daily")
        )

    return render_template("input.html", username=session["username"])
# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("carbon.db")
    c = conn.cursor()
    c.execute("SELECT SUM(total) FROM emissions WHERE user_id=?", (session["user_id"],))
    total_sum = c.fetchone()[0] or 0

    c.execute("""
        SELECT energy, transport, diet, waste, water
        FROM emissions
        WHERE user_id=?
        ORDER BY date DESC LIMIT 1
    """, (session["user_id"],))
    latest = c.fetchone()
    conn.close()

    energy, transport, diet, waste, water = latest if latest else (0,0,0,0,0)

    return render_template(
        "dashboard.html",
        username=session["username"],
        total=total_sum,
        energy=energy,
        transport=transport,
        diet=diet,
        waste=waste,
        water=water
    )

# ---------------- DYNAMIC AI SUGGESTION ----------------
@app.route("/dashboard/ai_suggestion")
def dashboard_ai_suggestion():
    try:
        lang = request.args.get("lang", "en")
        username = session.get("username", "User")

        # ---------------- FETCH ONLY LATEST ENTRY ----------------
        conn = sqlite3.connect("carbon.db")
        c = conn.cursor()

        c.execute("""
        SELECT energy, transport, diet, waste, water, total
        FROM emissions
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT 1
        """, (session["user_id"],))

        row = c.fetchone()
        conn.close()

        if not row:
            return jsonify({
                "text": "No emission data available yet.",
                "lang": lang
            })

        energy, transport, diet, waste, water, total = row

        # ---------------- FIND HIGHEST CATEGORY ----------------
        categories = {
            "Energy usage": energy,
            "Transport": transport,
            "Food/Diet": diet,
            "Waste": waste,
            "Water usage": water
        }

        highest_category = max(categories, key=categories.get)

        # ---------------- CATEGORY-SPECIFIC PROMPT ----------------
        if highest_category == "Transport":

            prompt = f"""
User transport emissions are the highest ({transport:.2f} kg CO2).

Give 3 practical ways to reduce TRANSPORT emissions.

Focus only on:
- car usage
- fuel consumption
- public transport
- cycling or walking

Return exactly 3 numbered suggestions.
"""

        elif highest_category == "Energy usage":

            prompt = f"""
User electricity/energy emissions are the highest ({energy:.2f} kg CO2).

Give 3 practical ways to reduce ENERGY consumption.

Focus only on:
- electricity usage
- appliances
- LED lights
- solar energy

Return exactly 3 numbered suggestions.
"""

        elif highest_category == "Food/Diet":

            prompt = f"""
User diet emissions are the highest ({diet:.2f} kg CO2).

Give 3 practical ways to reduce FOOD related carbon emissions.

Focus only on:
- reducing meat consumption
- plant-based diet
- sustainable food choices

Return exactly 3 numbered suggestions.
"""

        elif highest_category == "Waste":

            prompt = f"""
User waste emissions are the highest ({waste:.2f} kg CO2).

Give 3 practical ways to reduce WASTE emissions.

Focus only on:
- recycling
- composting
- reducing plastic waste

Return exactly 3 numbered suggestions.
"""

        else:  # Water usage

            prompt = f"""
User water usage emissions are the highest ({water:.2f} kg CO2).

Give 3 practical ways to reduce WATER related emissions.

Focus only on:
- reducing water waste
- efficient water usage
- water-saving habits

Return exactly 3 numbered suggestions.

FORMAT STRICTLY LIKE THIS:

1. First suggestion
2. Second suggestion
3. Third suggestion

Do not return fewer than 3 suggestions.
Do not return more than 3 suggestions.
"""

        # ---------------- AI GENERATION ----------------
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a sustainability expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=150
        )

        ai_text = response.choices[0].message.content.strip()

        # ---------------- FRIENDLY EXPLANATION ----------------
        friendly_text = explain_like_girl(ai_text, username, lang)

        # ---------------- LANGUAGE MAPPING ----------------
        language_names = {
            "hi": "Hindi",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "zh-cn": "Chinese",
            "ja": "Japanese",
            "ru": "Russian",
            "ar": "Arabic",
            "ko": "Korean",
            "it": "Italian",
            "pt": "Portuguese"
        }

        # ---------------- TRANSLATION ----------------
        if lang == "en":
            final_text = friendly_text

        else:
            target_language = language_names.get(lang, "English")

            translation_prompt = f"""
You are a professional translator.

Translate the below text into pure {target_language}.

STRICT RULES:
- Keep EXACT same numbering format (1., 2., 3.)
- Keep all bullet points separately.
- Do NOT merge points.
- Do NOT summarize.
- Do NOT remove any point.
- Do NOT mix English words.
- Output must contain exactly 3 numbered points.

Return ONLY translated text.

Text:
{friendly_text}
"""

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a strict professional translator."},
                    {"role": "user", "content": translation_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            final_text = response.choices[0].message.content.strip()

        return jsonify({
            "text": final_text,
            "lang": lang
        })

    except Exception as e:
        print("AI ERROR:", e)
        return jsonify({
            "text": "AI assistant unavailable",
            "lang": "en"
        })
# ------------------- DASHBOARD ADVANCED FEATURES -------------------
from collections import defaultdict
from datetime import datetime
from flask import jsonify

# Helper DB connection
def get_db_connection():
    conn = sqlite3.connect("carbon.db")
    conn.row_factory = sqlite3.Row
    return conn

# 1️⃣ Trends: daily/monthly/yearly
@app.route("/dashboard/trends_data")
def trends_data():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT date, SUM(total) as total_emission FROM emissions WHERE user_id=? GROUP BY date", (session['user_id'],))
    rows = c.fetchall()
    conn.close()

    daily = []
    monthly = defaultdict(float)
    yearly = defaultdict(float)

    for r in rows:
        date_obj = datetime.strptime(r['date'], "%Y-%m-%d")
        daily.append({"date": r['date'], "total": r['total_emission']})
        monthly_key = date_obj.strftime("%Y-%m")
        yearly_key = date_obj.strftime("%Y")
        monthly[monthly_key] += r['total_emission']
        yearly[yearly_key] += r['total_emission']

    return jsonify({
        "daily": daily,
        "monthly": [{"month": k, "total": v} for k, v in monthly.items()],
        "yearly": [{"year": k, "total": v} for k, v in yearly.items()]
    })

# 2️⃣ Carbon Budget & Goals
@app.route("/dashboard/budget_data")
def budget_data():
    ANNUAL_BUDGET = 2000  # kg CO2
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT SUM(total) as used FROM emissions WHERE user_id=?", (session['user_id'],))
    used = c.fetchone()['used'] or 0
    remaining = max(0, ANNUAL_BUDGET - used)
    conn.close()
    return jsonify({"budget": ANNUAL_BUDGET, "used": used, "remaining": remaining})

# 3️⃣ What-If Simulation
@app.route("/dashboard/whatif", methods=['POST'])
def whatif():
    """
    Expecting JSON:
    { "scenario": "bike_to_bus", "current_emission": 20 }
    """
    data = request.json
    scenario = data.get("scenario")
    old_emission = float(data.get("current_emission", 0))

    # Simple scenario mappings
    scenario_map = {
        "bike_to_bus": 7,
        "car_to_public": 8,
        "electric_to_solar": 0
    }

    new_emission = scenario_map.get(scenario, old_emission)
    saved = old_emission - new_emission
    return jsonify({"scenario": scenario, "before": old_emission, "after": new_emission, "saved": saved})

# 4️⃣ Scope Emissions (1/2/3)
@app.route("/dashboard/scope_data")
def scope_data():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute("""
        SELECT 
            SUM(transport) as transport,
            SUM(energy) as energy,
            SUM(diet + waste + water) as indirect
        FROM emissions
        WHERE user_id=?
    """, (session['user_id'],))

    row = c.fetchone()
    conn.close()

    return jsonify({
        "scope1": row["transport"] or 0,   # Direct
        "scope2": row["energy"] or 0,       # Electricity
        "scope3": row["indirect"] or 0      # Other
    })
# 5️⃣ Carbon Offset 🌱
@app.route("/dashboard/offset_data")
def offset_data():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT SUM(total) as total_emission FROM emissions WHERE user_id=?", (session['user_id'],))
    total = c.fetchone()['total_emission'] or 0
    conn.close()

    trees_needed = round(total / 21)  # 1 tree ≈ 21 kg CO2/year
    cost = trees_needed * 50  # ₹50 per tree
    ngo_list = ["GreenPeace", "TreeIndia", "CarbonNeutral"]  # static suggestions

    return jsonify({
        "total": total,
        "trees": trees_needed,
        "cost": cost,
        "ngo_list": ngo_list
    })
# ---------------- LEADERBOARD (UNCHANGED) ----------------
@app.route("/leaderboard")
def leaderboard():
    period = request.args.get("period", "daily")

    multiplier = {
        "daily": 1,
        "weekly": 7,
        "monthly": 30,
        "yearly": 365
    }.get(period, 1)

    conn = sqlite3.connect("carbon.db")
    c = conn.cursor()

    c.execute("""
        SELECT users.username, SUM(emissions.total) * ?
        FROM emissions
        JOIN users ON users.id = emissions.user_id
        GROUP BY users.id
        ORDER BY SUM(emissions.total) ASC
    """, (multiplier,))

    rows = c.fetchall()
    conn.close()

    leaderboard = [{"username": r[0], "total": r[1]} for r in rows]

    return render_template(
        "leaderboard.html",
        leaderboard=leaderboard,
        period=period
    )

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
