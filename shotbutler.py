import boto3
from time import sleep
import sys
import botocore

# Get setup information
print("Welcome to Shot Butler!")
profile_nm = input("Enter AWS Profile to use. This must be already extant. ")
region_nm = input("Enter region in format like 'us-east-1': ")
session = boto3.Session(profile_name=profile_nm, region_name=region_nm)
# Get account to transfer from. Your current profile should be accessing this one
orig_acct = input("What account are you transferring from? ")
# Get account to transfer to
new_acct = input("What account are you transferring to? ")
# Get the KMS key id for the new, shared key that can be accessed by both accts
new_kms_key = input("What is the KMS Key ID you'd like to use to encrypt? ")
# If you're filtering by customer number, this *should* limit to that customer's snapshots
search_filter = input("What value to you want to filter for? (ie customer #) ")

# Quickly validate AWS acct numbers by length
if len(orig_acct) != 12 or len(new_acct) != 12:
    print("Invalid value: AWS Account numbers are 12 digits.")
    sys.exit(1)

# Initiate the session
ec2 = session.client('ec2')

# Get initial batch of snapshots owned by current account
snapshots = ec2.describe_snapshots(
    Filters=[
        {
            'Name': 'owner-id',
            'Values': [
                orig_acct,
            ]
        },
    ]
)

customer_snapshots = []
# Create new snapshots
for snapshot in snapshots['Snapshots']:
    if search_filter in snapshot['Description']:
        print(f"Now copying - Snapshot ID: {snapshot['SnapshotId']}, Description: {snapshot['Description']}")
        try:
            ec2.copy_snapshot(
                Description="Copy - " + snapshot['SnapshotId'],
                Encrypted=True,
                KmsKeyId=new_kms_key,
                SourceRegion=region_nm,
                SourceSnapshotId=snapshot['SnapshotId'],
                TagSpecifications=[
                    {
                        'ResourceType': 'snapshot',
                        'Tags': [
                            {
                                'Key': 'shot_butler',
                                'Value': 'True'
                            },
                            {
                                'Key': 'search_filter',
                                'Value': search_filter
                            }
                        ]
                    },
                ]
            )
        except botocore.exceptions.ClientError as e:
            print(f"{e} happened.\n Waiting 5 seconds.\n Hit CTRL-C to cancel")
            sleep(5)


# Get snapshots, this time filtered to get the new ones for this search filter
snapshots_to_xfer = ec2.describe_snapshots(
    Filters=[
        {
            'Name': 'owner-id',
            'Values': [
                orig_acct,
            ]
        },
        {
            'Name': 'tag:shot_butler',
            'Values': ['True',]
        },
        {
            'Name': 'tag:search_filter',
            'Values': [search_filter,]
        }
    ]
)

print (snapshots_to_xfer)

for snapshot in snapshots_to_xfer['Snapshots']:
    print(f"Now sharing {snapshot['SnapshotId']} with {new_acct}")
    ec2.modify_snapshot_attribute(
        Attribute='createVolumePermission',
        OperationType='add',
        SnapshotId=snapshot['SnapshotId'],
        UserIds=[
            new_acct,
        ],
    )
