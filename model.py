import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib

# Load dataset
data = pd.read_csv("data.csv")

# Features
X = data[["Attendance", "InternalMarks", "AssignmentCompletion"]]

# Target
y = data["FinalResult"]

# Create model
model = LogisticRegression()

# Train model
model.fit(X, y)

# Save model
joblib.dump(model, "model.pkl")

print("Model trained successfully!")