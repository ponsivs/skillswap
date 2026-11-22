"""
Skill Matching Engine
Implements transparent rule-based matching based on:
1. Skill compatibility (Reciprocal mutual exchange vs. One-way learning)
2. Proficiency & Experience level fit
3. Availability overlap
"""
from app.models.user import User
from app.models.skill import UserSkill

class MatchingEngine:
    @staticmethod
    def get_matches_for_user(user_id, limit=20):
        current_user = User.query.get(user_id)
        if not current_user:
            return []

        # Current user's skills
        my_teach_skills = {
            us.skill_id: (us.skill.skill_name, us.proficiency_level)
            for us in current_user.teaching_skills if us.skill
        }
        my_learn_skills = {
            us.skill_id: (us.skill.skill_name, us.proficiency_level)
            for us in current_user.learning_skills if us.skill
        }

        if not my_teach_skills and not my_learn_skills:
            # If user hasn't configured skills yet, return top mentors as recommendations
            other_users = User.query.filter(User.id != user_id, User.role != 'admin', User.is_active == True).limit(limit).all()
            matches = []
            for other in other_users:
                teach_names = [us.skill.skill_name for us in other.teaching_skills if us.skill][:3]
                if teach_names:
                    matches.append({
                        'user': other,
                        'compatibility_score': 70,
                        'match_type': 'Discovery Match',
                        'reciprocal': False,
                        'can_teach_you': teach_names,
                        'you_can_teach': [],
                        'reasons': [
                            f"Teaches popular skills: {', '.join(teach_names)}",
                            "Explore mentoring opportunities"
                        ]
                    })
            return matches

        candidate_users = User.query.filter(
            User.id != user_id,
            User.role != 'admin',
            User.is_active == True
        ).all()

        scored_matches = []

        for candidate in candidate_users:
            candidate_teach = {
                us.skill_id: (us.skill.skill_name, us.proficiency_level)
                for us in candidate.teaching_skills if us.skill
            }
            candidate_learn = {
                us.skill_id: (us.skill.skill_name, us.proficiency_level)
                for us in candidate.learning_skills if us.skill
            }

            # Intersection: Skills candidate can teach that current_user wants to learn
            can_teach_you = []
            for skill_id, (skill_name, cand_prof) in candidate_teach.items():
                if skill_id in my_learn_skills:
                    can_teach_you.append((skill_name, cand_prof))

            # Intersection: Skills current_user can teach that candidate wants to learn
            you_can_teach = []
            for skill_id, (skill_name, my_prof) in my_teach_skills.items():
                if skill_id in candidate_learn:
                    you_can_teach.append((skill_name, my_prof))

            # Calculate match score and explanations
            score = 0
            reasons = []
            is_reciprocal = False

            if can_teach_you and you_can_teach:
                # Strong reciprocal exchange!
                is_reciprocal = True
                base_score = 80
                score = min(100, base_score + (len(can_teach_you) + len(you_can_teach)) * 5)
                
                teach_you_names = [s[0] for s in can_teach_you]
                you_teach_names = [s[0] for s in you_can_teach]
                reasons.append(
                    f"Mutual Swap: They teach {', '.join(teach_you_names)} while you teach {', '.join(you_teach_names)}"
                )
            elif can_teach_you:
                # One-way learning match (they can teach you)
                score = min(85, 65 + len(can_teach_you) * 5)
                teach_you_names = [s[0] for s in can_teach_you]
                reasons.append(f"Direct Mentor: They can teach you {', '.join(teach_you_names)}")
            elif you_can_teach:
                # One-way teaching opportunity (you can teach them)
                score = min(75, 55 + len(you_can_teach) * 5)
                you_teach_names = [s[0] for s in you_can_teach]
                reasons.append(f"Teaching Opportunity: They want to learn {', '.join(you_teach_names)}")
            else:
                # No direct match
                continue

            # Availability boost
            if current_user.availability and candidate.availability:
                curr_avail_low = current_user.availability.lower()
                cand_avail_low = candidate.availability.lower()
                if any(w in cand_avail_low for w in ['weekend', 'evening', 'anytime'] if w in curr_avail_low):
                    score = min(100, score + 5)
                    reasons.append("Convenient scheduling: Compatible availability periods")

            # High ratings boost
            if candidate.average_rating >= 4.8 and candidate.completed_sessions_count > 0:
                score = min(100, score + 4)
                reasons.append(f"Highly rated peer mentor ({candidate.average_rating}★)")

            scored_matches.append({
                'user': candidate,
                'compatibility_score': score,
                'match_type': 'Reciprocal Exchange' if is_reciprocal else 'Peer Learning',
                'reciprocal': is_reciprocal,
                'can_teach_you': [s[0] for s in can_teach_you],
                'you_can_teach': [s[0] for s in you_can_teach],
                'reasons': reasons
            })

        # Sort matches by score descending
        scored_matches.sort(key=lambda m: (m['compatibility_score'], m['reciprocal']), reverse=True)
        return scored_matches[:limit]
