import pandas as pd


class Dataset:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = self.load_data()
        self.feature_df = self.make_feature_df()
        self.encoded_df = self.drop_and_encode_categorical()

    def load_data(self):
        if self.filepath.endswith(".json"):
            df = pd.read_json(self.filepath)
        elif self.filepath.endswith(".csv"):
            df = pd.read_csv(self.filepath, low_memory=False)
        else:
            raise Exception("Unsupported data format.")
        return df

    def make_feature_df(self, dropna=True):
        features = self.numerical_features + self.categorical_features + self.keep_other
        target = [self.target] if self.target else []
        if not features and not target:
            return pd.DataFrame()
        feature_df = self.df[features + target].copy(deep=True)
        for cf in self.categorical_features:
            feature_df[cf] = pd.Categorical(feature_df[cf])
        if dropna:
            feature_df.dropna(inplace=True)
            feature_df.reset_index(drop=True, inplace=True)
        return feature_df

    def drop_and_encode_categorical(self, dropna=True):
        encoded_df = self.feature_df.copy(deep=True).drop(columns=self.keep_other)
        for feature, mapping in self.category_mapping.items():
            encoded_df[feature] = encoded_df[feature].map(mapping).astype("category")
        if dropna:
            encoded_df.dropna(inplace=True)
            encoded_df.reset_index(drop=True, inplace=True)
        return encoded_df


class CompasDataset(Dataset):
    def __init__(self, filepath):
        self.target = "two_year_recid"
        self.numerical_features = [
            "juv_fel_count",
            "juv_misd_count",
            "priors_count",
            "age",
        ]
        self.categorical_features = ["sex", "c_charge_degree"]
        self.keep_other = ["c_charge_desc"]
        self.category_mapping = {
            "sex": {"Female": 0, "Male": 1},
            "c_charge_degree": {"M": 0, "F": 1},
        }

        super().__init__(filepath)
        self.feature_df.replace(
            {"c_charge_degree": {"M": "Misdemeanor", "F": "Felony"}}, inplace=True
        )


class LoanDataset(Dataset):
    def __init__(self, filepath):
        self.filepath = filepath
        self.target = "loan_status"
        self.numerical_features = [
            "annual_inc",
            "loan_amnt",
            "installment",
            "int_rate",
            "fico_range_low",
        ]
        self.categorical_features = ["term"]
        self.keep_other = []
        self.category_mapping = {
            "term": {" 36 months": 36, " 60 months": 60},
            "loan_status": {"Fully Paid": 1, "Charged Off": 0},
        }
        super().__init__(filepath)
