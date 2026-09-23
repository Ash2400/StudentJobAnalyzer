# data_manager.py
# Responsible for reading and writing all data files

import pandas as pd
import json
import os

# ============================================
# CONSTANTS — file paths
# ============================================
SKILLS_FILE = "data/skills.csv"
ALIASES_FILE = "data/aliases.json"
TRAINING_FILE = "data/training_data.csv"
HISTORY_DIR = "data/history"


# ============================================
# CLASS — DataManager
# ============================================
class DataManager:

    def __init__(self):
        self.skills_df = None
        self.aliases = {}
        self.training_df = None
        self.history = []
        self.student_name = None
        self.history_file = None
        self.load_all()

    # ----------------------------------------
    # Load all data files at startup
    # ----------------------------------------
    def load_all(self):
        self.skills_df = self.load_skills()
        self.aliases = self.load_aliases()
        self.training_df = self.load_training_data()

    # ----------------------------------------
    # Set student name and load their history
    # ----------------------------------------
    def set_student(self, name):
        self.student_name = name.strip().lower()
        if not os.path.exists(HISTORY_DIR):
            os.makedirs(HISTORY_DIR)
        self.history_file = (
            f"{HISTORY_DIR}/history_{self.student_name}.json"
        )
        self.history = self.load_history()
        print(f"[OK] Student set to: {self.student_name}")

    # ----------------------------------------
    # Load skills.csv
    # ----------------------------------------
    def load_skills(self):
        try:
            df = pd.read_csv(SKILLS_FILE)
            df['skill'] = df['skill'].str.lower().str.strip()
            print(f"[OK] Loaded {len(df)} skills from skills.csv")
            return df
        except FileNotFoundError:
            print("[ERROR] skills.csv not found")
            return pd.DataFrame(columns=['skill', 'category'])

    # ----------------------------------------
    # Load aliases.json
    # ----------------------------------------
    def load_aliases(self):
        try:
            with open(ALIASES_FILE, 'r') as f:
                aliases = json.load(f)
            print(f"[OK] Loaded {len(aliases)} aliases from aliases.json")
            return aliases
        except FileNotFoundError:
            print("[ERROR] aliases.json not found")
            return {}

    # ----------------------------------------
    # Load training_data.csv
    # ----------------------------------------
    def load_training_data(self):
        try:
            df = pd.read_csv(TRAINING_FILE)
            print(f"[OK] Loaded {len(df)} training samples")
            return df
        except FileNotFoundError:
            print("[ERROR] training_data.csv not found")
            return pd.DataFrame()

    # ----------------------------------------
    # Load student history
    # ----------------------------------------
    def load_history(self):
        if not self.history_file:
            return []
        try:
            if not os.path.exists(self.history_file):
                print("[OK] No past analyses yet")
                return []
            if os.path.getsize(self.history_file) == 0:
                print("[OK] No past analyses yet")
                return []
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            print(f"[OK] Loaded {len(history)} past analyses")
            return history
        except Exception as e:
            print(f"[ERROR] Could not load history: {e}")
            return []

    # ----------------------------------------
    # Save analysis to student history
    # ----------------------------------------
    def save_analysis(self, analysis):
        if not self.history_file:
            print("[ERROR] No student set.")
            return
        self.history.append(analysis)
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=4)
            print(f"[OK] Analysis saved for {self.student_name}")
        except Exception as e:
            print(f"[ERROR] Could not save analysis: {e}")

    # ----------------------------------------
    # Get list of all known skills
    # ----------------------------------------
    def get_skills_list(self):
        return self.skills_df['skill'].tolist()

    # ----------------------------------------
    # Get aliases dictionary
    # ----------------------------------------
    def get_aliases(self):
        return self.aliases

    # ----------------------------------------
    # Get training dataframe
    # ----------------------------------------
    def get_training_data(self):
        return self.training_df

    # ----------------------------------------
    # Get history list
    # ----------------------------------------
    def get_history(self):
        return self.history