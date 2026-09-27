# field_finder.py
# Analyzes student skills against entire field
# Tells student which field suits them best

import pandas as pd
from analyzer import Analyzer

# ============================================
# CLASS — FieldFinder
# ============================================
class FieldFinder:

    def __init__(self, data_manager, analyzer):
        self.dm = data_manager
        self.analyzer = analyzer
        self.jobs_df = data_manager.get_jobs()

    # ----------------------------------------
    # Analyze student against one entire field
    # ----------------------------------------
    def analyze_field(self, student_input, field):
        jobs = self.jobs_df[
            self.jobs_df['field'] == field
        ].reset_index(drop=True)

        if len(jobs) == 0:
            return None

        scores = []
        missing_freq = {}
        best_job = None
        best_score = -1

        for i, row in jobs.iterrows():
            result = self.analyzer.analyze(
                student_input,
                row['description']
            )

            if result is None:
                continue

            score = result['match_score']
            scores.append(score)

            # track missing skills frequency
            for skill in result['missing']:
                missing_freq[skill] = missing_freq.get(skill, 0) + 1

            # track best matching job
            if score > best_score:
                best_score = score
                best_job = {
                    'company': row['company'],
                    'title': row['title'],
                    'level': row['level'],
                    'score': score
                }

        if not scores:
            return None

        avg_score = round(sum(scores) / len(scores), 2)

        # sort missing skills by frequency
        sorted_missing = sorted(
            missing_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            'field': field,
            'total_jobs': len(scores),
            'avg_score': avg_score,
            'best_job': best_job,
            'top_missing': sorted_missing,
            'all_scores': scores
        }

    # ----------------------------------------
    # Analyze student against ALL fields
    # ----------------------------------------
    def analyze_all_fields(self, student_input):
        fields = self.jobs_df['field'].unique().tolist()
        fields = [f for f in fields if f != 'Other']

        results = []
        print("\n  [Analyzing all fields...]\n")

        for field in fields:
            print(f"  Checking {field}...")
            result = self.analyze_field(student_input, field)
            if result:
                results.append(result)

        # sort by average score
        results.sort(key=lambda x: x['avg_score'], reverse=True)
        return results

    # ----------------------------------------
    # Print field analysis results
    # ----------------------------------------
    def print_field_results(self, results):
        if not results:
            print("\n  [!] No results found.")
            return

        print("\n" + "=" * 55)
        print("  FIELD MATCH RESULTS")
        print("=" * 55)
        print(f"\n  {'Field':<25} {'Avg Score':>10} {'Jobs':>6}")
        print(f"  {'─'*25} {'─'*10} {'─'*6}")

        for r in results:
            bar_length = int(r['avg_score'] / 5)
            bar = '█' * bar_length
            print(
                f"\n  {r['field']:<25} "
                f"{r['avg_score']:>8}%  "
                f"({r['total_jobs']} jobs)"
            )
            print(f"  {bar}")

        # best field
        best = results[0]
        print("\n" + "=" * 55)
        print(f"\n  🎯 Best Field For You: {best['field']}")
        print(f"     Average Match: {best['avg_score']}%")

        # best job in best field
        if best['best_job']:
            print(f"\n  Best Job Match:")
            print(f"     Company: {best['best_job']['company']}")
            print(f"     Title:   {best['best_job']['title']}")
            print(f"     Level:   {best['best_job']['level']}")
            print(f"     Score:   {best['best_job']['score']}%")

        # top missing skills in best field
        if best['top_missing']:
            print(f"\n  Top Skills to Learn for {best['field']}:")
            for i, (skill, count) in enumerate(best['top_missing'][:5], 1):
                print(f"     {i}. {skill} (missing in {count} jobs)")

        print("\n" + "=" * 55)

    # ----------------------------------------
    # Print single field results
    # ----------------------------------------
    def print_single_field_results(self, result):
        if not result:
            print("\n  [!] No results found.")
            return

        print("\n" + "=" * 55)
        print(f"  FIELD ANALYSIS — {result['field'].upper()}")
        print("=" * 55)
        print(f"\n  Jobs analyzed:   {result['total_jobs']}")
        print(f"  Average score:   {result['avg_score']}%")

        if result['avg_score'] >= 70:
            verdict = "Strong fit  You should apply to jobs in this field"
        elif result['avg_score'] >= 50:
            verdict = "Good fit  Work on missing skills then apply"
        elif result['avg_score'] >= 30:
            verdict = "Moderate fit   Significant learning needed"
        else:
            verdict = "Low fit  Consider a different field first"

        print(f"\n  Verdict: {verdict}")

        if result['best_job']:
            print(f"\n  Best Matching Job:")
            print(f"     Company: {result['best_job']['company']}")
            print(f"     Title:   {result['best_job']['title']}")
            print(f"     Score:   {result['best_job']['score']}%")

        if result['top_missing']:
            print(f"\n  Most Missing Skills:")
            for i, (skill, count) in enumerate(result['top_missing'][:7], 1):
                print(f"     {i}. {skill:<25} missing in {count} jobs")

        print("\n" + "=" * 55)