# generate_skills.py
# Generates skills.csv from real job data
# Run once then delete

import pandas as pd
import re
from collections import Counter

# load jobs
df = pd.read_csv('data/jobs.csv')

# current skills for reference
current_skills = pd.read_csv('data/skills.csv')
current_list = current_skills['skill'].str.lower().tolist()

# category mapping keywords
category_map = {
    'Programming': ['python', 'java', 'javascript', 'c++', 'c#', 'r', 'swift', 'kotlin', 'go', 'rust', 'typescript', 'php', 'ruby', 'scala', 'bash', 'perl', 'matlab'],
    'Database': ['sql', 'mysql', 'postgresql', 'mongodb', 'sqlite', 'oracle', 'redis', 'cassandra', 'dynamodb', 'firebase', 'elasticsearch', 'snowflake'],
    'Data Science': ['pandas', 'numpy', 'matplotlib', 'seaborn', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'xgboost', 'lightgbm', 'opencv', 'nltk', 'spacy'],
    'Machine Learning': ['machine learning', 'deep learning', 'neural networks', 'computer vision', 'natural language processing', 'reinforcement learning', 'transfer learning'],
    'Cloud': ['aws', 'azure', 'google cloud', 'heroku', 'docker', 'kubernetes'],
    'Web Development': ['django', 'flask', 'react', 'node.js', 'angular', 'vue.js', 'html', 'css', 'fastapi', 'spring boot', 'graphql', 'rest api'],
    'Tools': ['git', 'linux', 'excel', 'tableau', 'power bi', 'jira', 'jenkins', 'figma'],
    'Soft Skill': ['communication', 'teamwork', 'leadership', 'problem solving', 'critical thinking', 'adaptability', 'creativity', 'collaboration', 'attention to detail', 'time management'],
    'Project Management': ['agile', 'scrum', 'kanban', 'devops', 'ci/cd'],
    'Testing': ['selenium', 'pytest', 'junit', 'quality assurance'],
}

# count skill frequency in job descriptions
skill_counts = Counter()
for desc in df['description'].dropna():
    desc_lower = desc.lower()
    for category, skills in category_map.items():
        for skill in skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', desc_lower):
                skill_counts[skill] += 1

# keep skills mentioned in at least 3 jobs
MIN_FREQUENCY = 2
rows = []
for skill, count in skill_counts.items():
    if count >= MIN_FREQUENCY:
        category = 'Other'
        for cat, skills in category_map.items():
            if skill in skills:
                category = cat
                break
        rows.append({
            'skill': skill,
            'category': category,
            'frequency': count
        })

# sort by frequency
result_df = pd.DataFrame(rows)
result_df = result_df.sort_values('frequency', ascending=False)

print(f"Skills found in jobs: {len(result_df)}")
print(f"\nTop 20 most frequent:")
print(result_df.head(20)[['skill', 'category', 'frequency']].to_string())
print(f"\nCategory distribution:")
print(result_df['category'].value_counts().to_string())

# add important missing skills manually
extra_skills = [
    {'skill': 'data analysis', 'category': 'Data Science'},
    {'skill': 'data visualization', 'category': 'Data Science'},
    {'skill': 'statistical analysis', 'category': 'Data Science'},
    {'skill': 'matplotlib', 'category': 'Data Science'},
    {'skill': 'seaborn', 'category': 'Data Science'},
    {'skill': 'django', 'category': 'Web Development'},
    {'skill': 'fastapi', 'category': 'Web Development'},
    {'skill': 'adaptability', 'category': 'Soft Skill'},
    {'skill': 'decision making', 'category': 'Soft Skill'},
    {'skill': 'presentation skills', 'category': 'Soft Skill'},
    {'skill': 'research', 'category': 'Academic'},
    {'skill': 'xgboost', 'category': 'Data Science'},
    {'skill': 'statistical modeling', 'category': 'Data Science'},
]

extra_df = pd.DataFrame(extra_skills)
final_df = pd.concat([result_df[['skill', 'category']], extra_df], ignore_index=True)
final_df = final_df.drop_duplicates(subset='skill')

final_df.to_csv('data/skills_from_jobs.csv', index=False)
print(f"\nTotal skills saved: {len(final_df)}")
print("Saved to data/skills_from_jobs.csv")
print(f"\nSaved to data/skills_from_jobs.csv")
print("Review it then rename to skills.csv if satisfied")