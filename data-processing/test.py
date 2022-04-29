import pandas as pd
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split

from main import build_model
from utils import LoanDataset, print_score


def main():
    loan = LoanDataset("task_data/accepted_100k.csv")

    default = loan.encoded_df[loan.encoded_df.loan_status == 1]
    paid = loan.encoded_df[loan.encoded_df.loan_status == 0]
    df = pd.concat([default, paid[:len(default)]])

    print("Number of instances", len(df))

    features, labels = df.drop("loan_status", axis=1), df.loan_status.astype("int")
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42, stratify=labels)

    model_types = ["logr", "xgboost", "gam"]
    models, preds, metrics = {}, {}, {}

    for model_type in model_types:
        model = build_model(model_type)
        models[model_type] = model.fit(X_train, y_train)
        preds[model_type] = model.predict(X_test)
        metrics[model_type] = f1_score(preds[model_type], y_test)

        print_score(y_train, model.predict(X_train), train=True)
        print_score(y_test, preds[model_type], train=False)


if __name__ == "__main__":
    main()
