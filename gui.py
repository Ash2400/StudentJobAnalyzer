# gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import threading
from data_manager import DataManager
from analyzer import Analyzer
from ml_model import MLModel
from evaluator import Evaluator
from charts import Charts
from field_finder import FieldFinder

LEVEL_ORDER = {
    'Internship': 0, 'Entry level': 1, 'Associate': 2,
    'Mid-Senior level': 3, 'Director': 4, 'Executive': 5,
    'Not Specified': 6, 'Open': 7,
}

class App:
    BG      = "#f5f5f5"
    FG      = "#212121"
    FBGC    = "#ffffff"
    BLUE    = "#1565C0"
    GREEN   = "#2E7D32"
    ORANGE  = "#E65100"
    GRAY    = "#455A64"
    RED     = "#C62828"
    WHITE   = "#ffffff"
    FONT    = ("Arial", 10)
    FONTB   = ("Arial", 10, "bold")
    FONTT   = ("Arial", 13, "bold")

    def __init__(self, root):
        self.root = root
        self.root.title("Student Job & Internship Readiness Analyzer")
        self.root.geometry("780x700")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG)

        # fix ttk dropdown colors
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TCombobox',
            fieldbackground=self.WHITE,
            background=self.WHITE,
            foreground=self.FG,
            selectbackground=self.BLUE,
            selectforeground=self.WHITE,
        )
        style.map('TCombobox',
            fieldbackground=[('readonly', self.WHITE)],
            foreground=[('readonly', self.FG)],
        )

        self.dm = self.analyzer = self.ev = self.ch = self.ff = None
        self.models = []
        self.current_jobs = None
        self.setup_ui()

    def mk_btn(self, parent, text, cmd, color, width=15):
        return tk.Button(
            parent, text=text, command=cmd,
            bg=color, fg=self.FG,
            activebackground=color,
            activeforeground=self.FG,
            font=self.FONT, width=width,
            relief="flat", cursor="hand2",
            padx=4, pady=5
        )

    def mk_label(self, parent, text, bold=False):
        return tk.Label(
            parent, text=text,
            bg=self.FBGC, fg=self.FG,
            font=self.FONTB if bold else self.FONT
        )

    def mk_frame(self, parent, title):
        return tk.LabelFrame(
            parent, text=title,
            bg=self.FBGC, fg=self.FG,
            font=self.FONTB,
            padx=10, pady=8
        )

    def setup_ui(self):
        # title
        tk.Label(
            self.root,
            text="Student Job & Internship Readiness Analyzer",
            font=self.FONTT, bg=self.BG, fg=self.FG, pady=10
        ).pack()

        f = tk.Frame(self.root, bg=self.BG, padx=15)
        f.pack(fill="both", expand=True)

        # student info
        sf = self.mk_frame(f, "Student Info")
        sf.pack(fill="x", pady=4)

        self.mk_label(sf, "Name:").grid(row=0, column=0, sticky="w")
        self.name = tk.Entry(sf, width=25, font=self.FONT,
                             bg=self.WHITE, fg=self.FG,
                             insertbackground=self.FG)
        self.name.grid(row=0, column=1, padx=8, sticky="w")
        self.mk_btn(sf, "Load / Login", self.load_student, self.GREEN).grid(
            row=0, column=2, padx=8)

        self.mk_label(sf, "Skills:").grid(row=1, column=0, sticky="w", pady=6)
        self.skills = tk.Entry(sf, width=52, font=self.FONT,
                               bg=self.WHITE, fg=self.FG,
                               insertbackground=self.FG)
        self.skills.grid(row=1, column=1, columnspan=2, padx=8, sticky="w")
        tk.Label(sf, text="e.g. Python, SQL, Git, Machine Learning",
                 bg=self.FBGC, fg="gray", font=("Arial", 9)).grid(
            row=2, column=1, sticky="w", padx=8)

        # analyze job
        jf = self.mk_frame(f, "Analyze a Job")
        jf.pack(fill="x", pady=4)

        self.mk_label(jf, "Field:").grid(row=0, column=0, sticky="w")
        self.field_var = tk.StringVar()
        self.field_dd = ttk.Combobox(jf, textvariable=self.field_var,
                                     width=28, state="disabled", font=self.FONT)
        self.field_dd.grid(row=0, column=1, padx=8, sticky="w")
        self.field_dd.bind("<<ComboboxSelected>>", self.on_field_selected)
        self.mk_btn(jf, "Analyze Job", self.analyze_job, self.BLUE).grid(
            row=0, column=2, padx=8)

        self.mk_label(jf, "Job:").grid(row=1, column=0, sticky="w", pady=6)
        self.job_var = tk.StringVar()
        self.job_dd = ttk.Combobox(jf, textvariable=self.job_var,
                                   width=55, state="disabled", font=self.FONT)
        self.job_dd.grid(row=1, column=1, columnspan=2, padx=8, sticky="w")

        # field finder
        ff = self.mk_frame(f, "Field Finder")
        ff.pack(fill="x", pady=4)

        self.mk_label(ff, "Analyze:").grid(row=0, column=0, sticky="w")
        self.finder_var = tk.StringVar(value="All Fields")
        self.finder_dd = ttk.Combobox(ff, textvariable=self.finder_var,
                                      width=28, state="disabled", font=self.FONT)
        self.finder_dd.grid(row=0, column=1, padx=8, sticky="w")
        self.analyze_fields_btn = self.mk_btn(
            ff, "Analyze Fields", self.find_field, self.ORANGE)
        self.analyze_fields_btn.grid(row=0, column=2, padx=8)

        # buttons row
        bf = tk.Frame(f, bg=self.BG)
        bf.pack(fill="x", pady=6)
        self.mk_btn(bf, "View Progress", self.view_progress, self.GRAY, 16).pack(
            side="left", padx=4)
        self.mk_btn(bf, "Algorithm Comparison", self.view_comparison, self.GRAY, 20).pack(
            side="left", padx=4)
        self.mk_btn(bf, "Save Charts", self.save_charts, self.GRAY, 14).pack(
            side="left", padx=4)
        self.mk_btn(bf, "Exit", self.root.destroy, self.RED, 8).pack(
            side="right", padx=4)

        # results
        rf = self.mk_frame(f, "Results")
        rf.pack(fill="both", expand=True, pady=4)

        self.result_text = scrolledtext.ScrolledText(
            rf, height=13, font=("Arial", 10),
            bg=self.WHITE, fg=self.FG,
            insertbackground=self.FG,
            state="disabled"
        )
        self.result_text.pack(fill="both", expand=True)

        # status bar
        self.status = tk.StringVar(value="Enter your name and click Load / Login")
        tk.Label(self.root, textvariable=self.status,
                 fg="gray", bg=self.BG, anchor="w",
                 font=("Arial", 9)).pack(fill="x", padx=15, pady=2)

    def display(self, text, clear=True):
        self.result_text.config(state="normal")
        if clear:
            self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text + "\n")
        self.result_text.config(state="disabled")
        self.result_text.see(tk.END)

    def load_student(self):
        name = self.name.get().strip()
        if not name:
            messagebox.showwarning("Missing", "Please enter your name.")
            return
        self.status.set("Loading data and training models...")
        self.root.update()
        try:
            self.dm = DataManager()
            self.dm.set_student(name)
            self.analyzer = Analyzer(self.dm)
            rf  = MLModel(self.dm, 'random_forest')
            lr  = MLModel(self.dm, 'logistic_regression')
            knn = MLModel(self.dm, 'knn')
            self.models = [rf, lr, knn]
            self.ev = Evaluator(self.models)
            self.ch = Charts(student_name=self.dm.student_name)
            self.ff = FieldFinder(self.dm, self.analyzer)

            fields = sorted([
                f for f in self.dm.jobs_df['field'].unique()
                if f != 'Other'
            ])
            self.field_dd['values'] = fields
            self.field_dd['state'] = 'readonly'
            self.finder_dd['values'] = ['All Fields'] + fields
            self.finder_dd['state'] = 'readonly'
            self.finder_var.set('All Fields')

            count = len(self.dm.get_history())
            self.status.set(f"Welcome {name.title()}! {count} past analyses loaded.")
            self.display(
                f"Welcome {name.title()}!\n"
                f"{count} past analyses loaded.\n"
                f"Models trained and ready.\n\n"
                f"Select a field and job to begin."
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_field_selected(self, event):
        field = self.field_var.get()
        jobs = self.dm.jobs_df[self.dm.jobs_df['field'] == field].copy()
        jobs['level_order'] = jobs['level'].map(lambda x: LEVEL_ORDER.get(x, 99))
        jobs = jobs.sort_values('level_order').reset_index(drop=True)
        self.current_jobs = jobs
        job_list = [
            f"{i+1}. [{row['level']}] {row['company']} — {row['title']}"
            for i, row in jobs.iterrows()
        ]
        self.job_dd['values'] = job_list
        self.job_dd['state'] = 'readonly'
        if job_list:
            self.job_var.set(job_list[0])

    def analyze_job(self):
        if not self.dm:
            messagebox.showwarning("Not loaded", "Please load student first.")
            return
        skills = self.skills.get().strip()
        if not skills:
            messagebox.showwarning("Missing", "Please enter your skills.")
            return
        job_sel = self.job_var.get()
        if not job_sel:
            messagebox.showwarning("Missing", "Please select a job.")
            return
        try:
            idx = int(job_sel.split('.')[0]) - 1
            job = self.current_jobs.iloc[idx]
            result = self.analyzer.analyze(skills, job['description'])
            if result is None:
                self.display("No recognizable skills found in job.")
                return

            score = result['match_score']
            ind = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
            out = (
                f"{'='*50}\n"
                f"{job['company']} — {job['title']}\n"
                f"{'='*50}\n"
                f"Match Score: {score}% {ind}\n"
                f"{result['recommendation_message']}\n\n"
                f"✓ Matched ({len(result['matched'])}): "
                f"{', '.join(sorted(result['matched'])) or 'None'}\n\n"
                f"✗ Missing ({len(result['missing'])}): "
                f"{', '.join(sorted(result['missing'])) or 'None'}\n\n"
                f"+ Extra ({len(result['extra'])}): "
                f"{', '.join(sorted(result['extra'])) or 'None'}\n\n"
                f"ML Predictions:\n"
            )
            for model in self.models:
                pred, conf = model.predict(
                    result['match_score'], result['matched_count'],
                    result['missing_count'], result['total_required']
                )
                name = model.algorithm.replace('_', ' ').title()
                out += f"  {name}: {pred} ({conf}%)\n"
            if result['missing']:
                out += f"\n💡 Learn next: {', '.join(sorted(result['missing'])[:3])}"

            self.display(out)
            result['date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            result['job_title'] = job['title']
            result['company'] = job['company']
            self.dm.save_analysis(result)
            self.status.set(f"Saved — {job['title']} at {job['company']}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def find_field(self):
        if not self.dm:
            messagebox.showwarning("Not loaded", "Please load student first.")
            return
        skills = self.skills.get().strip()
        if not skills:
            messagebox.showwarning("Missing", "Please enter your skills.")
            return
        selection = self.finder_var.get()
        self.display("Analyzing fields... please wait (30-60 seconds).")
        self.status.set("Analyzing fields...")
        self.analyze_fields_btn.config(state="disabled")

        def run():
            try:
                results = None
                if selection == 'All Fields':
                    results = self.ff.analyze_all_fields(skills)
                    out = "="*50 + "\nFIELD MATCH RESULTS\n" + "="*50 + "\n\n"
                    out += f"{'Field':<25} {'Score':>8}\n" + "-"*35 + "\n"
                    for r in results:
                        bar = '█' * int(r['avg_score'] / 5)
                        out += f"{r['field']:<25} {r['avg_score']:>6}%  {bar}\n"
                    if results:
                        best = results[0]
                        out += f"\n🎯 Best Field: {best['field']} ({best['avg_score']}%)\n"
                        if best['best_job']:
                            out += f"Best Job: {best['best_job']['company']} — {best['best_job']['title']}\n"
                        if best['top_missing']:
                            out += "\nTop skills to learn:\n"
                            for i, (s, c) in enumerate(best['top_missing'][:5], 1):
                                out += f"  {i}. {s} (missing in {c} jobs)\n"
                else:
                    result = self.ff.analyze_field(skills, selection)
                    out = "="*50 + f"\nFIELD: {selection.upper()}\n" + "="*50 + "\n\n"
                    if result:
                        s = result['avg_score']
                        ind = "🟢" if s >= 70 else "🟡" if s >= 40 else "🔴"
                        out += f"Avg Score: {s}% {ind}\n"
                        out += f"Jobs analyzed: {result['total_jobs']}\n"
                        if result['best_job']:
                            out += f"\nBest match: {result['best_job']['company']}\n"
                            out += f"Score: {result['best_job']['score']}%\n"
                        if result['top_missing']:
                            out += "\nTop missing skills:\n"
                            for i, (sk, c) in enumerate(result['top_missing'][:5], 1):
                                out += f"  {i}. {sk}\n"
                # hand everything back to the main thread (plotting included)
                self.root.after(0, lambda: self.on_field_done(out, results))
            except Exception as e:
                msg = str(e)  # capture now, 'e' is deleted after this block
                self.root.after(0, lambda: self.on_field_error(msg))

        threading.Thread(target=run, daemon=True).start()

    def on_field_done(self, out, results):
        self.display(out)
        if results:
            try:
                self.ch.plot_field_comparison(results)  # runs on main thread
            except Exception as e:
                messagebox.showerror("Chart error", str(e))
        self.status.set("Field analysis complete.")
        self.analyze_fields_btn.config(state="normal")

    def on_field_error(self, msg):
        messagebox.showerror("Error", msg)
        self.status.set("Field analysis failed.")
        self.analyze_fields_btn.config(state="normal")

    def view_progress(self):
        if not self.dm:
            messagebox.showwarning("Not loaded", "Please load student first.")
            return
        history = self.dm.get_history()
        if not history:
            self.display("No analyses yet. Analyze a job first.")
            return
        scores = [e.get('match_score', 0) for e in history]
        out = (
            f"{'='*50}\n"
            f"PROGRESS — {self.dm.student_name.title()}\n"
            f"{'='*50}\n"
            f"Total analyses:  {len(history)}\n"
            f"Average score:   {round(sum(scores)/len(scores), 2)}%\n"
            f"Highest score:   {max(scores)}%\n"
            f"Lowest score:    {min(scores)}%\n\n"
            f"Most Missing Skills:\n"
        )
        freq = {}
        for e in history:
            for s in e.get('missing', []):
                freq[s] = freq.get(s, 0) + 1
        for s, c in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:8]:
            out += f"  {s:<25} {c} times\n"
        self.display(out)
        self.ch.plot_score_progress(history)
        self.ch.plot_missing_skills(history)
        self.status.set("Progress charts saved to output/ folder.")

    def view_comparison(self):
        if not self.ev:
            messagebox.showwarning("Not loaded", "Please load student first.")
            return
        out = (
            f"{'='*50}\n"
            f"ALGORITHM COMPARISON\n"
            f"{'='*50}\n"
            f"{'Algorithm':<25} {'Acc':>6} {'Prec':>6} {'Rec':>6} {'F1':>6}\n"
            f"{'-'*55}\n"
        )
        for m in self.ev.metrics:
            name = m['algorithm'].replace('_', ' ').title()
            out += f"{name:<25} {m['accuracy']:>5}% {m['precision']:>5}% {m['recall']:>5}% {m['f1_score']:>5}%\n"
        best = self.ev.get_best_algorithm().replace('_', ' ').title()
        out += f"\nBest Algorithm: {best}"
        self.display(out)

    def save_charts(self):
        if not self.ev:
            messagebox.showwarning("Not loaded", "Please load student first.")
            return
        self.ch.plot_algorithm_comparison(self.ev.metrics)
        history = self.dm.get_history()
        if history:
            self.ch.plot_missing_skills(history)
            self.ch.plot_score_progress(history)
        self.status.set("Charts saved to output/ folder.")
        self.display("Charts saved to output/ folder.")

if __name__ == "__main__":
    root = tk.Tk()
    root.option_add("*Background", "#f5f5f5")
    root.option_add("*Foreground", "#212121")
    root.option_add("*Entry.Background", "#ffffff")
    root.option_add("*Entry.Foreground", "#212121")
    root.option_add("*Button.Background", "#455A64")
    root.option_add("*Button.Foreground", "#ffffff")
    app = App(root)
    root.mainloop()
