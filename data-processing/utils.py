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

    df = df[keep_cols]
    df.dropna(subset=["c_charge_desc"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    one_hot_df = df.copy(deep=True)

    one_hot_df["sex"] = one_hot_df["sex"].map({"Female": 0, "Male": 1})
    one_hot_df["c_charge_degree"] = one_hot_df["c_charge_degree"].map({"M": 0, "F": 1})
    one_hot_df.drop(columns=["c_charge_desc"], inplace=True)
    return df, one_hot_df
