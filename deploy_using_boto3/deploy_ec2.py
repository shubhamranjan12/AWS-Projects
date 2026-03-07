import boto3


REGION = "ap-south-2"
AMI_ID = "ami-090b9c8aa1c84aefc"
INSTANCE_TYPE = "t3.micro"
KEY_NAME = "ec2_test"
SECURITY_GROUP_NAME = "demo-app-sg"

ec2 = boto3.client("ec2", region_name=REGION)

# create Security group
response = ec2.create_security_group(
    Description="Security group for project",
    GroupName=SECURITY_GROUP_NAME,
)

security_group_id = response["GroupId"]


ec2.authorize_security_group_ingress(
    GroupId=security_group_id,
    IpPermissions=[
        {
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        },
        {
            "IpProtocol": "tcp",
            "FromPort": 8080,
            "ToPort": 8080,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        },
    ],
)

print(f"Created Security Group: {security_group_id}")

# user data script to install flask & setup demo app
user_data_script = """#!/bin/bash
yum update -y
yum install python3-pip -y
pip3 install flask

cat <<EOF > app.py
import datetime
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    time = str(datetime.datetime.now())
    return f"Hello from EC2 automated deployment! - {time}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
EOF

python3 app.py &
"""

# Launch ec2 instance
instance = ec2.run_instances(
    ImageId=AMI_ID,
    InstanceType=INSTANCE_TYPE,
    KeyName=KEY_NAME,
    SecurityGroupIds=[security_group_id],
    MinCount=1,
    MaxCount=1,
    UserData=user_data_script,
)

instance_id = instance["Instances"][0]["InstanceId"]
print(f"Launching Instance: {instance_id}")


print("Waiting for instance to enter running state...")
waiter = ec2.get_waiter("instance_running")
waiter.wait(InstanceIds=[instance_id])


instance_description = ec2.describe_instances(InstanceIds=[instance_id])
public_ip = instance_description["Reservations"][0]["Instances"][0]["PublicIpAddress"]

print(f"\nInstance is running!")
print(f"The demo app is available at: http://{public_ip}:8080")

# Cleaning up
user_input = input("\nPress Enter to terminate the instance...")
print("Terminating instance...")
ec2.terminate_instances(InstanceIds=[instance_id])
waiter = ec2.get_waiter('instance_terminated')
waiter.wait(InstanceIds=[instance_id])

print("Instance terminated. Cleaning up security group...")

time.sleep(10)  # Waiting for few seconds to ensure the instance is terminated
ec2.delete_security_group(GroupId=security_group_id)
