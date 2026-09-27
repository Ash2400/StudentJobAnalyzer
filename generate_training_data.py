# generate_training_data.py
# Run once to generate balanced training data from jobs.csv

import pandas as pd
import random
from data_manager import DataManager
from analyzer import Analyzer

# ============================================
# SETTINGS
# ============================================
TARGET_PER_LABEL = 600    # 600 per label = 1800 total
OUTPUT_FILE = "data/training_data.csv"
RANDOM_SEED = 42

random.seed(RANDOM_SEED)

# ============================================
# LOAD DATA
# ============================================
print("[...] Loading data...")
dm = DataManager()
analyzer = Analyzer(dm)
skills_list = dm.get_skills_list()

print(f"[OK] Loaded {len(skills_list)} skills")
print(f"[OK] Loaded {len(dm.jobs_df)} jobs")

# ============================================
# LABEL FUNCTION
# ============================================
def get_label(score):
    if score >= 70:
        return "Good Fit"
    elif score >= 40:
        return "Needs Work"
    else:
        return "Not Ready"

# ============================================
# EXTRACT JOB SKILLS
# ============================================
print("[...] Extracting skills from jobs...")

job_skills_data = []
for index, job in dm.jobs_df.iterrows():
    job_skills = analyzer.extract_skills(job['description'])
    if len(job_skills) >= 2:
        job_skills_data.append(list(job_skills))

print(f"[OK] Found {len(job_skills_data)} valid jobs")

# ============================================
# GENERATE BALANCED TRAINING DATA
# ============================================
print("[...] Generating balanced training data...")

good_fit_rows = []
needs_work_rows = []
not_ready_rows = []

max_attempts = 100000
attempts = 0

while (
    len(good_fit_rows) < TARGET_PER_LABEL or
    len(needs_work_rows) < TARGET_PER_LABEL or
    len(not_ready_rows) < TARGET_PER_LABEL
) and attempts < max_attempts:

    attempts += 1

    # pick random job
    job_skills = random.choice(job_skills_data)
    total_required = len(job_skills)

    if total_required == 0:
        continue

    # randomly decide target label for this row
    # then generate student skills to match that label
    target_label = random.choice(["Good Fit", "Needs Work", "Not Ready"])

    # skip if we already have enough of this label
    if target_label == "Good Fit" and len(good_fit_rows) >= TARGET_PER_LABEL:
        continue
    if target_label == "Needs Work" and len(needs_work_rows) >= TARGET_PER_LABEL:
        continue
    if target_label == "Not Ready" and len(not_ready_rows) >= TARGET_PER_LABEL:
        continue

    # generate student skills to match target label
    if target_label == "Good Fit":
        # student has 70-100% of job skills
        num_from_job = random.randint(
            max(1, int(total_required * 0.7)),
            total_required
        )
    elif target_label == "Needs Work":
        # student has 40-69% of job skills
        num_from_job = random.randint(
            max(1, int(total_required * 0.4)),
            max(1, int(total_required * 0.69))
        )
    else:
        # student has 0-39% of job skills
        num_from_job = random.randint(
            0,
            max(0, int(total_required * 0.39))
        )

    # clamp to valid range
    num_from_job = min(num_from_job, total_required)

    # pick matching skills from job
    student_skills = set(
        random.sample(job_skills, num_from_job)
    )

    # add some random extra skills
    other_skills = [s for s in skills_list if s not in job_skills]
    if other_skills:
        num_extra = random.randint(0, 5)
        extra = random.sample(other_skills, min(num_extra, len(other_skills)))
        student_skills.update(extra)

    # calculate actual score
    matched = student_skills & set(job_skills)
    missing = set(job_skills) - student_skills
    matched_count = len(matched)
    missing_count = len(missing)
    match_score = round((matched_count / total_required) * 100, 2)
    actual_label = get_label(match_score)

    # only add if actual label matches target
    if actual_label != target_label:
        continue

    row = {
        "match_score": match_score,
        "matched_count": matched_count,
        "missing_count": missing_count,
        "total_required": total_required,
        "label": actual_label
    }

    if actual_label == "Good Fit":
        good_fit_rows.append(row)
    elif actual_label == "Needs Work":
        needs_work_rows.append(row)
    else:
        not_ready_rows.append(row)

# ============================================
# COMBINE AND ADD NOISE
# ============================================
all_rows = good_fit_rows + needs_work_rows + not_ready_rows
df = pd.DataFrame(all_rows)
df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

# add 15% noise — flip some labels randomly
print("[...] Adding noise to training data...")
noise_rate = 0.15
noise_count = int(len(df) * noise_rate)
noise_indices = random.sample(range(len(df)), noise_count)

label_options = ["Good Fit", "Needs Work", "Not Ready"]

for idx in noise_indices:
    current_label = df.at[idx, 'label']
    wrong_labels = [l for l in label_options if l != current_label]
    df.at[idx, 'label'] = random.choice(wrong_labels)

print(f"[OK] Added noise to {noise_count} rows ({noise_rate*100}%)")

# ============================================
# SAVE
# ============================================
df.to_csv(OUTPUT_FILE, index=False)

# ============================================
# SUMMARY
# ============================================
print(f"\n[OK] Generated {len(df)} training rows")
print(f"[OK] Saved to {OUTPUT_FILE}")
print(f"\nLabel distribution:")
print(df['label'].value_counts().to_string())
print(f"\nScore statistics:")
print(df['match_score'].describe().round(2).to_string())