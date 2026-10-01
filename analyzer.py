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
        self.skill_categories = data_manager.get_skills_with_categories()
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

         # prioritize technical skills over soft skills
        technical = {
            s for s in found_skills
            if self.skill_categories.get(s, '') != 'Soft Skill'
        }
        soft = {
            s for s in found_skills
            if self.skill_categories.get(s, '') == 'Soft Skill'
        }

        # cap at 15 total, technical skills first
        combined = list(technical) + list(soft)
        return set(combined[:15])

    # ----------------------------------------
    # Process student skills input
    # ----------------------------------------
    def process_student_skills(self, raw_input):
        skills = raw_input.split(',')
        processed = set()
        for skill in skills:
            skill = skill.strip().lower()
            if skill in self.aliases:
                skill = self.aliases[skill].lower()
            if skill in self.skills_list:
                processed.add(skill)
            else:
                print(f"  [!] '{skill}' not recognized — skipped")

        implied = {
            'matplotlib': ['data visualization'],
            'seaborn': ['data visualization'],
            'numpy': ['statistical analysis'],
            'pandas': ['data analysis'],
            'scikit-learn': ['machine learning'],
            'tensorflow': ['machine learning', 'deep learning'],
            'pytorch': ['machine learning', 'deep learning'],
            'keras': ['deep learning', 'machine learning'],
            'tableau': ['data visualization'],
            'power bi': ['data visualization'],
            'postgresql': ['sql'],
            'mysql': ['sql'],
            'docker': ['devops'],
            'kubernetes': ['devops'],
            'jenkins': ['ci/cd'],
            'react': ['javascript'],
            'django': ['python'],
            'flask': ['python'],
        }

        expanded = set(processed)
        for skill in processed:
            if skill in implied:
                for implied_skill in implied[skill]:
                    if implied_skill in self.skills_list:
                        expanded.add(implied_skill)

        return expanded
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

        HARD_WEIGHT = 1.0
        SOFT_WEIGHT = 0.3

        weighted_matched = 0
        weighted_total = 0

        for skill in job_skills:
            category = self.skill_categories.get(skill, 'Unknown')
            weight = SOFT_WEIGHT if category == 'Soft Skill' else HARD_WEIGHT
            weighted_total += weight
            if skill in matched:
                weighted_matched += weight

        if weighted_total == 0:
            return 0

        score = (weighted_matched / weighted_total) * 100
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