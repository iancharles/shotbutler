# Shot Butler
A CLI tool for sharing AWS EBS snapshots between accounts with new KMS keys
---

## Prerequisites:
- Python 3 (I have tested this on Python 3.7. I can't vouch for earlier versions.)
- You will need a current version of boto3
- You will need to have a valid AWS_PROFILE configured
- You will need the following information available:
    - Desired region
    - AWS account number for current (origin) account
    - AWS account number for target account
    - KMS Key Id to use to encrypt new snapshots
    - Search filter (i.e. if snapshots must meet a certain description). This keys off the "Description" field for snapshots.

## Potential issues
If you are using an older version of Python 3 (3.5 or earlier), there may be some issues with format strings printing out information in a readable format.

## To-Do:
This is very much a work in progress. Goals include:
- Add option to generate new KMS key
- Add ability to delete original snapshots once they have been copied to a new shot
