# job_selector.py
# Handles job selection from jobs.csv

# ============================================
# CLASS — JobSelector
# ============================================
class JobSelector:

    def __init__(self, data_manager):
        self.jobs_df = data_manager.get_jobs()

    # ----------------------------------------
    # Get list of available fields
    # ----------------------------------------
    def get_fields(self):
        fields = self.jobs_df['field'].unique().tolist()
        fields = sorted([f for f in fields if f != 'Other'])
        fields.append('Other')
        return fields

    # ----------------------------------------
    # Get jobs by field
    # ----------------------------------------
    def get_jobs_by_field(self, field):
        filtered = self.jobs_df[
            self.jobs_df['field'] == field
        ].reset_index(drop=True)
        return filtered

    # ----------------------------------------
    # Show field selection menu
    # ----------------------------------------
    def select_field(self):
        fields = self.get_fields()

        print("\n" + "=" * 55)
        print("  SELECT JOB FIELD")
        print("=" * 55)
        print("\n  Available fields:\n")

        for i, field in enumerate(fields, 1):
            count = len(self.get_jobs_by_field(field))
            print(f"  {i:>2}. {field:<30} ({count} jobs)")

        print()
        while True:
            try:
                choice = int(input("  Enter field number: "))
                if 1 <= choice <= len(fields):
                    return fields[choice - 1]
                print(f"  [!] Enter number between 1 and {len(fields)}")
            except ValueError:
                print("  [!] Please enter a valid number.")

    # ----------------------------------------
    # Show job selection menu
    # ----------------------------------------
    def select_job(self, field):
        jobs = self.get_jobs_by_field(field)

        print("\n" + "=" * 75)
        print(f"  JOBS IN {field.upper()}")
        print("=" * 75)
        print(f"\n  {'#':<4} {'Company':<25} {'Level':<15} {'Title':<30}")
        print(f"  {'─'*4} {'─'*25} {'─'*15} {'─'*30}")

        for i, row in jobs.iterrows():
            company = row['company'][:23]
            title = row['title'][:28]
            level = row['level']

            if 'Entry' in level:
                level_short = 'Entry'
            elif 'Mid' in level:
                level_short = 'Mid-Senior'
            elif 'Intern' in level:
                level_short = 'Intern'
            elif 'Director' in level:
                level_short = 'Director'
            elif 'Executive' in level:
                level_short = 'Executive'
            elif 'Associate' in level:
                level_short = 'Associate'
            else:
                level_short = 'Open'

            print(f"  {i+1:<4} {company:<25} {level_short:<15} {title:<30}")

        print(f"  {'─'*75}")
        print()
        while True:
            try:
                choice = int(input("  Enter job number: "))
                if 1 <= choice <= len(jobs):
                    selected = jobs.iloc[choice - 1]
                    return selected
                print(f"  [!] Enter number between 1 and {len(jobs)}")
            except ValueError:
                print("  [!] Please enter a valid number.")
                
    # ----------------------------------------
    # Show selected job details
    # ----------------------------------------
    def show_job_details(self, job):
        print("\n" + "=" * 55)
        print("  SELECTED JOB")
        print("=" * 55)
        print(f"\n  Company:  {job['company']}")
        print(f"  Title:    {job['title']}")
        print(f"  Field:    {job['field']}")
        print(f"  Level:    {job['level']}")
        print(f"\n  Description preview:")
        print(f"  {job['description'][:200]}...")

    # ----------------------------------------
    # Full job selection flow
    # ----------------------------------------
    def choose_job(self):
        field = self.select_field()
        job = self.select_job(field)
        self.show_job_details(job)
        return job['description'], job['title'], job['company']