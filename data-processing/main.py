import json
import random
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import pydotplus
import shap
import statsmodels.api as sm
import torch
from lime.lime_tabular import LimeTabularExplainer
from pygam import LogisticGAM
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier, export_graphviz, export_text
from statsmodels.formula.api import ols
from transformers import pipeline

from utils import *


def build_model(model_type: str):
    if model_type == "rf":
        model = RandomForestClassifier(n_estimators=100, random_state=0, max_depth=3)
    elif model_type == "lgr":
        model = LogisticRegression(solver="lbfgs", max_iter=500)
    elif model_type == "dt":
        model = DecisionTreeClassifier(
            criterion="entropy", max_depth=10, random_state=0
        )
    elif model_type == "svc":
        model = SVC(probability=True, gamma="auto")
    elif model_type == "gam":
        model = LogisticGAM()
    return model


def train(model, X_train, y_train):
    return model.fit(X_train, y_train)


def predict(model, X_test):
    return model.predict(X_test)


def evaluate(y_pred, y_test):
    return {"acc": accuracy_score(y_pred, y_test)}


def get_dt_local_expl(X_sample, dt, X_test, feature_list):
    node_indicator = dt.decision_path(X_sample)
    leaf_id = dt.apply(X_test)

    feature = dt.tree_.feature
    threshold = dt.tree_.threshold
    sample_id = 0
    # obtain ids of the nodes `sample_id` goes through, i.e., row `sample_id`
    node_index = node_indicator.indices[
        node_indicator.indptr[sample_id] : node_indicator.indptr[sample_id + 1]
    ]

    rules = []
    for node_id in node_index:
        # continue to the next node if it is a leaf node
        if leaf_id[sample_id] == node_id:
            continue

        # check if value of the split feature for sample 0 is below threshold
        if X_test[sample_id, feature[node_id]] <= threshold[node_id]:
            threshold_sign = "<="
        else:
            threshold_sign = ">"

        rules.append(
            f"[{feature_list[feature[node_id]]} = {X_test[sample_id, feature[node_id]]}] "
            f"{threshold_sign} {threshold[node_id]}"
        )
    return rules


def get_dt_tree_expl(X_sample, dt, feature_list):
    dot_data = export_graphviz(
        dt,
        out_file=None,
        feature_names=feature_list,
        class_names=["will not", "will"],
        filled=True,
        rounded=True,
        special_characters=True,
    )
    graph = pydotplus.graph_from_dot_data(dot_data)

    # empty all nodes, i.e.set color to white and number of samples to zero
    for node in graph.get_node_list():
        if node.get_attributes().get("label") is None:
            continue
        if "samples = " in node.get_attributes()["label"]:
            labels = node.get_attributes()["label"].split("<br/>")
            for i, label in enumerate(labels):
                if label.startswith("samples = "):
                    labels[i] = "samples = 0"
            node.set("label", "<br/>".join(labels))
            node.set_fillcolor("white")

    decision_paths = dt.decision_path(X_sample)

    for decision_path in decision_paths:
        for n, node_value in enumerate(decision_path.toarray()[0]):
            if node_value == 0:
                continue
            node = graph.get_node(str(n))[0]
            node.set_fillcolor("green")
            labels = node.get_attributes()["label"].split("<br/>")
            for i, label in enumerate(labels):
                if label.startswith("samples = "):
                    labels[i] = "samples = {}".format(int(label.split("=")[1]) + 1)

            node.set("label", "<br/>".join(labels))

    filename = "expl/dt_path_compas.png"
    graph.write_png(filename)


def get_gam_pdp(gam, feature_list):
    print(gam)
    plt.rcParams["figure.figsize"] = (28, 8)
    _, axs = plt.subplots(1, len(feature_list))
    for i, ax in enumerate(axs):
        XX = gam.generate_X_grid(term=i)
        pdep, confi = gam.partial_dependence(term=i, width=0.95)

        ax.plot(XX[:, i], pdep)
        ax.set_title(feature_list[i])
    plt.savefig("expl/gam_pdp_compas.png")


def beer_review():
    with open("task_data/beer_reviews.json", "r") as f:
        data = json.load(f)
    X, y = zip(*[(ex["X"], ex["Y"]) for ex in data])
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.1, random_state=0
    )

    y_pred = []
    classifier = pipeline(
        "sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest"
    )
    for i in range(len(X)):
        result = classifier(X[i])[0]
        y_pred.append(1 if result["label"] == "Positive" else 0)
        print(
            f"label: {result['label']}, with score: {round(result['score'], 4)}, Actual: {y[i]}"
        )
    acc = (np.array(y_pred) == np.array(y)).mean()
    print(acc)


