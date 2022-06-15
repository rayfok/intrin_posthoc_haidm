### Commands

### Usage

1. Create credentials json file with valid `sandbox`, `accessKeyId`, and `secretAccessKey` fields.

   ```json
   {
       "sandbox": [boolean flag indicating whether to run on mturk sandbox or production],
       "accessKeyId": [AWS access key ID],
       "secretAccessKey": [AWS secret access key]
   }
   ```

2. Run

   ```
   python manage_hits.py <path to credentials file> <path to experiment config> <Optional: Number of HITs>
   ```

   to launch an interactive CLI to deploy and manage HITs.

3. Create a payment csv file.
4. Run

   ```
   python pay_workers.py -c <path to credentials file> -p <path to payment file> --last_hit_type_id <HIT type ID file>
   ```

   to approve, reject, pay, and bonus workers.

### Interactive MTurk CLI

Available commands

- list/ls
- exit
- deploy
- assignments [hitId | all]
- expire [HITId | "all"]
- delete [HITId | "all"]
- qualify ["worker" | "hit" | "type"] [entityId] [QUALIFICATION_ID] ([value = 1])

Unavailable commands

- list-bonus ["assignment" | "hit"] [*Id]
- bonus ["assignment" | "hit"] [*Id]
- approve ["assignment" | "hit" | "type" ] [*Id | ""]
- reject ["assignment" | "hit" | "type"] [*Id]
