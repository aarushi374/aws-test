import boto3
import csv
import os

# Specify the output file path and name
output_file = "ec2_instances.csv"
output_path = "/home/uthakkar"

# Create a Boto3 EC2 client
ec2_client = boto3.client('ec2')

# Get all AWS regions
regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

# Create a list to store the EC2 instances information
ec2_instances = []

# Loop through each region and get all running EC2 instances
for region in regions:
    ec2_resource = boto3.resource('ec2', region_name=region)
    instances = ec2_resource.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        ec2_instances.append({
            'InstanceID': instance.id,
            'Region': region,
            'InstanceType': instance.instance_type,
            'LaunchTime': str(instance.launch_time),
            #'CreationTime': str(instance.meta.data['CreationDate'])
        })

# Write the EC2 instances information to a CSV file
if not os.path.exists(output_path):
    os.makedirs(output_path)

with open(os.path.join(output_path, output_file), mode='w', newline='') as csv_file:
    fieldnames = ['InstanceID', 'Region', 'InstanceType', 'LaunchTime', 'CreationTime']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for instance in ec2_instances:
        writer.writerow(instance)

print(f"EC2 instances information has been saved to {output_path}/{output_file}")

