# charts.py
# Responsible for generating and saving all charts

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# ============================================
# CLASS — Charts
# ============================================
class Charts:

    def __init__(self, output_dir="output", student_name="student"):
        self.output_dir = output_dir
        self.student_name = student_name
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    # ----------------------------------------
    # Save figure helper
    # ----------------------------------------
    def save_figure(self, filename):
        named_file = f"{self.student_name}_{filename}"
        path = os.path.join(self.output_dir, named_file)
        plt.savefig(path, bbox_inches='tight', dpi=100)
        plt.close()
        print(f"[OK] Chart saved → {path}")

    # ----------------------------------------
    # Chart 1 — Match Score Bar Chart
    # ----------------------------------------
    def plot_match_score(self, matched, missing):
        labels = ['Matched Skills', 'Missing Skills']
        values = [len(matched), len(missing)]
        colors = ['#2ecc71', '#e74c3c']

        plt.figure(figsize=(8, 5))
        bars = plt.bar(labels, values, color=colors, width=0.4)

        for bar, val in zip(bars, values):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                str(val),
                ha='center',
                fontsize=12,
                fontweight='bold'
            )

        plt.title(
            f'Skill Match Overview — {self.student_name.title()}',
            fontsize=14,
            fontweight='bold'
        )
        plt.ylabel('Number of Skills')
        plt.ylim(0, max(values) + 2)
        plt.tight_layout()
        self.save_figure('match_chart.png')

    # ----------------------------------------
    # Chart 2 — Algorithm Comparison Bar Chart
    # ----------------------------------------
    def plot_algorithm_comparison(self, metrics_list):
        algorithms = []
        accuracy = []
        precision = []
        recall = []
        f1 = []

        for m in metrics_list:
            algorithms.append(
                m['algorithm'].replace('_', ' ').title()
            )
            accuracy.append(m['accuracy'])
            precision.append(m['precision'])
            recall.append(m['recall'])
            f1.append(m['f1_score'])

        x = np.arange(len(algorithms))
        width = 0.2

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.bar(x - 1.5*width, accuracy,  width, label='Accuracy',  color='#3498db')
        ax.bar(x - 0.5*width, precision, width, label='Precision', color='#2ecc71')
        ax.bar(x + 0.5*width, recall,    width, label='Recall',    color='#e67e22')
        ax.bar(x + 1.5*width, f1,        width, label='F1 Score',  color='#9b59b6')

        ax.set_title(
            'Algorithm Performance Comparison',
            fontsize=14,
            fontweight='bold'
        )
        ax.set_ylabel('Score (%)')
        ax.set_xticks(x)
        ax.set_xticklabels(algorithms)
        ax.set_ylim(0, 110)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        self.save_figure('algorithm_comparison.png')

    # ----------------------------------------
    # Chart 3 — Confusion Matrix Heatmap
    # ----------------------------------------
    def plot_confusion_matrix(self, model):
        cm = model.get_confusion_matrix()
        if cm is None:
            return

        labels = ["Good Fit", "Needs Work", "Not Ready"]
        name = model.algorithm.replace('_', ' ').title()

        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=labels,
            yticklabels=labels
        )

        plt.title(
            f'Confusion Matrix — {name}',
            fontsize=14,
            fontweight='bold'
        )
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.tight_layout()

        filename = f"confusion_matrix_{model.algorithm}.png"
        self.save_figure(filename)

    # ----------------------------------------
    # Chart 4 — Missing Skills Frequency
    # ----------------------------------------
    def plot_missing_skills(self, history):
        if not history:
            print("[!] No history to plot.")
            return

        missing_freq = {}
        for entry in history:
            for skill in entry.get('missing', []):
                missing_freq[skill] = missing_freq.get(skill, 0) + 1

        if not missing_freq:
            print("[!] No missing skills recorded.")
            return

        sorted_skills = sorted(
            missing_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        skills = [s[0] for s in sorted_skills]
        counts = [s[1] for s in sorted_skills]

        plt.figure(figsize=(10, 6))
        bars = plt.barh(skills, counts, color='#e74c3c')

        for bar, val in zip(bars, counts):
            plt.text(
                bar.get_width() + 0.1,
                bar.get_y() + bar.get_height() / 2,
                str(val),
                va='center',
                fontsize=10
            )

        plt.title(
            f'Most Frequently Missing Skills — {self.student_name.title()}',
            fontsize=14,
            fontweight='bold'
        )
        plt.xlabel('Times Missing')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        self.save_figure('missing_skills.png')

    # ----------------------------------------
    # Chart 5 — Score Progress Over Time
    # ----------------------------------------
    def plot_score_progress(self, history):
        if len(history) < 2:
            print("[!] Need at least 2 analyses to plot progress.")
            return

        scores = [
            entry.get('match_score', 0)
            for entry in history
        ]
        analyses = list(range(1, len(scores) + 1))

        plt.figure(figsize=(10, 5))
        plt.plot(
            analyses,
            scores,
            marker='o',
            color='#3498db',
            linewidth=2,
            markersize=8
        )

        plt.title(
            f'Match Score Progress — {self.student_name.title()}',
            fontsize=14,
            fontweight='bold'
        )
        plt.xlabel('Analysis Number')
        plt.ylabel('Match Score (%)')
        plt.ylim(0, 110)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        self.save_figure('score_progress.png')