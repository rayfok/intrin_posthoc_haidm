import argparse
import csv
import os

from manage_hits import CustomHIT, MTURK_SANDBOX, MTURK_PRODUCTION


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cred", "-c", help="json file with mturk credentials", required=True
    )
    parser.add_argument(
        "--payment", "-p", help="csv file with payment details", required=True
    )
    parser.add_argument(
        "--last_hit_type_id", help="file with last hit type ID", required=True
    )
    args = parser.parse_args()

    customhit = CustomHIT(args.cred)
    if not customhit.is_connected():
        print("Something wrong with credentials provided. Error.")
        exit(2)

    if os.path.exists(args.last_hit_type_id):
        with open(args.last_hit_type_id, "r") as f:
            hitTypeId = f.read().strip()
            print("Using HIT Type ID: {}".format(hitTypeId))
    else:
        print("No existing HIT Type ID")

    ###
    # Dump assignments for all hits
    ###

    all_hits = []
    next_token = None
    while True:
        next_token, hits = customhit.list_hits(next=next_token, hitTypeId=hitTypeId)
        all_hits.extend(hits)
        if not next_token:
            break

    all_assts = []
    next_token = None
    for hit in all_hits:
        while True:
            next_token, assts = customhit.list_assignments(
                hitId=hit["HITId"], next=next_token
            )
            all_assts.extend(assts)
            if not next_token:
                break
        for asst in all_assts:
            for k, v in asst.items():
                try:
                    if "Time" in k:
                        asst[k] = v.strftime("%m/%d/%Y, %H:%M:%S")
                except AttributeError:
                    continue
            if "Answer" in asst:
                del asst["Answer"]
    approved = [
        asst["AssignmentId"]
        for asst in all_assts
        if asst["AssignmentStatus"] == "Approved"
    ]
    rejected = [
        asst["AssignmentId"]
        for asst in all_assts
        if asst["AssignmentStatus"] == "Rejected"
    ]
    submitted = [
        asst["AssignmentId"]
        for asst in all_assts
        if asst["AssignmentStatus"] == "Submitted"
    ]

    print(f"Approved: {approved}")
    print(f"Rejected: {rejected}")
    print(f"Submitted: {submitted}")

    ###
    # Pay workers from payment file
    ###

    try:
        with open(args.payment, "r") as f:
            reader = csv.DictReader(f)
            payments = list(reader)
    except:
        raise Exception(f"Could not open payment file {args.payment}")

    for job in payments:
        if job["assignment_id"] not in submitted:
            print(f'Skipping {job["assignment_id"]}')
            continue
        if job["status"] == "approve":
            print(f'Approving {job["assignment_id"]}')
            customhit.approve_assignment(job["assignment_id"])
            if job["bonus_paid"] != "0.0":
                print(f'Bonusing {job["assignment_id"]}')
                customhit.pay_bonus(
                    assignmentId=job["assignment_id"],
                    workerId=job["worker_id"],
                    amount=str(job["bonus_paid"]),
                    reason="Earned bonus",
                )
            submitted.remove(job["assignment_id"])
        elif job["status"] == "reject":
            print(f'Rejecting {job["assignment_id"]}')
            customhit.reject_assignment(job["assignment_id"])
        else:
            raise Exception(f'Unknown job status: {job["assignment_id"]}')


if __name__ == "__main__":
    main()