def main():
    compas_df, compas_features_df = load_compas_data()

    # Make c_charge_degree values more readable in output
    compas_df.replace(
        {"c_charge_degree": {"M": "Misdemeanor", "F": "Felony"}}, inplace=True
    )

    labels = compas_features_df["two_year_recid"]
    features = compas_features_df.drop("two_year_recid", axis=1)
    feature_list = list(features.columns)

    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.2, random_state=0, stratify=labels
    )
    df_train = pd.concat([X_train, y_train], axis=1)
    df_test = pd.concat([X_test, y_test], axis=1)
    model_types = [
        "rf",
        "lgr",
        "dt",
        "svc",
        "gam",
    ]
    models = {}
    preds = {}
    metrics = {}

    for model_type in model_types:
        model = build_model(model_type)
        models[model_type] = train(model, X_train.values, y_train)
        preds[model_type] = predict(models[model_type], X_test.values)
        metrics[model_type] = evaluate(preds[model_type], y_test)

    # Statsmodels lgr has a different syntax
    logr_model = ols(
        "two_year_recid ~ C(sex) + C(c_charge_degree) + age + juv_fel_count + juv_misd_count + priors_count",
        data=df_train,
    ).fit()
    print(logr_model.summary())
    models["lgr-sm"] = logr_model
    model_pred = predict(logr_model, X_test)  # probabilities
    preds["lgr-sm"] = list(map(round, model_pred))
    metrics["lgr-sm"] = evaluate(preds["lgr-sm"], y_test)

    # Print accuracies of all models
    print(metrics)

    # Export global explanation for decision tree model
    tree_rules = export_text(models["dt"], feature_names=feature_list)
    with open("expl/dt_full_tree.txt", "w") as out:
        out.write(tree_rules)

    # Export final JSON with select examples, model predictions, and explanations
    dataset = "compas"
    output = {}
    n_examples = 50
    indices = random.sample(range(0, len(X_test)), n_examples)
    output_df = (
        compas_df.iloc[X_test.index].reset_index().rename(columns={"index": "id"})
    )
    raw_output = output_df.iloc[indices].to_dict(orient="index")
    output = defaultdict(list)

    # Global explanation for logistic regression model
    # score = permutation_importance(
    #     models["lgr"], X_train.values, y_train, n_repeats=30, random_state=0
    # )
    # ftr_importance = {feature_list[i]: v for i, v in enumerate(score.importances_mean)}

    bin_cat_ftrs = ["sex", "c_charge_degree"]
    for i, ex in raw_output.items():
        i = int(i)
        sample = X_test.iloc[i].values.reshape(1, -1)
        label = int(y_test.iloc[i])

        # Local exact explanation for logistic regression model
        # base_rate_ftrs = {
        #     "age": 30,
        #     "juv_fel_count": 0,
        #     "juv_misd_count": 0,
        #     "priors_count": 0,
        #     "sex": 0,
        #     "c_charge_degree": 0,
        # }
        lgr_ftr_contr = {}
        for ftr_i, feature in enumerate(feature_list):
            ### Interpretation as log-odds
            # lgr_ftr_contr[feature] = (
            #     sample[0][ftr_i] - base_rate_ftrs[feature]
            # ) * logr_model.params[feature]
            logr_feature = f"C({feature})[T.1]" if feature in bin_cat_ftrs else feature
            lgr_ftr_contr[feature] = sample[0][ftr_i] * logr_model.params[logr_feature]
        lgr_ftr_contr["intercept"] = logr_model.params["Intercept"]
        # base_rate = sum(
        #     base_rate_ftrs[feature] * logr_model.params[feature]
        #     for feature in feature_list
        # )

        # Local post-hoc explanation for SVC model
        lime_explainer = LimeTabularExplainer(
            X_train.values,
            mode="classification",
            feature_names=feature_list,
            categorical_features=[
                4,
                5,
            ],  # sex and c_charge_degree are 4th and 5th features
        )
        lime_rules = lime_explainer.explain_instance(
            sample.squeeze(),
            models["svc"].predict_proba,
            num_features=len(feature_list),
        ).as_list()
        lime_ftr_contr = {}
        for rule, weight in lime_rules:
            for feature in feature_list:
                if feature in rule:
                    lime_ftr_contr[feature] = round(weight, 3)
                    break

        output[dataset].append(
            {
                "id": ex["id"],
                "features": {
                    feature: ex[feature] for feature in list(compas_df.columns)
                },
                "label": label,
                "preds": {
                    model_type: int(preds[model_type][i]) for model_type in model_types + ["lgr-sm"]
                },
                "expls": {
                    "logr_ftr_cont": lgr_ftr_contr,
                    "svc_lime": lime_ftr_contr,
                },
            }
        )
    with open("output/task_data.json", "w") as out:
        json.dump(output, out, indent=2)


if __name__ == "__main__":
    main()
