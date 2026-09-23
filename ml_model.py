# ml_model.py
# Responsible for training ML models and making predictions

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# ============================================
# CLASS — MLModel
# ============================================
class MLModel:

    def __init__(self, data_manager, algorithm="random_forest"):
        self.data_manager = data_manager
        self.algorithm = algorithm
        self.model = None
        self.X_test = None
        self.y_test = None
        self.y_pred = None
        self.is_trained = False
        self.train()

    # ----------------------------------------
    # Select algorithm based on name
    # ----------------------------------------
    def get_algorithm(self):
        if self.algorithm == "random_forest":
            return RandomForestClassifier(
                n_estimators=100,
                random_state=42
            )
        elif self.algorithm == "logistic_regression":
            return LogisticRegression(
                random_state=42,
                max_iter=1000
            )
        elif self.algorithm == "knn":
            return KNeighborsClassifier(n_neighbors=5)
        else:
            print("[!] Unknown algorithm. Using Random Forest.")
            return RandomForestClassifier(random_state=42)

    # ----------------------------------------
    # Train the model
    # ----------------------------------------
    def train(self):
        df = self.data_manager.get_training_data()

        if df.empty:
            print("[ERROR] No training data found.")
            return

        # features and label
        X = df[['match_score', 'matched_count',
                'missing_count', 'total_required']]
        y = df['label']

        # split data
        self.X_train, self.X_test, self.y_train, self.y_test = (
            train_test_split(X, y, test_size=0.2, random_state=42)
        )

        # get and train model
        self.model = self.get_algorithm()
        self.model.fit(self.X_train, self.y_train)

        # make predictions on test set
        self.y_pred = self.model.predict(self.X_test)
        self.is_trained = True

        print(f"[OK] {self.algorithm} model trained successfully")

    # ----------------------------------------
    # Predict fit level for new input
    # ----------------------------------------
    def predict(self, match_score, matched_count,
                missing_count, total_required):
        if not self.is_trained:
            return "Unknown", 0.0

        features = pd.DataFrame(
            [[float(match_score), int(matched_count),
              int(missing_count), int(total_required)]],
            columns=['match_score', 'matched_count',
                     'missing_count', 'total_required']
        )

        prediction = self.model.predict(features)[0]

        try:
            probabilities = self.model.predict_proba(features)[0]
            confidence = round(max(probabilities) * 100, 2)
        except Exception:
            confidence = 0.0

        return prediction, confidence

    # ----------------------------------------
    # Get evaluation metrics
    # ----------------------------------------
    def get_metrics(self):
        if not self.is_trained:
            return {}

        accuracy = accuracy_score(self.y_test, self.y_pred)
        precision = precision_score(
            self.y_test, self.y_pred,
            average='weighted', zero_division=0
        )
        recall = recall_score(
            self.y_test, self.y_pred,
            average='weighted', zero_division=0
        )
        f1 = f1_score(
            self.y_test, self.y_pred,
            average='weighted', zero_division=0
        )

        return {
            "algorithm": self.algorithm,
            "accuracy": round(accuracy * 100, 2),
            "precision": round(precision * 100, 2),
            "recall": round(recall * 100, 2),
            "f1_score": round(f1 * 100, 2)
        }

    # ----------------------------------------
    # Get confusion matrix
    # ----------------------------------------
    def get_confusion_matrix(self):
        if not self.is_trained:
            return None
        return confusion_matrix(
            self.y_test,
            self.y_pred,
            labels=["Good Fit", "Needs Work", "Not Ready"]
        )

    # ----------------------------------------
    # Get classification report
    # ----------------------------------------
    def get_classification_report(self):
        if not self.is_trained:
            return ""
        return classification_report(
            self.y_test,
            self.y_pred,
            zero_division=0
        )