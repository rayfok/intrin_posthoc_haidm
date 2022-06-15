import datetime
import json
import random
from xml.sax.saxutils import escape

import boto3

MTURK_SANDBOX = "https://mturk-requester-sandbox.us-east-1.amazonaws.com"
MTURK_PRODUCTION = "https://mturk-requester.us-east-1.amazonaws.com"

AUTO_APPROVE_DELAY = 5 * 24 * 3600
ASSIGNMENT_DUR = 4 * 3600

# Other consts
EXTERNAL_Q_SCHEMA = "http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd"
EXTERNAL_Q_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<ExternalQuestion xmlns="{}">
    <ExternalURL>{}</ExternalURL>
    <FrameHeight>{}</FrameHeight>
</ExternalQuestion>"""


class CustomHIT:
    def __init__(self, configFile=None):
        self.connection = None
        if not configFile is None:
            with open(configFile) as f:
                config = json.load(f)
                self.createConnection(
                    config["accessKeyId"], config["secretAccessKey"], config["sandbox"]
                )

    def isConnected(self):
        """
        Checks whether the current task is connected
        """
        return not self.connection is None

    def createConnection(self, accessKeyId, secretAccessKey, sandbox=False):
        """
        Creates a sandbox
        """
        print(
            "Connecting to MTurk {}".format("PRODUCTION" if not sandbox else "SANDBOX")
        )
        self.connection = boto3.client(
            "mturk",
            aws_access_key_id=accessKeyId,
            aws_secret_access_key=secretAccessKey,
            region_name="us-east-1",
            endpoint_url=MTURK_SANDBOX if sandbox else MTURK_PRODUCTION,
        )
        print(
            "Acct Balance: ${}".format(
                self.connection.get_account_balance()["AvailableBalance"]
            )
        )

    def registerHitType(self, config):
        """
        Register the HIT type to use in the experiment.
        """
        if self.connection is None:
            raise Exception("No MTurk connection established yet")
        # Some sanity check
        if (
            (not "title" in config)
            or (not "reward" in config)
            or (not "description" in config)
            or (not "keywords" in config)
        ):
            raise Exception("HIT Config missing critical information!")

        response = self.connection.create_hit_type(
            AssignmentDurationInSeconds=config["duration"]
            if "duration" in config
            else ASSIGNMENT_DUR,
            AutoApprovalDelayInSeconds=config["autoApproveDelay"]
            if "autoApproveDelay" in config
            else AUTO_APPROVE_DELAY,
            Reward="{}".format(config["reward"]),
            Title=config["title"],
            Keywords=",".join(config["keywords"]),
            Description=config["description"],
            QualificationRequirements=config["qualifications"]
            if "qualifications" in config
            else [],
        )
        return response["HITTypeId"]

    def createHit(self, config, hitTypeId=None, uniqueToken=None):
        # Create the external question object
        token = (
            "".join(
                random.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"))
                for _ in range(16)
            )
            if uniqueToken is None
            else uniqueToken
        )
        response = self.connection.create_hit_with_hit_type(
            HITTypeId=hitTypeId,
            MaxAssignments=config["maxAssignments"]
            if "maxAssignments" in config
            else 1,
            LifetimeInSeconds=config["lifeTime"] if "lifeTime" in config else 172800,
            Question=EXTERNAL_Q_TEMPLATE.format(
                EXTERNAL_Q_SCHEMA, escape(config["externalUrl"]), config["frameHeight"]
            ),
            UniqueRequestToken=token,
        )
        return token, response

    def listHits(self, next=None, hitTypeId=None):
        if not next is None:
            response = self.connection.list_hits(NextToken=next, MaxResults=100)
        else:
            response = self.connection.list_hits(MaxResults=100)

        if hitTypeId is None:
            return response.get("NextToken", None), response["HITs"]
        else:
            return (
                response.get("NextToken", None),
                [h for h in response["HITs"] if h["HITTypeId"] == hitTypeId],)

    def updateExpireTime(self, hitId, newExpireTime=None):
        self.connection.update_expiration_for_hit(
            HITId=hitId,
            ExpireAt=datetime.datetime(2008, 1, 1)
            if newExpireTime is None
            else newExpireTime,
        )

    def deleteHit(self, hitId):
        self.connection.delete_hit(HITId=hitId)

    def listAssignments(
        self, hitId, next=None, statusFilter=["Submitted", "Approved", "Rejected"]
    ):
        if not next is None:
            response = self.connection.list_assignments_for_hit(
                HITId=hitId,
                NextToken=next,
                MaxResults=100,
                AssignmentStatuses=statusFilter,
            )
        else:
            response = self.connection.list_assignments_for_hit(
                HITId=hitId, MaxResults=100, AssignmentStatuses=statusFilter
            )
        return response.get("NextToken", None), response["Assignments"]

    def listBonuses(self, id, next=None, group="assignment"):
        if group == "assignment":
            if next is None:
                resp = self.connection.list_bonus_payments(
                    AssignmentId=id, MaxResults=100
                )
            else:
                resp = self.connection.list_bonus_payments(
                    AssignmentId=id, NextToken=next, MaxResults=100
                )
        elif group == "hit":
            if next is None:
                resp = self.connection.list_bonus_payments(HITId=id, MaxResults=100)
            else:
                resp = self.connection.list_bonus_payments(
                    HITId=id, NextToken=next, MaxResults=100
                )
        return (
            (resp["NextToken"] if "NextToken" in resp else None),
            resp["BonusPayments"],
        )

    def approveAssignment(self, assignmentId, reason="", override=False):
        self.connection.approve_assignment(
            AssignmentId=assignmentId,
            RequesterFeedback=reason,
            OverrideRejection=override,
        )

    def rejectAssignment(self, assignmentId, reason=""):
        self.connection.reject_assignment(
            AssignmentId=assignmentId, RequesterFeedback=reason,
        )

    def qualifyWorker(self, workerId, qualificationId, value=1):
        self.connection.associate_qualification_with_worker(
            QualificationTypeId=qualificationId, WorkerId=workerId, IntegerValue=value
        )

    def bonus(self, assignmentId, workerId=None, reason="", amount="0.25"):
        # Try to get the worker id
        if workerId is None:
            asst = self.connection.get_assignment(AssignmentId=assignmentId)
            workerId = asst["Assignment"]["WorkerId"]
        self.connection.send_bonus(
            WorkerId=workerId,
            AssignmentId=assignmentId,
            Reason=reason,
            BonusAmount=amount,
        )


if __name__ == "__main__":
    import os.path
    import sys

    if len(sys.argv) < 3:
        print(
            "Usage: {} [credentials.json] [task-config.json] (count)".format(
                sys.argv[0]
            )
        )
        print("    credentials.json - Supplies MTurk Credentials/Sandbox config")
        print("    task-config.json - Supplies task-config")
        print("    count            - (Optional) How many HITs to create.")
        print("                       If unspecified, will drop into prompt")
        exit(1)

    task_config_dir = os.path.dirname(sys.argv[2])

    hit = CustomHIT(sys.argv[1])
    if not hit.isConnected():
        print("Something wrong with credentials provided. Error.")
        exit(2)

    # Load the task info
    taskInfo = None
    if not os.path.isfile(sys.argv[2]):
        print("Could not read task info file")
        exit(2)
    with open(sys.argv[2], "r") as f:
        taskInfo = json.load(f)

    # Try to load the local HIT id
    hitTypeId = None
    localconfig = os.path.join(task_config_dir, "LAST_HIT_TYPE_ID")
    if os.path.isfile(localconfig):
        print("Found existing HIT type registration.")
        with open(localconfig, "r") as f:
            hitTypeId = f.read().strip()
            print("Using HIT Type ID: {}".format(hitTypeId))
    else:
        c = input("No existing registration. Re-register HIT? (Y/n)")
        if c.lower() == "n":
            print("User cancelled script")
            exit(3)
        else:
            hitTypeId = hit.registerHitType(taskInfo)
            print("Registered HIT Type ID: {}".format(hitTypeId))
            with open(localconfig, "w") as f:
                f.write(hitTypeId)

    if hitTypeId is None:
        print("Could not get hit type id")
        exit(3)

    while True:
        command = input("> ").strip().split(" ")

        if command[0] == "":
            continue

        elif command[0] == "exit":
            exit(0)

        elif command[0] == "balance":
            print(
                "Acct Balance: ${}".format(
                    hit.connection.get_account_balance()["AvailableBalance"]
                )
            )

        elif command[0] == "create-qual":
            if len(command) < 2:
                print("create-qual [workerId]")
                continue
            hit.createQualification(command[1])

        elif command[0] == "deploy":
            if len(command) == 1:
                nonce, hitData = hit.createHit(config=taskInfo, hitTypeId=hitTypeId)
                print("HITId: {} ({})".format(hitData["HIT"]["HITId"], nonce))
                continue
            else:
                try:
                    for i in range(int(command[1])):
                        nonce, hitData = hit.createHit(
                            config=taskInfo, hitTypeId=hitTypeId
                        )
                        print(
                            "{:03d} -> HITId: {} ({})".format(
                                i, hitData["HIT"]["HITId"], nonce
                            )
                        )
                except Exception as e:
                    print(e)

        elif command[0] == "list" or command[0] == "ls":
            token = None
            while True:
                if len(command) >= 2:
                    next, hits = hit.listHits(
                        next=token,
                        hitTypeId=None if command[1] == "all" else command[1],
                    )
                else:
                    next, hits = hit.listHits(next=token, hitTypeId=hitTypeId)
                for h in hits:
                    print(
                        "Id: {} | TypeId: {} | Status: {} | ReviewStatus: {} | Avail: {} | Complete: {} | Pending: {}".format(
                            h["HITId"],
                            h["HITTypeId"],
                            h["HITStatus"],
                            h["HITReviewStatus"],
                            h["NumberOfAssignmentsAvailable"],
                            h["NumberOfAssignmentsCompleted"],
                            h["NumberOfAssignmentsPending"],
                        )
                    )
                if next is None:
                    break
                else:
                    token = next

        elif command[0] == "assignments":
            if len(command) < 2:
                print('assignments [HITId | "all"]')
                continue
            if command[1] == "all":
                token = None
                while True:
                    next, hits = hit.listHits(next=token, hitTypeId=hitTypeId)
                    for h in hits:
                        t = None
                        while True:
                            n, assts = hit.listAssignments(
                                hitId=h["HITId"], next=t, statusFilter=["Submitted"]
                            )
                            for a in assts:
                                print(
                                    "SubmitTime: {} | HitId: {} | AsstId: {} | WorkerId: {} | Status: {}".format(
                                        a["SubmitTime"],
                                        h["HITId"],
                                        a["AssignmentId"],
                                        a["WorkerId"],
                                        a["AssignmentStatus"],
                                    )
                                )
                            if n is None:
                                break
                            else:
                                t = n
                    if next is None:
                        break
                    else:
                        token = next
            else:
                token = None
                while True:
                    next, assignments = hit.listAssignments(
                        hitId=command[1], next=token
                    )
                    for h in assignments:
                        print(
                            "Id: {} | WorkerId: {} | Status: {}".format(
                                h["AssignmentId"], h["WorkerId"], h["AssignmentStatus"]
                            )
                        )
                    if next is None:
                        break
                    else:
                        token = next

        elif command[0] == "expire":
            if len(command) < 2:
                print('expire [HITId | "all"]')
                continue

            if command[1] != "all":
                try:
                    hit.updateExpireTime(command[1])
                    print("Set As Expired")
                except Exception as e:
                    print(e)
            else:
                token = None
                while True:
                    next, hits = hit.listHits(next=token, hitTypeId=hitTypeId)
                    for h in hits:
                        try:
                            hit.updateExpireTime(h["HITId"])
                            print("Set {} As Expired".format(h["HITId"]))
                        except Exception as e:
                            print(e)
                    if next is None:
                        break
                    else:
                        token = next

        elif command[0] == "delete" or command[0] == "rm" or command[0] == "del":
            if len(command) < 2:
                print('delete [HITId | "all"]')
                continue
            if command[1] != "all":
                try:
                    hit.deleteHit(command[1])
                    print("Deleted")
                except Exception as e:
                    print(e)
            else:
                token = None
                while True:
                    next, hits = hit.listHits(next=token, hitTypeId=hitTypeId)
                    for h in hits:
                        try:
                            hit.deleteHit(h["HITId"])
                            print("Deleted {}".format(h["HITId"]))
                        except Exception as e:
                            print(e)
                    if next is None:
                        break
                    else:
                        token = next

        elif command[0] == "qualify":
            if len(command) < 4:
                print(
                    'qualify ["worker" | "hit" | "type"] '
                    + "[entityId] [QUALIFICATION_ID] ([value = 1])"
                )
                continue
            value = int(command[4]) if len(command) > 4 else 1
            if command[1] == "worker":
                try:
                    hit.qualifyWorker(command[2], command[3], value)
                except Exception as e:
                    print(e)
                    continue
            elif command[1] == "hit":
                print("Qualifying all workers in HIT {}".format(command[2]))
                token = None
                while True:
                    next, assignments = hit.listAssignments(
                        hitId=command[2], next=token
                    )
                    for a in assignments:
                        try:
                            hit.qualifyWorker(a["WorkerId"], command[3], value)
                            print(
                                "Qualified worker {} (value={})".format(
                                    a["WorkerId"], value
                                )
                            )
                        except Exception as e:
                            print(e)
                    if next is None:
                        break
                    else:
                        token = next
            elif command[1] == "type":
                print("Not implemented")
            else:
                print("Unrecognized type {}".format(command[1]))
        else:
            print("Unknown command: {}".format(command[0]))
