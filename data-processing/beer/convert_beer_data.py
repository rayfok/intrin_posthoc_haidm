# Converts beer review and explanations from csv into json format
# Input format: id, label, pred, tok1, weight1, tok2, weight2, ...,
# Ouptut format:
# {
#   "beer": {
#     "instances": [{
#       "id": int,
#       "label": int,
#       "preds": { str: int },
#       "expls": { ... }
#     }, ...]
#   }
# }
import csv
import json
from pathlib import Path


def convert_beer_data():
    file_dir = Path(__file__).parent.resolve()
    root_dir = Path(__file__).parent.parent.resolve()

    instances = {}
    with open(Path(file_dir, "beer_logr_out.csv"), "r") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        for row in reader:
            id, label, pred = int(row[0]), int(row[1]), int(row[2])
            token_weights = row[3:]
            token_weights = [tk for tk in token_weights if tk != ""]
            raw_tokens, weights = token_weights[::2], token_weights[1::2]
            assert len(raw_tokens) == len(weights)
            weights = [float(w) for w in weights]
            instances[id] = {
                "label": label,
                "preds": {"intrinsic": int(pred)},
                "expls": {
                    "intrinsic": {
                        "tokens": raw_tokens,
                        "weights": weights,
                        "intercept": 0.8397366805904339,
                    }
                },
            }

    with open(Path(file_dir, "beer_opaque_out.csv"), "r") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        for i, row in enumerate(reader):
            id, label, pred, y_int = (
                int(row[0]),
                int(row[1]),
                float(row[2]),
                float(row[3]),
            )
            token_weights = row[4:]
            token_weights = [tk for tk in token_weights if tk != ""]
            raw_tokens, weights = token_weights[::2], token_weights[1::2]
            assert len(raw_tokens) == len(weights)
            weights = [float(w) for w in weights]
            instances[id]["preds"]["opaque"] = int(pred)
            instances[id]["expls"]["opaque"] = {
                "tokens": raw_tokens,
                "weights": weights,
                "intercept": y_int,
            }

    task_data_file = Path(root_dir, "output", "raw_task_data.json")
    if task_data_file.is_file():
        with open(task_data_file, "r") as f:
            task_data = json.load(f)
    else:
        task_data = {}
    task_data["beer"] = {"instances": instances}
    with open(task_data_file, "w") as out:
        json.dump(task_data, out, indent=2)


if __name__ == "__main__":
    convert_beer_data()
