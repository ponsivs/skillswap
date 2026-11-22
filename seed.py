"""
SkillSwap Database Seeder
Seeds realistic EdTech demo accounts, skills, matches, sessions, reviews, and credit transactions.
"""
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.skill import Skill, UserSkill
from app.models.session import LearningSession
from app.models.credit import CreditTransaction
from app.models.review import Review
from app.models.notification import Notification

def seed_database():
    app = create_app()
    with app.app_context():
        print("Creating all tables...")
        db.drop_all()
        db.create_all()

        print("Seeding Skills...")
        skills_data = [
            # Programming & Technology
            {"skill_name": "Python", "category": "Programming & Technology", "description": "Core Python programming, scripting, data structures, and OOP.", "icon": "code"},
            {"skill_name": "Web Development", "category": "Programming & Technology", "description": "Full-stack HTML, CSS, JavaScript, responsive modern web design.", "icon": "globe"},
            {"skill_name": "Flask & APIs", "category": "Programming & Technology", "description": "Building backend RESTful web services and database apps.", "icon": "server"},
            {"skill_name": "JavaScript", "category": "Programming & Technology", "description": "Modern ES6+, async/await, DOM manipulation, frontend tooling.", "icon": "cpu"},
            {"skill_name": "Data Analysis", "category": "Programming & Technology", "description": "Pandas, NumPy, data cleaning, exploratory data visualization.", "icon": "bar-chart-2"},
            
            # Design & Creativity
            {"skill_name": "UI/UX Design", "category": "Design & Creativity", "description": "User research, wireframing, usability principles, and design systems.", "icon": "layout"},
            {"skill_name": "Figma", "category": "Design & Creativity", "description": "Components, autolayout, interactive prototyping, and handoff.", "icon": "figma"},
            {"skill_name": "Graphic Design", "category": "Design & Creativity", "description": "Typography, color theory, visual hierarchy, branding design.", "icon": "palette"},
            {"skill_name": "Video Editing", "category": "Design & Creativity", "description": "Timeline editing, color grading, audio sync in Premiere / DaVinci.", "icon": "video"},
            
            # Communication
            {"skill_name": "Public Speaking", "category": "Communication", "description": "Speech delivery, voice modulation, overcoming stage anxiety.", "icon": "mic"},
            {"skill_name": "Presentation Skills", "category": "Communication", "description": "Designing slide decks and pitching ideas persuasively.", "icon": "airplay"},
            {"skill_name": "Storytelling", "category": "Communication", "description": "Structuring narratives that captivate and persuade audiences.", "icon": "book-open"},
            
            # Academics
            {"skill_name": "Mathematics", "category": "Academics", "description": "Calculus, Linear Algebra, and discrete mathematical logic.", "icon": "hash"},
            {"skill_name": "Statistics", "category": "Academics", "description": "Hypothesis testing, probability distributions, regression.", "icon": "pie-chart"},
            
            # Business & Entrepreneurship
            {"skill_name": "Digital Marketing", "category": "Business & Entrepreneurship", "description": "SEO, content strategy, growth loops, and social campaigns.", "icon": "trending-up"},
            {"skill_name": "Product Management", "category": "Business & Entrepreneurship", "description": "Roadmapping, user personas, MVP scoping, and agile delivery.", "icon": "briefcase"},
            
            # Media & Content Creation
            {"skill_name": "Photography", "category": "Media & Content Creation", "description": "Camera exposure triangle, framing, portrait and event lighting.", "icon": "camera"},
            
            # Languages
            {"skill_name": "Spanish", "category": "Languages", "description": "Conversational Spanish, grammar essentials, and vocabulary.", "icon": "message-circle"},
            
            # Personal Development
            {"skill_name": "Time Management", "category": "Personal Development", "description": "Pomodoro, calendar blocking, prioritization, and deep focus.", "icon": "clock"}
        ]

        skill_map = {}
        for s in skills_data:
            skill_obj = Skill(**s)
            db.session.add(skill_obj)
            skill_map[s['skill_name']] = skill_obj

        db.session.commit()

        print("Seeding Users...")
        # 1. Admin User
        admin = User(
            full_name="Admin Director",
            email="admin@skillswap.edu",
            institution="SkillSwap HQ",
            education_level="Staff / Admin",
            bio="SkillSwap Platform Administrator & Community Safety Director.",
            role="admin",
            credits_balance=100,
            avatar_url="https://api.dicebear.com/7.x/initials/svg?seed=Admin",
            availability="Weekdays 9 AM - 5 PM",
            is_onboarded=True
        )
        admin.set_password("AdminPass123!")
        db.session.add(admin)

        # 2. Alex Rivera (Student A - Python expert, wants UI/UX)
        alex = User(
            full_name="Alex Rivera",
            email="alex@skillswap.edu",
            institution="Stanford University",
            education_level="Undergraduate (Year 2)",
            bio="CS sophomore passionate about backend architecture, APIs, and Python. Looking to master UI/UX to build clean, user-friendly applications.",
            role="student",
            credits_balance=25,
            avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=AlexRivera",
            availability="Weekday Evenings & Weekends",
            learning_interests="UI/UX Design, Figma Prototyping, Product Design",
            is_onboarded=True
        )
        alex.set_password("StudentPass123!")
        db.session.add(alex)

        # 3. Priya Sharma (Student B - UI/UX expert, wants Python)
        priya = User(
            full_name="Priya Sharma",
            email="priya@skillswap.edu",
            institution="UC Berkeley",
            education_level="Undergraduate (Year 3)",
            bio="Design student specializing in user research and Figma systems. Eager to learn Python for scripting and automating data flows.",
            role="student",
            credits_balance=30,
            avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=PriyaSharma",
            availability="Weekends & Tuesday Evenings",
            learning_interests="Python, Backend Development, Data Analysis",
            is_onboarded=True
        )
        priya.set_password("StudentPass123!")
        db.session.add(priya)

        # 4. Marcus Chen (Student C - Data Science, wants Public Speaking)
        marcus = User(
            full_name="Marcus Chen",
            email="marcus@skillswap.edu",
            institution="MIT",
            education_level="Postgraduate",
            bio="Data scientist passionate about turning complex numbers into clear stories. Want to improve public speaking and executive presentation skills.",
            role="student",
            credits_balance=20,
            avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=MarcusChen",
            availability="Weekday Evenings",
            learning_interests="Public Speaking, Storytelling, Presentation Skills",
            is_onboarded=True
        )
        marcus.set_password("StudentPass123!")
        db.session.add(marcus)

        # 5. Elena Rostova (Student D - Debate & Speech Champion, wants Web Dev)
        elena = User(
            full_name="Elena Rostova",
            email="elena@skillswap.edu",
            institution="New York University",
            education_level="Undergraduate (Year 3)",
            bio="Debate team captain and speech mentor. Keen on building modern websites to publish multimedia journalism projects.",
            role="student",
            credits_balance=20,
            avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=ElenaRostova",
            availability="Monday, Wednesday, Weekends",
            learning_interests="Web Development, JavaScript, Python",
            is_onboarded=True
        )
        elena.set_password("StudentPass123!")
        db.session.add(elena)

        db.session.commit()

        print("Seeding UserSkills...")
        # Alex skills (Teaches Python & Flask; Learns UI/UX & Figma)
        user_skills_data = [
            UserSkill(user_id=alex.id, skill_id=skill_map["Python"].id, skill_type="teach", proficiency_level="Advanced", progress_percentage=100, notes="2+ years building web scrapers and backends"),
            UserSkill(user_id=alex.id, skill_id=skill_map["Flask & APIs"].id, skill_type="teach", proficiency_level="Intermediate", progress_percentage=100, notes="Built REST APIs with auth and SQLite/PostgreSQL"),
            UserSkill(user_id=alex.id, skill_id=skill_map["UI/UX Design"].id, skill_type="learn", proficiency_level="Beginner", progress_percentage=35, notes="Currently learning user journeys and wireframing"),
            UserSkill(user_id=alex.id, skill_id=skill_map["Figma"].id, skill_type="learn", proficiency_level="Beginner", progress_percentage=20, notes="Learning auto-layout and components"),
            UserSkill(user_id=alex.id, skill_id=skill_map["Digital Marketing"].id, skill_type="interested", proficiency_level="Beginner", progress_percentage=0, notes="Goal for next semester"),

            # Priya skills (Teaches UI/UX & Figma; Learns Python & Data Analysis)
            UserSkill(user_id=priya.id, skill_id=skill_map["UI/UX Design"].id, skill_type="teach", proficiency_level="Advanced", progress_percentage=100, notes="Designed 4 client apps and design systems"),
            UserSkill(user_id=priya.id, skill_id=skill_map["Figma"].id, skill_type="teach", proficiency_level="Master", progress_percentage=100, notes="Figma Community creator with popular UI kits"),
            UserSkill(user_id=priya.id, skill_id=skill_map["Python"].id, skill_type="learn", proficiency_level="Beginner", progress_percentage=30, notes="Learned loops and dictionaries, wants OOP"),
            UserSkill(user_id=priya.id, skill_id=skill_map["Data Analysis"].id, skill_type="learn", proficiency_level="Beginner", progress_percentage=15, notes="Wants to analyze user testing metrics"),

            # Marcus skills (Teaches Data Analysis & Math; Learns Public Speaking & Speech)
            UserSkill(user_id=marcus.id, skill_id=skill_map["Data Analysis"].id, skill_type="teach", proficiency_level="Advanced", progress_percentage=100, notes="Pandas, NumPy, and statistical modeling"),
            UserSkill(user_id=marcus.id, skill_id=skill_map["Mathematics"].id, skill_type="teach", proficiency_level="Advanced", progress_percentage=100, notes="Linear algebra and calculus tutor"),
            UserSkill(user_id=marcus.id, skill_id=skill_map["Public Speaking"].id, skill_type="learn", proficiency_level="Beginner", progress_percentage=50, notes="Overcoming conference talk anxiety"),
            UserSkill(user_id=marcus.id, skill_id=skill_map["Presentation Skills"].id, skill_type="learn", proficiency_level="Beginner", progress_percentage=40, notes="Structuring executive slide decks"),

            # Elena skills (Teaches Public Speaking & Storytelling; Learns Web Dev & Python)
            UserSkill(user_id=elena.id, skill_id=skill_map["Public Speaking"].id, skill_type="teach", proficiency_level="Master", progress_percentage=100, notes="National collegiate debate finalist"),
            UserSkill(user_id=elena.id, skill_id=skill_map["Storytelling"].id, skill_type="teach", proficiency_level="Advanced", progress_percentage=100, notes="Speechwriter and podcast host"),
            UserSkill(user_id=elena.id, skill_id=skill_map["Web Development"].id, skill_type="learn", proficiency_level="Beginner", progress_percentage=60, notes="Building a personal portfolio"),
            UserSkill(user_id=elena.id, skill_id=skill_map["Python"].id, skill_type="learn", proficiency_level="Beginner", progress_percentage=25, notes="Automating transcription workflows")
        ]

        db.session.add_all(user_skills_data)
        db.session.commit()

        print("Seeding Sessions & Reviews...")
        # 1. Completed session: Elena taught Marcus Public Speaking
        past_date = datetime.utcnow() - timedelta(days=3)
        session_completed = LearningSession(
            teacher_id=elena.id,
            learner_id=marcus.id,
            skill_id=skill_map["Public Speaking"].id,
            session_date=past_date,
            duration_minutes=45,
            status='completed',
            credits_amount=5,
            notes="Marcus: 'I need help structuring a 10-minute research keynote.'",
            meeting_link="https://meet.jit.si/skillswap-room-demo-elena-marcus"
        )
        db.session.add(session_completed)
        db.session.commit()

        # Review from Marcus to Elena
        review_1 = Review(
            session_id=session_completed.id,
            reviewer_id=marcus.id,
            reviewee_id=elena.id,
            rating=5,
            feedback="Elena is an incredible speech mentor! She broke down pacing, vocal inflection, and audience engagement techniques so clearly. Highly recommend!",
            learning_outcome="Mastered opening hooks and slide-less storytelling."
        )
        db.session.add(review_1)

        # Credit transactions for completed session
        tx1 = CreditTransaction(
            user_id=elena.id,
            amount=5,
            balance_after=20,
            transaction_type='earned_teaching',
            session_id=session_completed.id,
            description=f"Earned for teaching Public Speaking to Marcus Chen"
        )
        tx2 = CreditTransaction(
            user_id=marcus.id,
            amount=-5,
            balance_after=20,
            transaction_type='spent_learning',
            session_id=session_completed.id,
            description=f"Spent for learning Public Speaking from Elena Rostova"
        )
        db.session.add_all([tx1, tx2])

        # 2. Upcoming Accepted Session: Priya teaching Alex UI/UX Design!
        future_date = datetime.utcnow() + timedelta(days=2, hours=3)
        session_upcoming = LearningSession(
            teacher_id=priya.id,
            learner_id=alex.id,
            skill_id=skill_map["UI/UX Design"].id,
            session_date=future_date,
            duration_minutes=60,
            status='accepted',
            credits_amount=5,
            notes="Alex: 'Would love feedback on my EdTech platform wireframes and component library!'",
            meeting_link="https://meet.jit.si/skillswap-room-demo-priya-alex"
        )
        db.session.add(session_upcoming)

        # 3. Pending Request: Alex requested session to teach Priya Python
        pending_date = datetime.utcnow() + timedelta(days=4)
        session_pending = LearningSession(
            teacher_id=alex.id,
            learner_id=priya.id,
            skill_id=skill_map["Python"].id,
            session_date=pending_date,
            duration_minutes=45,
            status='pending',
            credits_amount=5,
            notes="Priya: 'Let us do our reciprocal swap! Show me how to connect Python with a SQLite database.'",
            meeting_link="https://meet.jit.si/skillswap-room-demo-alex-priya"
        )
        db.session.add(session_pending)

        # Notifications
        notif_alex = Notification(
            user_id=alex.id,
            title="Reciprocal Match Found!",
            message="Priya Sharma shares reciprocal skills: She can teach you UI/UX Design, and wants to learn Python from you!",
            link="/matching",
            notification_type="system",
            is_read=False
        )
        notif_priya = Notification(
            user_id=priya.id,
            title="Upcoming Session in 2 Days",
            message="Your session with Alex Rivera on UI/UX Design is scheduled for this weekend.",
            link="/sessions",
            notification_type="session_accepted",
            is_read=False
        )
        db.session.add_all([notif_alex, notif_priya])

        db.session.commit()
        print("Database successfully seeded with realistic EdTech demo data!")

if __name__ == '__main__':
    seed_database()
