import pandas as pd

COMPAS_DATASET_FILEPATH = "task_data/compas-scores-two-years.csv"


def load_compas_data(use_race=False):
    df = pd.read_csv(COMPAS_DATASET_FILEPATH)

    keep_cols = [
        "sex",
        "age",
        "juv_fel_count",
        "juv_misd_count",
        "priors_count",
        "c_charge_degree",
        "two_year_recid",
        "c_charge_desc",
    ]

    one_hot_cols = ["sex", "c_charge_degree"]
    if use_race:
        keep_cols.append("race")
        one_hot_cols.append("race")

    df = df[keep_cols]
    one_hot_df = df.copy(deep=True)

    # for x in one_hot_cols:
    #     one_hot = pd.get_dummies(df[x], prefix=x)
    #     one_hot_df = one_hot_df.drop(x, axis=1)
    #     one_hot_df = one_hot_df.join(one_hot)

    one_hot_df["is_male"] = one_hot_df["sex"].map({"Female": 0, "Male": 1})
    one_hot_df["is_felony"] = one_hot_df["c_charge_degree"].map({"M": 0, "F": 1})
    one_hot_df.drop(columns=["sex", "c_charge_degree", "c_charge_desc"], inplace=True)
    return df, one_hot_df
