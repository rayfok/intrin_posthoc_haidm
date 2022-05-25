import json
import random


def main():
    # NUM_EXAMPLES = 25
    # POSITIVE_CLASS_RATIO = 0.5
    # pos_instances = [id for id, x in instances.items() if x["label"] == 1]
    # neg_instances = [id for id, x in instances.items() if x["label"] == 0]
    # selected_ids = (
    #     pos_instances[: int(NUM_EXAMPLES * POSITIVE_CLASS_RATIO)]
    #     + neg_instances[: int(NUM_EXAMPLES * (1 - POSITIVE_CLASS_RATIO))]
    # )
    # selected_instances = {id: instances[id] for id in selected_ids}

    NUM_TRAINING_EXAMPLES = 3
    NUM_EXAMPLES = 20
    NUM_CORRECT_BEER = 17
    NUM_CORRECT_COMPAS = 13

    with open("output/raw_task_data.json", "r") as f:
        task_data = json.load(f)
    for task, data in task_data.items():
        if task == "beer":
            num_correct = NUM_CORRECT_BEER
            num_incorrect = NUM_EXAMPLES - NUM_CORRECT_BEER
        elif task == "compas":
            num_correct = NUM_CORRECT_COMPAS
            num_incorrect = NUM_EXAMPLES - NUM_CORRECT_COMPAS
        else:
            print("Invalid task:", task)
            return

        instances = data["instances"]
        models_agree, models_disagree = [], []
        positive, negative = [], []
        for id, instance in instances.items():
            if instance["preds"]["intrinsic"] == instance["preds"]["opaque"]:
                models_agree.append(id)
            else:
                models_disagree.append(id)

            if instance["label"] == 0:
                negative.append(id)
            else:
                positive.append(id)

        intrinsic_acc = sum(
            instance["preds"]["intrinsic"] == instance["label"]
            for instance in instances.values()
        ) / len(instances)
        opaque_acc = sum(
            instance["preds"]["opaque"] == instance["label"]
            for instance in instances.values()
        ) / len(instances)

        print(f"Task: {task}")
        print(f"Intrinsic acc: {intrinsic_acc} | Opaque acc: {opaque_acc}")
        print(
            f"Agree: {len(models_agree)} | Disagree: {len(models_disagree)} | Total: {len(instances)}"
        )
        print(f"Positive: {len(positive)} | Negative: {len(negative)}")

        # Selection criteria:
        # 1. Intrinsic and opaque models agree.
        # 2. NUM_CORRECT_{TASK} of NUM_EXAMPLES are correct, and the rest incorrect.
        # 3. Half of the instances are positive, half are negative.
        models_correct = [
            id
            for id in models_agree
            if instances[id]["label"] == instances[id]["preds"]["intrinsic"]
        ]
        pos_agree = [id for id in positive if id in models_agree]
        neg_agree = [id for id in negative if id in models_agree]
        pos_agree_correct = [id for id in pos_agree if id in models_correct]
        neg_agree_correct = [id for id in neg_agree if id in models_correct]
        pos_agree_incorrect = [id for id in pos_agree if id not in models_correct]
        neg_agree_incorrect = [id for id in neg_agree if id not in models_correct]

        random.seed(0)
        selected = []
        selected += random.sample(pos_agree_correct, num_correct // 2)
        selected += random.sample(neg_agree_correct, num_correct - num_correct // 2)
        selected += random.sample(neg_agree_incorrect, num_incorrect // 2)
        selected += random.sample(
            pos_agree_incorrect, num_incorrect - num_incorrect // 2
        )
        assert len(selected) == NUM_EXAMPLES

        selected_training = []
        sectors = [
            pos_agree_correct,
            neg_agree_correct,
            pos_agree_incorrect,
            neg_agree_incorrect,
        ]

        for i in range(NUM_TRAINING_EXAMPLES):
            selected_training.append(
                random.choice(
                    [id for id in sectors[i % len(sectors)] if id not in selected]
                )
            )

        selected_instances = {id: instances[id] for id in selected}
        selected_training_instances = {id: instances[id] for id in selected_training}
        task_data[task]["instances"] = selected_instances
        task_data[task]["training_instances"] = selected_training_instances

        print("Selected IDs (train):", sorted([int(x) for x in selected_training]))
        print("Selected IDs (main):", sorted([int(x) for x in selected]))
        print()

    with open("output/task_data.json", "w") as f:
        json.dump(task_data, f, indent=2)


if __name__ == "__main__":
    main()
