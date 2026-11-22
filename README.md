# SkillSwap 🎓
> **Share Skills. Exchange Knowledge. Grow Together.**

![SkillSwap Banner](https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=80)

**SkillSwap** is a modern, responsive, peer-to-peer student learning and skill exchange platform. It transforms students' individual knowledge into shared learning opportunities through **intelligent reciprocal matching**, a **credit-based knowledge token economy**, and **dynamic, personalised skill maps**.

---

## 🌟 Key Features

1. **Intelligent Reciprocal Matching Engine**:
   - Transparent rule-based algorithm that pairs students with complementary skills (e.g. Student A teaches Python and wants UI/UX; Student B teaches UI/UX and wants Python $\rightarrow$ 98% Compatibility Mutual Swap).
   - Also supports direct one-way peer mentorship.
2. **Personalised Interactive Skill Map**:
   - Dynamic, particle-physics canvas node graph visualising student skill networks.
   - Categorised nodes: *Center Hub*, *Category Domains*, *Skills I Can Teach* (Green), *Skills I Am Learning* (Blue with progress slider), *Completed / Mastered* (Teal), and *Future Goals* (Amber).
   - Real-time AJAX progress tracking updates.
3. **Credit-Based Knowledge Token Economy**:
   - Every new student receives **15 welcome credits** upon registration.
   - Earn **5 credits** for every completed teaching session.
   - Spend **5 credits** to book a learning session.
   - Full ACID transaction audit ledger preventing negative balances or duplicate completions.
4. **Structured Learning Sessions**:
   - In-app request flow with date, time, duration, and agenda notes.
   - Accept, Decline, Cancel, and Complete session workflows with private Jitsi video room links.
   - Post-session 5-star ratings, testimonials, and verified learning outcomes.
5. **Student Privacy & Child Safety**:
   - Personal phone numbers and private email addresses are never publicly exposed.
   - Controlled in-app scheduling and session coordination.
   - Student reporting & moderation mechanism.
6. **Administrator Portal**:
   - Platform metrics (Total students, sessions, credit volume).
   - Account status toggle (activate/suspend).
   - Official skill directory curation.
   - Moderation report resolution.

---

## 🎨 Design System

- **Primary**: Deep Indigo (`#4338CA`)
- **Secondary**: Electric Violet (`#7C3AED`)
- **Accent**: Soft Cyan (`#22D3EE`)
- **Background**: `#F8FAFC`
- **Headings Font**: Plus Jakarta Sans
- **Body Font**: Inter
- **Icons**: Lucide Icons

---

## 💻 Tech Stack

- **Backend**: Python 3.10+ / Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Werkzeug
- **Database**: PostgreSQL (Production) / SQLite (Zero-config local development)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5.3, Canvas Particle Graph, Lucide Icons
- **Deployment**: Render / Gunicorn

---

## 🚀 Quickstart & Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/skillswap.git
cd skillswap
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*Note: If `DATABASE_URL` is not provided, SkillSwap defaults to `sqlite:///instance/skillswap.db` for instant zero-configuration local runs.*

### 5. Seed the database with demo accounts & skills
```bash
python seed.py
```

### 6. Run the application
```bash
python run.py
```
Open your browser and navigate to: **`http://localhost:5000`**

---

## 🔑 Demo Accounts (Pre-configured)

Use these credentials to test the reciprocal matching and session exchange:

| Role / Persona | Email | Password | What to Observe |
| :--- | :--- | :--- | :--- |
| **Student A (Alex Rivera)** | `alex@skillswap.edu` | `StudentPass123!` | Teaches Python, wants UI/UX. Shows reciprocal match with Priya. |
| **Student B (Priya Sharma)** | `priya@skillswap.edu` | `StudentPass123!` | Teaches UI/UX, wants Python. Reciprocal swap partner for Alex. |
| **Student C (Marcus Chen)** | `marcus@skillswap.edu` | `StudentPass123!` | Teaches Data Analysis & Math, wants Public Speaking. |
| **Student D (Elena Rostova)**| `elena@skillswap.edu` | `StudentPass123!` | Debate champion, teaches Public Speaking & Storytelling. |
| **Administrator Director** | `admin@skillswap.edu` | `AdminPass123!` | Full Admin Portal (`/admin`) access, metrics, moderation. |

---

## 🧪 Running Automated Tests

Run the test suite with Python:
```bash
python -m unittest tests/test_skillswap.py
```

---

## 🌐 Deploying to Render

1. Push your repository to GitHub.
2. Create a new **Web Service** on [Render](https://render.com).
3. Connect your GitHub repository.
4. Set the following build and start commands:
   - **Build Command**: `pip install -r requirements.txt && python seed.py`
   - **Start Command**: `gunicorn run:app`
5. Under **Environment Variables**, add:
   - `SECRET_KEY`: `<your-random-secret-key>`
   - `DATABASE_URL`: (Attach Render PostgreSQL database internal connection string)
6. Click **Deploy Web Service**!

---

## 📄 License
MIT License &copy; 2026 SkillSwap Inc. Share Skills. Exchange Knowledge. Grow Together.
