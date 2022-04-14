import json
import random
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import pydotplus
import shap
import statsmodels.api as sm
from lime.lime_tabular import LimeTabularExplainer
from pygam import LogisticGAM
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier, export_graphviz, export_text
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
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


def get_log_regr_global_expl(lgr, feature_list):
    # Calculate weights and odds of logistic regression model
    weights = lgr.coef_[0]
    odds = np.exp(weights)
    df = pd.DataFrame(
        list(zip(feature_list, weights, odds)), columns=["feature", "weight", "odds"]
    )
    # print(df.to_string())

    with plt.style.context("ggplot"):
        _ = plt.figure(figsize=(8, 6))
        plt.barh(
            range(len(lgr.coef_[0])),
            lgr.coef_[0],
            color=["red" if coef < 0 else "green" for coef in lgr.coef_[0]],
        )
        plt.yticks(range(len(lgr.coef_[0])), feature_list)
        plt.title("Weights")
        plt.savefig("expl/lgr_feature_compas.png")


def get_gam_pdp(gam, feature_list):
    print(gam)
    plt.rcParams["figure.figsize"] = (28, 8)
    _, axs = plt.subplots(1, len(feature_list))
    for i, ax in enumerate(axs):
        XX = gam.generate_X_grid(term=i)
        pdep, confi = gam.partial_dependence(term=i, width=0.95)

        ax.plot(XX[:, i], pdep)
        # ax.plot(XX[:, i], confi, c="r", ls="--")
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

    labels = compas_features_df["two_year_recid"]
    features = compas_features_df.drop("two_year_recid", axis=1)
    feature_list = list(features.columns)

    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.2, random_state=0, stratify=labels
    )

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
        model = train(model, X_train.values, y_train)
        models[model_type] = model
        model_pred = predict(model, X_test.values)
        preds[model_type] = model_pred
        model_metrics = evaluate(model_pred, y_test)
        metrics[model_type] = model_metrics

    # Statsmodels lgr has a different syntax
    sm_lgr_model = sm.Logit(y_train, X_train).fit()
    model_pred = predict(sm_lgr_model, X_test.values)  # probabilities
    model_pred = list(map(round, model_pred))
    preds["lgr-sm"] = model_pred
    model_metrics = evaluate(model_pred, y_test)
    metrics["lgr-sm"] = evaluate(model_pred, y_test)

    # Print accuracies of all models
    print(metrics)

    # Export global explanation for logistic regression model
    get_log_regr_global_expl(models["lgr"], feature_list)

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
    score = permutation_importance(
        models["lgr"], X_train.values, y_train, n_repeats=30, random_state=0
    )
    ftr_importance = {feature_list[i]: v for i, v in enumerate(score.importances_mean)}

    for i, ex in raw_output.items():
        i = int(i)
        sample = X_test.iloc[i].values.reshape(1, -1)
        label = int(y_test.iloc[i])

        # Local exact explanation for logistic regression model
        base_rate_ftrs = {
            "age": 30,
            "juv_fel_count": 0,
            "juv_misd_count": 0,
            "priors_count": 0,
            "is_male": 0,
            "is_felony": 0,
        }
        lgr_ftr_contr = {}
        for ftr_i, feature in enumerate(feature_list):
            odds = np.exp(sm_lgr_model.params[feature])
            base_rate_delta = sample[0][ftr_i] - base_rate_ftrs[feature]
            lgr_ftr_contr[feature] = odds ** base_rate_delta

        # Local post-hoc explanation for SVC model
        lime_explainer = LimeTabularExplainer(
            X_train.values,
            mode="classification",
            class_names=[0, 1],
            feature_names=feature_list,
        )
        lime_rules = lime_explainer.explain_instance(
            sample.squeeze(),
            models["svc"].predict_proba,
            num_features=len(feature_list),
        ).as_list()
        rule_cleanup_map = {
            "0.00 < is_felony <= 1.00": "is_felony = 1",
            "is_felony <= 0.00": "is_felony = 0",
        }

        output[dataset].append(
            {
                "id": ex["id"],
                "features": {
                    feature: ex[feature] for feature in list(compas_df.columns)
                },
                "label": label,
                "preds": {
                    model_type: int(preds[model_type][i]) for model_type in model_types
                },
                "expls": {
                    "logr_ftr_cont": lgr_ftr_contr,
                    "svc_lime": lime_rules,
                    # "logr_ftr_importance": ftr_importance,
                },
            }
        )
    with open("output/task_data.json", "w") as out:
        json.dump(output, out, indent=2)

    def test_on_sample():
        idx = random.randint(1, len(X_test))
        print(f"=== MODEL OUTPUTS ON TEST SAMPLE {idx} ===")
        X_sample = X_test.iloc[idx].values.reshape(1, -1)
        for i, feature in enumerate(feature_list):
            print(f"{feature} = {X_sample[0][i]}")

        print("Actual :     ", y_test.iloc[idx])

        # Print predictions for all models
        print("Decision Tree prediction: ", models["dt"].predict(X_sample))
        print("SVC Prediction: ", models["svc"].predict(X_sample))
        print("GAM Prediction: ", models["gam"].predict(X_sample))
        print("Random Forest Prediction: ", models["rf"].predict(X_sample))
        print("LogR Prediction: ", models["lgr"].predict(X_sample))

        # Local, exact explanation for decision tree model
        dt_local_expl = get_dt_local_expl(
            X_sample, models["dt"], X_test.values, feature_list
        )
        get_dt_tree_expl(X_sample, models["dt"], feature_list)

        # Local explanation for logistic regression model
        # print(sm_lgr_model.summary())
        base_rate_ftrs = {
            "age": 30,
            "juv_fel_count": 0,
            "juv_misd_count": 0,
            "priors_count": 0,
            "is_male": 0,
            "is_felony": 0,
        }
        lgr_ftr_contr = {}
        numerical_features = ["age", "juv_fel_count", "juv_misd_count", "priors_count"]
        binary_features = ["is_male", "is_felony"]
        for i, feature in enumerate(feature_list):
            odds = np.exp(sm_lgr_model.params[feature])
            base_rate_delta = X_sample[0][i] - base_rate_ftrs[feature]
            lgr_ftr_contr[feature] = odds ** base_rate_delta
        print("Logistic regression feature contributions:", lgr_ftr_contr)

        # LIME expl. for "black-box" model
        print("SVC Pred. Prob. : ", models["svc"].predict_proba(X_sample))
        lime_explainer = LimeTabularExplainer(
            X_train.values,
            mode="classification",
            class_names=[0, 1],
            feature_names=feature_list,
        )
        exp = lime_explainer.explain_instance(
            X_sample.squeeze(), models["svc"].predict_proba, num_features=5
        )
        for rule in exp.as_list():
            print(f"({rule[0]}, {rule[1]:.2f})")
        exp.save_to_file("expl/svc_lime_compas.html")

        # Partial dependence plots for GAM
        get_gam_pdp(models["gam"], feature_list)

    # test_on_sample()


if __name__ == "__main__":
    main()
