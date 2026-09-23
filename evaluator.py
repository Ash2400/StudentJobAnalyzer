# evaluator.py
# Responsible for comparing all 3 algorithms and printing results

# ============================================
# CLASS — Evaluator
# ============================================
class Evaluator:

    def __init__(self, models):
        self.models = models
        self.metrics = []
        self.collect_metrics()

    # ----------------------------------------
    # Collect metrics from all models
    # ----------------------------------------
    def collect_metrics(self):
        for model in self.models:
            metrics = model.get_metrics()
            if metrics:
                self.metrics.append(metrics)

    # ----------------------------------------
    # Find best algorithm by F1 score
    # ----------------------------------------
    def get_best_algorithm(self):
        if not self.metrics:
            return None
        best = max(self.metrics, key=lambda x: x['f1_score'])
        return best['algorithm']

    # ----------------------------------------
    # Print comparison table
    # ----------------------------------------
    def print_comparison_table(self):
        if not self.metrics:
            print("[!] No metrics available.")
            return

        print("\n")
        print("=" * 55)
        print("         ALGORITHM COMPARISON RESULTS")
        print("=" * 55)
        print(f"{'Algorithm':<25} {'Acc':>6} {'Prec':>6} {'Rec':>6} {'F1':>6}")
        print("-" * 55)

        for m in self.metrics:
            name = m['algorithm'].replace('_', ' ').title()
            print(
                f"{name:<25} "
                f"{m['accuracy']:>5}% "
                f"{m['precision']:>5}% "
                f"{m['recall']:>5}% "
                f"{m['f1_score']:>5}%"
            )

        print("-" * 55)
        best = self.get_best_algorithm()
        best_name = best.replace('_', ' ').title()
        print(f"\n  Best Algorithm: {best_name}")
        print("=" * 55)

    # ----------------------------------------
    # Print classification report
    # ----------------------------------------
    def print_classification_reports(self):
        print("\n")
        print("=" * 55)
        print("         DETAILED CLASSIFICATION REPORTS")
        print("=" * 55)

        for model in self.models:
            name = model.algorithm.replace('_', ' ').title()
            print(f"\n--- {name} ---")
            print(model.get_classification_report())

    # ----------------------------------------
    # Print confusion matrices
    # ----------------------------------------
    def print_confusion_matrices(self):
        labels = ["Good Fit", "Needs Work", "Not Ready"]

        print("\n")
        print("=" * 55)
        print("           CONFUSION MATRICES")
        print("=" * 55)

        for model in self.models:
            name = model.algorithm.replace('_', ' ').title()
            cm = model.get_confusion_matrix()

            if cm is None:
                continue

            print(f"\n--- {name} ---")
            print(f"{'':20}", end="")
            for label in labels:
                print(f"{label:>12}", end="")
            print()

            for i, row_label in enumerate(labels):
                print(f"{row_label:20}", end="")
                for val in cm[i]:
                    print(f"{val:>12}", end="")
                print()

    # ----------------------------------------
    # Print history analysis
    # ----------------------------------------
    def print_history_analysis(self, history):
        if not history:
            print("\n[!] No history yet.")
            return

        print("\n")
        print("=" * 55)
        print("           HISTORY ANALYSIS")
        print("=" * 55)

        # count missing skills frequency
        missing_freq = {}
        scores = []

        for entry in history:
            scores.append(entry.get('match_score', 0))
            for skill in entry.get('missing', []):
                missing_freq[skill] = missing_freq.get(skill, 0) + 1

        # print score stats
        if scores:
            avg_score = round(sum(scores) / len(scores), 2)
            print(f"\n  Total analyses:    {len(history)}")
            print(f"  Average score:     {avg_score}%")
            print(f"  Highest score:     {max(scores)}%")
            print(f"  Lowest score:      {min(scores)}%")

        # print most missing skills
        if missing_freq:
            sorted_missing = sorted(
                missing_freq.items(),
                key=lambda x: x[1],
                reverse=True
            )
            print(f"\n  Most Missing Skills:")
            print(f"  {'Skill':<25} {'Times Missing':>15}")
            print(f"  {'-'*40}")
            for skill, count in sorted_missing[:10]:
                print(f"  {skill:<25} {count:>15}")

        print("=" * 55)