# main.py
# Entry point — runs the entire application

from data_manager import DataManager
from analyzer import Analyzer
from ml_model import MLModel
from evaluator import Evaluator
from charts import Charts
from job_selector import JobSelector
from field_finder import FieldFinder
from datetime import datetime

# ============================================
# HELPER — Print separator
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
# HELPER — Get student skills
# ============================================
def get_student_skills():
    print_separator("ENTER YOUR SKILLS")
    print("\n  Enter your skills separated by commas.")
    print("  Example: Python, Git, SQL, Communication\n")
    while True:
        raw = input("  Your skills: ").strip()
        if raw:
            return raw
        print("  [!] Please enter at least one skill.")

# ============================================
# HELPER — Print analysis results
# ============================================
def print_results(result, job_title, company):
    score = result['match_score']
    
    # score indicator
    if score >= 70:
        indicator = "🟢"
    elif score >= 40:
        indicator = "🟡"
    else:
        indicator = "🔴"

    print("\n" + "=" * 55)
    print(f"  {company} — {job_title}")
    print("=" * 55)
    print(f"\n  Match Score: {score}% {indicator}")
    print(f"  {'Strong match' if score >= 70 else 'Moderate match' if score >= 40 else 'Low match'}")

    print(f"\n  ✓ Matched ({len(result['matched'])}):", end=" ")
    if result['matched']:
        print(", ".join(sorted(result['matched'])))
    else:
        print("None")

    print(f"\n  ✗ Missing ({len(result['missing'])}):", end=" ")
    if result['missing']:
        print(", ".join(sorted(result['missing'])))
    else:
        print("None — perfect match!")

    if result['extra']:
        print(f"\n  + Extra ({len(result['extra'])}):", end=" ")
        print(", ".join(sorted(result['extra'])))

# ============================================
# HELPER — Print ML predictions
# ============================================
def print_predictions(models, result):
    predictions = []
    for model in models:
        prediction, confidence = model.predict(
            result['match_score'],
            result['matched_count'],
            result['missing_count'],
            result['total_required']
        )
        name = model.algorithm.replace('_', ' ').title()
        predictions.append(f"{name}: {prediction} ({confidence}%)")

    print(f"\n  ML: {' | '.join(predictions)}")

# ============================================
# HELPER — Print recommendations
# ============================================
def print_recommendations(result):
    print(f"\n  💡 {result['recommendation_message']}")
    if result['missing']:
        top3 = sorted(result['missing'])[:3]
        print(f"  Learn next: {', '.join(top3)}")
    print("=" * 55)

# ============================================
# FEATURE 1 — Analyze a job
# ============================================
def analyze_job(analyzer, models, dm, ch, js):
    student_input = get_student_skills()
    job_description, job_title, company = js.choose_job()

    result = analyzer.analyze(student_input, job_description)

    if result is None:
        print("\n  [!] No recognizable skills found in job.")
        return

    print_results(result, job_title, company)
    print_predictions(models, result)
    print_recommendations(result)

    result['date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    result['job_title'] = job_title
    result['company'] = company
    dm.save_analysis(result)

    print_separator("CHARTS")
    ch.plot_algorithm_comparison(
        [m.get_metrics() for m in models]
    )
     
    history = dm.get_history()
    ch.plot_missing_skills(history)
    ch.plot_score_progress(history)
    print("\n  Charts saved to output/ folder.")

# ============================================
# FEATURE 2 — Field Finder
# ============================================
def field_finder_menu(ff, dm, ch):
    print_separator("FIELD FINDER")
    print("\n  1. Find best field for me (check all fields)")
    print("  2. Analyze one specific field")
    print()

    while True:
        try:
            choice = int(input("  Enter choice (1-2): "))
            if 1 <= choice <= 2:
                break
            print("  [!] Enter 1 or 2.")
        except ValueError:
            print("  [!] Please enter a valid number.")

    # get student skills
    student_input = get_student_skills()

    if choice == 1:
        # analyze all fields
        results = ff.analyze_all_fields(student_input)
        ff.print_field_results(results)

        # save field comparison chart
        if results:
            ch.plot_field_comparison(results)

    elif choice == 2:
        # show field selection
        fields = sorted([
            f for f in ff.jobs_df['field'].unique()
            if f != 'Other'
        ])

        print_separator("SELECT FIELD")
        for i, field in enumerate(fields, 1):
            print(f"  {i}. {field}")
        print()

        while True:
            try:
                idx = int(input("  Enter field number: "))
                if 1 <= idx <= len(fields):
                    selected_field = fields[idx - 1]
                    break
                print(f"  [!] Enter number between 1 and {len(fields)}")
            except ValueError:
                print("  [!] Please enter a valid number.")

        print(f"\n  [Analyzing {selected_field}...]\n")
        result = ff.analyze_field(student_input, selected_field)
        ff.print_single_field_results(result)
        
# ============================================
# FEATURE 3 — View algorithm comparison
# ============================================
def view_algorithm_comparison(ev):
    ev.print_comparison_table()
    ev.print_classification_reports()

# ============================================
# FEATURE 4 — View my progress
# ============================================
def view_progress(dm, ev, ch):
    history = dm.get_history()

    if not history:
        print("\n  [!] No analyses yet. Analyze a job first.")
        return

    ev.print_history_analysis(history)
    ch.plot_score_progress(history)
    ch.plot_missing_skills(history)
    print("\n  Progress charts saved to output/ folder.")
    

# ============================================
# MAIN MENU
# ============================================
def show_menu(student_name):
    print_separator(f"MAIN MENU — Welcome {student_name.title()}")
    print("\n  What would you like to do?\n")
    print("  1. Analyze a job")
    print("  2. Find best field for me")
    print("  3. View algorithm comparison")
    print("  4. View my progress")
    print("  5. Exit")
    print()

    while True:
        try:
            choice = int(input("  Enter choice (1-5): "))
            if 1 <= choice <= 5:
                return choice
            print("  [!] Enter number between 1 and 5.")
        except ValueError:
            print("  [!] Please enter a valid number.")

# ============================================
# MAIN — Run the application
# ============================================
def main():
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

    # setup
    ev = Evaluator(models)
    ch = Charts(student_name=dm.student_name)
    analyzer = Analyzer(dm)
    js = JobSelector(dm)
    ff = FieldFinder(dm, analyzer)

    # main loop
    while True:
        choice = show_menu(name)

        if choice == 1:
            analyze_job(analyzer, models, dm, ch, js)

        elif choice == 2:
            field_finder_menu(ff, dm, ch)

        elif choice == 3:
            view_algorithm_comparison(ev)

        elif choice == 4:
            view_progress(dm, ev, ch)

        elif choice == 5:
            print_separator("GOODBYE")
            print(f"\n  Goodbye {name.title()}!")
            print(f"  Your progress has been saved.")
            print("\n" + "=" * 55 + "\n")
            break

if __name__ == "__main__":
    main()