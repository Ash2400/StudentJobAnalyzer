# main.py
# Entry point — runs the entire application

from data_manager import DataManager
from analyzer import Analyzer
from ml_model import MLModel
from evaluator import Evaluator
from charts import Charts
from datetime import datetime

# ============================================
# HELPER — Print formatted separator
# ============================================
def print_separator(title=""):
    print("\n" + "=" * 55)
    if title:
        print(f"  {title}")
        print("=" * 55)

# ============================================
# HELPER — Get student name
# ============================================
def get_student_name():
    print_separator("WELCOME")
    print("\n  Enter your name to continue.")
    print("  Your history and charts will be saved separately.\n")
    while True:
        name = input("  Your name: ").strip()
        if name:
            return name
        print("  [!] Please enter your name.")

# ============================================
# HELPER — Get student skills input
# ============================================
def get_student_skills():
    print_separator("STEP 1 — Enter Your Skills")
    print("\n  Enter your skills separated by commas.")
    print("  Example: Python, Git, SQL, Communication\n")
    while True:
        raw = input("  Your skills: ").strip()
        if raw:
            return raw
        print("  [!] Please enter at least one skill.")

# ============================================
# HELPER — Get job description input
# ============================================
def get_job_description():
    print_separator("STEP 2 — Paste Job Description")
    print("\n  Paste the job description below.")
    print("  Press ENTER twice when done.\n")
    lines = []
    while True:
        line = input()
        if line == "":
            if lines:
                break
        else:
            lines.append(line)
    return " ".join(lines)

# ============================================
# HELPER — Print analysis results
# ============================================
def print_results(result):
    print_separator("ANALYSIS RESULTS")

    print(f"\n  Match Score: {result['match_score']}%")

    # matched skills
    print(f"\n  Matched Skills ({len(result['matched'])}):")
    if result['matched']:
        for skill in sorted(result['matched']):
            print(f"    ✓ {skill}")
    else:
        print("    None")

    # missing skills
    print(f"\n  Missing Skills ({len(result['missing'])}):")
    if result['missing']:
        for skill in sorted(result['missing']):
            print(f"    ✗ {skill}")
    else:
        print("    None — perfect match!")

    # extra skills
    if result['extra']:
        print(f"\n  Extra Skills You Have ({len(result['extra'])}):")
        for skill in sorted(result['extra']):
            print(f"    + {skill}")

# ============================================
# HELPER — Print ML predictions
# ============================================
def print_predictions(models, result):
    print_separator("ML PREDICTIONS")

    for model in models:
        prediction, confidence = model.predict(
            result['match_score'],
            result['matched_count'],
            result['missing_count'],
            result['total_required']
        )
        name = model.algorithm.replace('_', ' ').title()
        print(f"\n  {name:<25} → {prediction} ({confidence}% confident)")

# ============================================
# HELPER — Print recommendations
# ============================================
def print_recommendations(result):
    print_separator("RECOMMENDATION")
    print(f"\n  {result['recommendation_message']}")

    if result['recommendations']:
        print("\n  Skills to learn next:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"    {i}. {rec}")

# ============================================
# HELPER — Ask to run again
# ============================================
def ask_run_again():
    print("\n")
    choice = input("  Analyze another job? (yes/no): ").strip().lower()
    return choice in ['yes', 'y']

# ============================================
# MAIN — Run the application
# ============================================
def main():
    # welcome screen
    print("\n" + "=" * 55)
    print("   STUDENT JOB & INTERNSHIP READINESS ANALYZER")
    print("=" * 55)
    print("  Analyzing your job readiness using ML algorithms")
    print("=" * 55)

    # load data
    print("\n  [Loading data...]\n")
    dm = DataManager()

    # get student name
    name = get_student_name()
    dm.set_student(name)

    # train models
    print("\n  [Training ML models...]\n")
    rf  = MLModel(dm, 'random_forest')
    lr  = MLModel(dm, 'logistic_regression')
    knn = MLModel(dm, 'knn')
    models = [rf, lr, knn]

    # evaluator and charts
    ev = Evaluator(models)
    ch = Charts(student_name=dm.student_name)
    analyzer = Analyzer(dm)

    # print algorithm comparison
    ev.print_comparison_table()

    # main loop
    while True:
        student_input = get_student_skills()
        job_description = get_job_description()

        result = analyzer.analyze(student_input, job_description)

        if result is None:
            print("\n  [!] Could not analyze. Try a different job description.")
            continue

        print_results(result)
        print_predictions(models, result)
        print_recommendations(result)

        # save analysis
        result['date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        dm.save_analysis(result)

        # generate charts
        print_separator("CHARTS")
        ch.plot_match_score(result['matched'], result['missing'])
        ch.plot_algorithm_comparison(ev.metrics)
        ch.plot_confusion_matrix(rf)
        history = dm.get_history()
        ch.plot_missing_skills(history)
        ch.plot_score_progress(history)
        print("\n  Charts saved to output/ folder.")

        if not ask_run_again():
            print_separator("GOODBYE")
            print(f"\n  Goodbye {name.title()}!")
            print(f"  Your progress has been saved.")
            print(f"  Charts saved to output/ folder.")
            print("\n" + "=" * 55 + "\n")
            break

if __name__ == "__main__":
    main()