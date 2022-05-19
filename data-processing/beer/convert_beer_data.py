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

NUM_EXAMPLES = 20
POSITIVE_CLASS_RATIO = 0.5


def convert_beer_data():
    root_dir = Path().resolve().parent

    instances = []
    with open("beer_logr_out.csv", "r") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        for row in reader:
            id, label, pred = int(row[0]), int(row[1]), int(row[2])
            token_weights = row[3:]
            token_weights = [tk for tk in token_weights if tk != ""]
            raw_tokens, weights = token_weights[::2], token_weights[1::2]
            assert len(raw_tokens) == len(weights)
            weights = [float(w) for w in weights]
            instances.append(
                {
                    "id": id,
                    "label": label,
                    "preds": {"logr": pred},
                    "expls": {"logr": {"tokens": raw_tokens, "weights": weights}},
                }
            )

    with open("beer_opaque_out.csv", "r") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        for i, row in enumerate(reader):
            id, label, pred, y_int = int(row[0]), int(row[1]), float(row[2]), float(row[3])
            token_weights = row[4:]
            token_weights = [tk for tk in token_weights if tk != ""]
            raw_tokens, weights = token_weights[::2], token_weights[1::2]
            assert len(raw_tokens) == len(weights)
            weights = [float(w) for w in weights]
            instances[i]["preds"]["opaque"] = pred
            instances[i]["expls"]["opaque"] = {"tokens": raw_tokens, "weights": weights}

    pos_instances = [x for x in instances if x["label"] == 1]
    neg_instances = [x for x in instances if x["label"] == 0]
    selected_instances = (
        pos_instances[: int(NUM_EXAMPLES * POSITIVE_CLASS_RATIO)]
        + neg_instances[: int(NUM_EXAMPLES * (1 - POSITIVE_CLASS_RATIO))]
    )

    task_data_file = Path(root_dir, "output", "task_data.json")
    if task_data_file.is_file():
        with open(task_data_file, "r") as f:
            task_data = json.load(f)
    else:
        task_data = {}
    task_data["beer"] = {"instances": selected_instances}
    with open(task_data_file, "w") as out:
        json.dump(task_data, out, indent=2)


if __name__ == "__main__":
    convert_beer_data()
