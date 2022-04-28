import pandas as pd

COMPAS_DATASET_FILEPATH = "task_data/compas-scores-two-years.csv"


def load_compas_data(use_race=False):
    df = pd.read_csv(COMPAS_DATASET_FILEPATH)

    keep_cols = [
        "age",
        "juv_fel_count",
        "juv_misd_count",
        "priors_count",
        "c_charge_degree",
        "sex",
        "two_year_recid",
        "c_charge_desc",
    ]

    df = df[keep_cols]
    df.dropna(subset=["c_charge_desc"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    one_hot_df = df.copy(deep=True)

    one_hot_df["sex"] = (
        one_hot_df["sex"].map({"Female": 0, "Male": 1}).astype("category")
    )
    one_hot_df["c_charge_degree"] = (
        one_hot_df["c_charge_degree"].map({"M": 0, "F": 1}).astype("category")
    )
    one_hot_df.drop(columns=["c_charge_desc"], inplace=True)
    return df, one_hot_df


class CompasDataset:
    def __init__(self, filepath):
        self.filepath = filepath
        self.target = "two_year_recid"
        self.numerical_features = [
            "juv_fel_count",
            "juv_misd_count",
            "priors_count",
            "age",
        ]
        self.categorical_features = ["sex", "c_charge_degree"]
        self.keep_other = ["c_charge_desc"]
        self.load_data()
        self.make_feature_df()

    def load_data(self):
        if self.filepath.endswith(".json"):
            self.df = pd.read_json(self.filepath)
        elif self.filepath.endswith(".csv"):
            self.df = pd.read_csv(self.filepath)
        else:
            raise Exception("Unsupported data format.")

    def make_feature_df(self, dropna=True):
        self.feature_df = self.df[
            self.numerical_features
            + self.categorical_features
            + self.keep_other
            + [self.target]
        ].copy(deep=True)
        self.feature_df.replace(
            {"c_charge_degree": {"M": "Misdemeanor", "F": "Felony"}}, inplace=True
        )
        for cf in self.categorical_features:
            self.feature_df[cf] = pd.Categorical(self.feature_df[cf])
        if dropna:
            self.feature_df.dropna(inplace=True)
            self.feature_df.reset_index(drop=True, inplace=True)

    def drop_and_encode_categorical(self):
        self.feature_df.drop(columns=["c_charge_desc"], inplace=True)
        self.feature_df["sex"] = (
            self.feature_df["sex"].map({"Female": 0, "Male": 1}).astype("category")
        )
        self.feature_df["c_charge_degree"] = (
            self.feature_df["c_charge_degree"]
            .map({"Misdemeanor": 0, "Felony": 1})
            .astype("category")
        )
