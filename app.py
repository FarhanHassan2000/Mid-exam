from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os
from functools import wraps

# --- ENV SUPPORT ---
# pip install python-dotenv
from dotenv import load_dotenv
load_dotenv()  # .env file ko load karega

# --- GEMINI API INTEGRATION ---
# pip install google-genai
from google import genai
from google.genai.errors import APIError

# API KEY automatically .env se load hogi
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = None
try:
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print("✅ Gemini Client successfully created.")
    else:
        print("❌ ERROR: GEMINI_API_KEY missing. Roadmap generation disabled.")
except Exception as e:
    print(f"❌ FATAL ERROR during Gemini Client setup: {e}")


# ---------------- CONFIG ----------------

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-change-karo'  # isko bhi env se lena better hai
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ---------------- MODELS ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    learning_paths = db.relationship("LearningPath", backref="user", lazy=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class LearningPath(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    level = db.Column(db.String(50), nullable=False)
    dream_role = db.Column(db.String(150), nullable=False)
    weekly_hours = db.Column(db.String(50), nullable=False)
    roadmap_json = db.Column(db.Text, nullable=False)


# ---------------- HELPERS ----------------

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper


def generate_fallback_roadmap(level, dream_role, weekly_hours):
    """
    Agar Gemini fail ho jaye (quota / key issue), to yeh simple static roadmap return karega
    jisme basic YouTube / Google search links honge.
    """
    level = level or "Beginner"
    dream_role = dream_role or "Developer"

    # Simple search query helpers
    base_youtube = "https://www.youtube.com/results?search_query="
    base_google = "https://www.google.com/search?q="

    role_query = dream_role.replace(" ", "+")
    level_query = level.replace(" ", "+")

    return [
        {
            "title": "Week 1: Fundamentals & Setup",
            "description": f"Start your journey towards becoming a {dream_role}. Focus on core basics and setup.",
            "content": [
                {
                    "title": "Install VS Code or any suitable IDE",
                    "type": "Article",
                    "url": base_google + "install+vs+code"
                },
                {
                    "title": f"{level} programming concepts (variables, loops, conditions)",
                    "type": "Video",
                    "url": base_youtube + f"{level_query}+programming+basics"
                },
            ],
        },
        {
            "title": "Week 2: Core Language Practice",
            "description": "Strengthen syntax and basic problem solving.",
            "content": [
                {
                    "title": "Practice easy coding problems",
                    "type": "Article",
                    "url": base_google + "easy+coding+problems+for+beginners"
                },
                {
                    "title": "Functions & debugging basics",
                    "type": "Video",
                    "url": base_youtube + "functions+and+debugging+for+beginners"
                },
            ],
        },
        {
            "title": "Week 3: Mini Projects",
            "description": "Apply basics to small real-world style tasks.",
            "content": [
                {
                    "title": "Build a simple calculator or to-do app",
                    "type": "Article",
                    "url": base_google + "build+simple+todo+app+tutorial"
                },
                {
                    "title": "Git & GitHub basics",
                    "type": "Video",
                    "url": base_youtube + "git+and+github+for+beginners"
                },
            ],
        },
        {
            "title": "Week 4: Role-Specific Skills",
            "description": f"Learn tools/topics directly related to {dream_role}.",
            "content": [
                {
                    "title": f"Search required skills for {dream_role}",
                    "type": "Article",
                    "url": base_google + f"roadmap+for+{role_query}"
                },
                {
                    "title": f"Intro video: {dream_role}",
                    "type": "Video",
                    "url": base_youtube + f"how+to+become+{role_query}"
                },
            ],
        },
        {
            "title": "Week 5: Portfolio Work",
            "description": "Make your work visible and strengthen understanding.",
            "content": [
                {
                    "title": "Push your projects to GitHub",
                    "type": "Article",
                    "url": base_google + "how+to+push+project+to+github"
                },
                {
                    "title": "Write README for each project",
                    "type": "Article",
                    "url": base_google + "how+to+write+a+good+readme"
                },
            ],
        },
        {
            "title": "Week 6: Revision & Next Steps",
            "description": "Revise, polish, and plan your next steps.",
            "content": [
                {
                    "title": "Revise all topics covered in earlier weeks",
                    "type": "Article",
                    "url": base_google + f"{role_query}+beginner+revision+checklist"
                },
                {
                    "title": "Plan next 30 days of learning",
                    "type": "Video",
                    "url": base_youtube + "how+to+plan+your+learning+roadmap"
                },
            ],
        },
    ]


def generate_roadmap_with_gemini(level, dream_role, weekly_hours):
    """
    Pehle Gemini se roadmap banane ki koshish karta hai.
    Agar API error / quota / koi masla ho to fallback roadmap generate karta hai.
    """
    global client

    level = (level or "Beginner").strip()
    dream_role = (dream_role or "Developer").strip()
    weekly_hours = (weekly_hours or "5-10 hrs").strip()

    # Agar client hi nahi bana (no key ya config issue)
    if client is None:
        flash("Gemini API is not configured. Using fallback roadmap.", "warning")
        return generate_fallback_roadmap(level, dream_role, weekly_hours)

    # Strong system prompt: JSON + links + types
    system_instruction = (
        "You are an expert career and learning path generator. "
        "Create a structured, detailed 6-week learning roadmap based on the user's input. "
        "The final output MUST be a JSON array with exactly 6 objects (one per week). "
        "Each week object MUST have: "
        "  - 'title' (string): short week name, "
        "  - 'description' (string): what the user will achieve this week, "
        "  - 'content' (array): list of learning items. "
        "Each item in 'content' MUST be an object with: "
        "  - 'title' (string): what to learn/do, "
        "  - 'type' (string): one of 'Video', 'Article', 'Documentation', 'Course', or 'Project', "
        "  - 'url' (string): a real, publicly accessible learning resource URL relevant to that item "
        "       (for example a YouTube tutorial, official documentation, a free article, or free course). "
        "Prefer free resources that don't require login or payment if possible. "
        "At least one 'Video' and one 'Article' or 'Documentation' item should be present in every week. "
        "The roadmap should be realistic for the given weekly study hours and skill level. "
        "IMPORTANT: Return ONLY the JSON array. No extra text, no explanations, no markdown, no comments."
    )

    user_prompt = f"""
    The user wants to become: {dream_role}.
    Current level: {level}.
    Weekly available study time: {weekly_hours}.

    Generate a detailed 6-week learning roadmap focused on the most important skills and topics
    for this role. Start with fundamentals appropriate to the level and progress towards more
    practical, portfolio-worthy work.

    For each content item, include an appropriate 'type' and a real URL to a useful learning resource
    (YouTube video, free article, official docs, or free course) that matches the topic.

    Output MUST be a valid JSON array of 6 week objects exactly, following the schema described
    in the system instructions. Do NOT include anything outside JSON.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json"
            )
        )

        cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
        roadmap_json = json.loads(cleaned_text)
        return roadmap_json

    except APIError as e:
        # Special handling for quota / 429
        if "RESOURCE_EXHAUSTED" in str(e) or "quota" in str(e).lower():
            print("💥 Gemini quota exhausted:", e)
            flash(
                "Gemini ka free quota khatam ho gaya hai. Fallback roadmap use ho raha hai.",
                "warning",
            )
        else:
            print("Gemini API Error:", e)
            flash("Gemini API error aayi hai. Fallback roadmap use ho raha hai.", "error")
        return generate_fallback_roadmap(level, dream_role, weekly_hours)

    except Exception as e:
        print("Unexpected Gemini Error:", e)
        flash("Unexpected error while generating roadmap. Fallback roadmap use ho raha hai.", "error")
        return generate_fallback_roadmap(level, dream_role, weekly_hours)


# ---------------- ROUTES ----------------

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("pass")

        if not full_name or not email or not password:
            flash("Please fill all fields.", "error")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "error")
            return redirect(url_for("login"))

        user = User(full_name=full_name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("pass")

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        session["user_name"] = user.full_name.split()[0] if user.full_name else "User"

        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    user_name = session.get("user_name", "User")
    roadmap = None
    level = dream_role = weekly_hours = ""

    if request.method == "POST":
        level = request.form.get("level")
        dream_role = request.form.get("dream_role")
        weekly_hours = request.form.get("weekly_hours")

        # 👇 Pehle check karo: same inputs ka roadmap pehle se DB me hai?
        existing_lp = LearningPath.query.filter_by(
            user_id=session["user_id"],
            level=level,
            dream_role=dream_role,
            weekly_hours=weekly_hours
        ).order_by(LearningPath.created_at.desc()).first()

        if existing_lp:
            roadmap = json.loads(existing_lp.roadmap_json)
            flash("Loaded saved roadmap (no new AI call).", "info")
        else:
            roadmap = generate_roadmap_with_gemini(level, dream_role, weekly_hours)
            if roadmap:
                lp = LearningPath(
                    user_id=session["user_id"],
                    level=level,
                    dream_role=dream_role,
                    weekly_hours=weekly_hours,
                    roadmap_json=json.dumps(roadmap)
                )
                db.session.add(lp)
                db.session.commit()
                flash("Roadmap generated successfully!", "success")

    history = LearningPath.query.filter_by(user_id=session["user_id"]).order_by(
        LearningPath.created_at.desc()
    ).limit(5).all()

    if not roadmap and history:
        latest = history[0]
        roadmap = json.loads(latest.roadmap_json)
        level = latest.level
        dream_role = latest.dream_role
        weekly_hours = latest.weekly_hours

    return render_template(
        "dashboard.html",
        user_name=user_name,
        roadmap=roadmap,
        history=history,
        level=level,
        dream_role=dream_role,
        weekly_hours=weekly_hours
    )


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out!", "success")
    return redirect(url_for("login"))


# ---------------- MAIN ----------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # In deployed/containerized environments the Flask reloader attempts to
    # register signal handlers which can fail (ValueError) when not running
    # in the main thread. Disable debug/reloader for production runs.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
