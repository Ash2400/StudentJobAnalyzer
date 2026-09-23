# analyzer.py
# Responsible for skill extraction and match score calculation

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# ============================================
# CLASS — Analyzer
# ============================================
class Analyzer:

    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.skills_list = data_manager.get_skills_list()
        self.aliases = data_manager.get_aliases()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    # ----------------------------------------
    # Clean raw text
    # ----------------------------------------
    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s\+\#\.]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    # ----------------------------------------
    # Apply aliases to text
    # ----------------------------------------
    def apply_aliases(self, text):
        for alias, real_skill in self.aliases.items():
            pattern = r'\b' + re.escape(alias) + r'\b'
            text = re.sub(pattern, real_skill.lower(), text)
        return text

    # ----------------------------------------
    # Extract skills from text
    # ----------------------------------------
    def extract_skills(self, text):
        text = self.clean_text(text)
        text = self.apply_aliases(text)

        found_skills = set()

        # check single word skills
        tokens = word_tokenize(text)
        for token in tokens:
            if token in self.skills_list:
                found_skills.add(token)

        # check multi word skills
        for skill in self.skills_list:
            if ' ' in skill and skill in text:
                found_skills.add(skill)

        return found_skills

    # ----------------------------------------
    # Process student skills input
    # ----------------------------------------
    def process_student_skills(self, raw_input):
        skills = raw_input.split(',')
        processed = set()
        for skill in skills:
            skill = skill.strip().lower()
            # check alias
            if skill in self.aliases:
                skill = self.aliases[skill].lower()
            # check if valid skill
            if skill in self.skills_list:
                processed.add(skill)
            else:
                print(f"  [!] '{skill}' not recognized — skipped")
        return processed

    # ----------------------------------------
    # Compare student skills vs job skills
    # ----------------------------------------
    def compare_skills(self, student_skills, job_skills):
        matched = student_skills & job_skills
        missing = job_skills - student_skills
        extra = student_skills - job_skills
        return matched, missing, extra

    # ----------------------------------------
    # Calculate match score
    # ----------------------------------------
    def calculate_score(self, matched, job_skills):
        if len(job_skills) == 0:
            return 0
        score = (len(matched) / len(job_skills)) * 100
        return round(score, 2)

    # ----------------------------------------
    # Get recommendation based on score
    # ----------------------------------------
    def get_recommendation(self, score, missing_skills):
        if score >= 80:
            message = "Strong match! You can apply confidently."
        elif score >= 60:
            message = "Good match. Work on missing skills before applying."
        elif score >= 40:
            message = "Moderate match. Focus on missing skills first."
        else:
            message = "Low match. Significant preparation needed."

        recommendations = []
        for skill in missing_skills:
            recommendations.append(f"Learn: {skill}")

        return message, recommendations

    # ----------------------------------------
    # Run full analysis
    # ----------------------------------------
    def analyze(self, student_input, job_description):
        print("\n[...] Processing your input...")

        # process inputs
        student_skills = self.process_student_skills(student_input)
        job_skills = self.extract_skills(job_description)

        if len(job_skills) == 0:
            print("[!] No recognizable skills found in job description.")
            return None

        # compare
        matched, missing, extra = self.compare_skills(
            student_skills, job_skills
        )

        # calculate score
        score = self.calculate_score(matched, job_skills)

        # get recommendation
        message, recommendations = self.get_recommendation(
            score, missing
        )

        # build result dictionary
        result = {
            "student_skills": list(student_skills),
            "job_skills": list(job_skills),
            "matched": list(matched),
            "missing": list(missing),
            "extra": list(extra),
            "match_score": score,
            "matched_count": len(matched),
            "missing_count": len(missing),
            "total_required": len(job_skills),
            "recommendation_message": message,
            "recommendations": recommendations
        }

        return result