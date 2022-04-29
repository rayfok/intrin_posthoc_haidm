import json
import os
import random

import matplotlib.pyplot as plt
import numpy as np
from lime.lime_tabular import LimeTabularExplainer
from pygam import LogisticGAM
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from tqdm import tqdm

from utils import CompasDataset


def build_model(model_type: str, random_state: int = 0):
    if model_type == "rf":
        model = RandomForestClassifier(
            n_estimators=100, random_state=random_state, max_depth=3
        )
    elif model_type == "logr":
        model = LogisticRegression(solver="lbfgs", max_iter=500)
    elif model_type == "ridge":
        model = RidgeClassifier(random_state=random_state)
    elif model_type == "dt":
        model = DecisionTreeClassifier(
            criterion="entropy", max_depth=10, random_state=random_state
        )
    elif model_type == "svm":
        model = SVC(probability=True, gamma="auto")
    elif model_type == "gam":
        model = LogisticGAM()
    else:
        raise Exception("Unknown model type:", model_type)
    return model


def visualize_gam_pdp(gam, dataset, feature_list):
    gam_expl_dir = "expl/gam"
    os.makedirs(gam_expl_dir, exist_ok=True)
    for i, feature in enumerate(feature_list):
        XX = gam.generate_X_grid(term=i)
        pdep, confi = gam.partial_dependence(term=i, width=0.95)
        plt.plot(XX[:, i], pdep)
        plt.savefig(os.path.join(gam_expl_dir, f"{dataset}_{feature}.png"))
        plt.clf()


def main():
    compas = CompasDataset("task_data/compas-scores-two-years.csv")
    feature_df = compas.feature_df
    df = compas.encoded_df
    labels = df[compas.target]
    features = df.drop(compas.target, axis=1)

    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.2, random_state=0, stratify=labels
    )
    mean_df = X_train[compas.numerical_features].mean()

    models = {}
    preds = {}
    metrics = {}
    model_types = ["logr", "svm", "gam"]

    for model_type in model_types:
        model = build_model(model_type)
        models[model_type] = model.fit(X_train.values, y_train)
        preds[model_type] = model.predict(X_test.values)
        metrics[model_type] = accuracy_score(preds[model_type], y_test)

    for m, acc in metrics.items():
        print(f"{m}: {acc:.3f}")

    feature_list = compas.numerical_features + compas.categorical_features
    dataset = "compas"
    output = {dataset: {}}

    ### Global Explanations
    visualize_gam_pdp(models["gam"], dataset, feature_list)
    gam_pdp = {}
    for i, feature in enumerate(feature_list):
        XX = models["gam"].generate_X_grid(term=i)
        pdep, confi = models["gam"].partial_dependence(term=i, width=0.95)
        gam_pdp[feature] = list(zip(list(XX[:, i]), list(pdep)))
    output[dataset]["explanations"] = {}
    output[dataset]["explanations"]["gam_pdp"] = gam_pdp

    ### Local Explanations
    n_examples = 50
    random.seed(0)
    indices = random.sample(range(0, len(X_test)), n_examples)
    output_df = (
        feature_df.iloc[X_test.index].reset_index().rename(columns={"index": "id"})
    )
    raw_output = output_df.iloc[indices].to_dict(orient="index")
    output[dataset]["instances"] = []

    # Reference point for logistic regression log odds calculations
    logr_coef = models["logr"].coef_[0]
    logr_intercept = models["logr"].intercept_[0]
    reference = {
        "age": 28,
        "juv_fel_count": 1,
        "juv_misd_count": 1,
        "priors_count": 4,
    }
    ref_base_rate = 0
    for ftr_i, feature in enumerate(feature_list):
        if feature in compas.numerical_features:
            ref_base_rate += reference[feature] * logr_coef[ftr_i]
    ref_base_rate += logr_intercept
    print("Base rate:", ref_base_rate)  # Should be around 0

    for i, ex in tqdm(raw_output.items()):
        i = int(i)
        sample = X_test.iloc[i].values
        label = int(y_test.iloc[i])

        # Feature contribution explanation for logistic regression classifier
        logr_custom_ref = {}
        for ftr_i, feature in enumerate(feature_list):
            if feature in compas.categorical_features:
                logr_custom_ref[feature] = logr_coef[ftr_i]
                if sample[ftr_i] == 0:
                    logr_custom_ref[feature] *= -1
            else:
                logr_custom_ref[feature] = (
                    sample[ftr_i] - reference[feature]
                ) * logr_coef[ftr_i]
        logr_custom_ref["intercept"] = logr_intercept

        logr_mean_ref = {}
        for ftr_i, feature in enumerate(feature_list):
            if feature in compas.categorical_features:
                logr_mean_ref[feature] = logr_coef[ftr_i]
                if sample[ftr_i] == 0:
                    logr_mean_ref[feature] *= -1
            else:
                logr_mean_ref[feature] = (sample[ftr_i] - mean_df[feature]) * logr_coef[
                    ftr_i
                ]
        logr_mean_ref["intercept"] = logr_intercept

        logr_zero_ref = {}
        logr_params = {}
        for ftr_i, feature in enumerate(feature_list):
            logr_zero_ref[feature] = sample[ftr_i] * logr_coef[ftr_i]
            logr_params[feature] = logr_coef[ftr_i]
        logr_zero_ref["intercept"] = logr_intercept
        logr_params["intercept"] = logr_intercept

        logr_prob = {}
        for ftr_i, feature in enumerate(feature_list):
            if feature in compas.categorical_features:
                feature_log_odds = logr_coef[ftr_i]
                if sample[ftr_i] == 0:
                    feature_log_odds *= -1
            else:
                feature_log_odds = (sample[ftr_i] - mean_df[feature]) * logr_coef[ftr_i]
            feature_odds_ratio = np.exp(feature_log_odds)
            feature_prob = feature_odds_ratio / (1 + feature_odds_ratio)
            relative_feature_prob = feature_prob - 0.5
            logr_prob[feature] = relative_feature_prob

        # LIME explanation for SVM classifier
        lime_explainer = LimeTabularExplainer(
            X_train.values,
            mode="classification",
            feature_names=feature_list,
            categorical_features=[
                feature_list.index(f) for f in compas.categorical_features
            ],
        )
        lime_rules = lime_explainer.explain_instance(
            sample, models["svm"].predict_proba, num_features=10,
        ).as_list()
        lime_ftr_contr = {}
        for rule, weight in lime_rules:
            for feature in feature_list:
                if feature in rule:
                    lime_ftr_contr[feature] = round(weight, 3)
                    break

        output[dataset]["instances"].append(
            {
                "id": ex["id"],
                "features": {feature: ex[feature] for feature in feature_df.columns},
                "label": label,
                "preds": {
                    model_type: int(preds[model_type][i]) for model_type in model_types
                },
                "expls": {
                    "logr_params": logr_params,
                    "logr_custom_ref": logr_custom_ref,
                    "logr_mean_ref": logr_mean_ref,
                    "logr_zero_ref": logr_zero_ref,
                    "logr_prob": logr_prob,
                    "svc_lime": lime_ftr_contr,
                },
            }
        )
    with open("output/task_data.json", "w") as out:
        json.dump(output, out, indent=2)


if __name__ == "__main__":
    main()
