import json
import random
from pathlib import Path

import xgboost as xgb
from lime.lime_tabular import LimeTabularExplainer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from tqdm import tqdm

from utils import CompasDataset


def main():
    file_dir = Path(__file__).parent.resolve()
    root_dir = Path(__file__).parent.parent.resolve()

    compas = CompasDataset(f"{file_dir}/compas-scores-two-years.csv")
    feature_df = compas.feature_df
    df = compas.encoded_df
    labels = df[compas.target]
    features = df.drop(compas.target, axis=1)

    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.2, random_state=0, stratify=labels
    )
    print("Number of train examples:", len(y_train))
    print("Number of test examples:", len(y_test))
    print(f"Class distribution: 0: {sum(y_test == 0)}, 1: {sum(y_test == 1)}")

    feature_list = compas.numerical_features + compas.categorical_features

    n_examples = 250
    random.seed(0)
    indices = random.sample(range(0, len(X_test)), n_examples)
    output_df = (
        feature_df.iloc[X_test.index].reset_index().rename(columns={"index": "id"})
    )
    raw_output = output_df.iloc[indices].to_dict(orient="index")
    instances = {}

    # Intrinsically interpretable model (logistic regression)
    interpretable_model = LogisticRegression(
        class_weight="balanced", solver="lbfgs", max_iter=500, n_jobs=8
    )
    interpretable_model.fit(X_train.values, y_train)
    interpretable_preds = interpretable_model.predict(X_test.values)

    # Opaque model
    opaque_model = xgb.XGBClassifier(tree_method="gpu_hist", enable_categorical=True)
    opaque_model.fit(X_train.values, y_train)
    opaque_preds = opaque_model.predict(X_test.values)

    logr_coef = interpretable_model.coef_[0]
    logr_intercept = interpretable_model.intercept_[0]
    for i, ex in tqdm(raw_output.items()):
        i = int(i)
        sample = X_test.iloc[i].values
        label = int(y_test.iloc[i])

        # Feature contribution explanation for intrinsically interpretable model
        logr = {}
        logr_params = {}
        for ftr_i, feature in enumerate(feature_list):
            logr[feature] = sample[ftr_i] * logr_coef[ftr_i]
            logr_params[feature] = logr_coef[ftr_i]
        logr["intercept"] = logr_intercept
        logr_params["intercept"] = logr_intercept

        # LIME explanation for opaque model
        lime_explainer = LimeTabularExplainer(
            X_train.values,
            mode="classification",
            feature_names=feature_list,
            categorical_features=[
                feature_list.index(f) for f in compas.categorical_features
            ],
        )
        lime_rules = lime_explainer.explain_instance(
            sample, opaque_model.predict_proba, num_features=10,
        ).as_list()
        lime_ftr_contr = {}
        for rule, weight in lime_rules:
            for feature in feature_list:
                if feature in rule:
                    lime_ftr_contr[feature] = round(weight, 3)
                    break

        # Save data for instance
        instances[ex["id"]] = {
            "features": {feature: ex[feature] for feature in feature_df.columns},
            "label": label,
            "preds": {
                "intrinsic": int(interpretable_preds[i]),
                "opaque": int(opaque_preds[i]),
            },
            "expls": {
                "intrinsic_params": logr_params,
                "intrinsic": logr,
                "opaque": lime_ftr_contr,
            },
        }

    task_data_file = Path(root_dir, "output", "raw_task_data.json")
    if task_data_file.is_file():
        with open(task_data_file, "r") as f:
            task_data = json.load(f)
    else:
        task_data = {}
    task_data["compas"] = {"instances": instances}
    with open(task_data_file, "w") as out:
        json.dump(task_data, out, indent=2)


if __name__ == "__main__":
    main()
