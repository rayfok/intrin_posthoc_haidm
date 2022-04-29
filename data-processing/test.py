from sklearn.model_selection import train_test_split

from sklearn.metrics import accuracy_score

from main import build_model
from utils import LoanDataset

loan = LoanDataset("task_data/accepted_100k.csv")

features, labels = loan.encoded_df.drop("loan_status", axis=1), loan.encoded_df.loan_status
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42, stratify=labels)

model_types = ["logr", "svm"]
models, preds, metrics = {}, {}, {}

for model_type in model_types:
    model = build_model(model_type)
    models[model_type] = model.fit(X_train, y_train)
    preds[model_type] = model.predict(X_test)
    metrics[model_type] = accuracy_score(preds[model_type], y_test)


print(metrics)
