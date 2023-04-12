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
ec21=boto3.Session().resource('ec2',region_name = region)
instance_info = []

# Loop through each region and get all running EC2 instances
for region in regions:
    ec2_resource = boto3.resource('ec2', region_name=region)
    instances = ec2_resource.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        instance_id="Instance ID not found"
        state="State not found"
        private_ip_address="Private IP address not found"
        public_ip_address="Public IP address not found"
        instance_type="Instance type not found"
        name = 'Name not found in tags'
        owneremail = 'Owner email not found in tags'
        ibe = 'BE not found'
        ibu = 'BU not found'
        ami_name = 'AMI not found'
        ami_create_date = ''
        bu = 'AMI BU not found'
        release = 'AMI release info not available'
        release_ver = 0.0
        pod="POD not found"
        cpeval="0"
        qualyseval="0"
        applicationenv="Application Enviornment not found"

        #get info about the instance
        instance_id = instance['InstanceId']
        image_id=instance['ImageId']
        launch_time=instance['LaunchTime']
        state = instance['State']['Name']
        private_ip_address = instance.get('PrivateIpAddress', '')
        public_ip_address = instance.get('PublicIpAddress', '')
        instance_type = instance['InstanceType']

        #loop through the tags of instance
        for tags in instance['Tags']:
            if (tags['Key']).strip().upper() == 'NAME':
                name = tags['Value']
            if (tags['Key']).strip().upper() == 'OWNEREMAIL':
                owneremail = tags['Value']
            if (tags['Key']).strip().upper() == 'BUSINESSENTITY':
                ibe = tags['Value']
            if (tags['Key']).strip().upper() == 'BUSINESSUNIT':
                ibu = tags['Value']
            if (tags['Key']).strip().upper() == 'POD':
                pod=tags['Value']
            if (tags['Key']).strip().upper() == 'CPEVAL':
                cpeval=tags['Value']
            if (tags['Key']).strip().upper() == 'QUALYSEVAL':
                qualyseval=tags['Value']
            if (tags['Key']).strip().upper() == 'APPLICATIONENV':
                applicationenv=tags['Value']

        ami_date=''

        #get the ami details of the instance
        ami_details = ec21.images.filter(ImageIds=[instance['ImageId']])
        try:
            ami_name = list(ami_details)[0].name
            ami_create_date = list(ami_details)[0].creation_date

            ami_tags= list(ami_details)[0].tags

            for ami_tag1 in ami_tags:

                if (ami_tag1['Key']).strip().upper() == 'BUSINESSUNIT':
                    bu = ami_tag1['Value']

                if (ami_tag1['Key']).strip().upper() == 'RELEASE':
                    release = ami_tag1['Value']
                    release_ver = release[1:len(release)]

        except IndexError:
            ami_name = 'AMI not found'
            ami_create_date = ''
            ami_tags = 'AMI not found'
            bu = 'AMI BU not found'
            release = 'AMI release info not available'
            release_ver = 0.0
        except TypeError:
            release = 'AMI release info not available'
            release_ver = 0.0

        # we only need the creation date of the AMI so remove the time given
        if len(ami_create_date)!=0:
            ami_create_date_list=ami_create_date.split("T")
            print(ami_create_date_list)
            print(ami_create_date_list[0])
            ami_date=ami_create_date_list[0]

        #append all the information
        instance_info.append([instance_id,image_id,launch_time, state, region,private_ip_address,
        public_ip_address, instance_type, name, owneremail, ibe,ibu,
        ami_name,ami_date,bu,release,release_ver,pod,cpeval,qualyseval,applicationenv])
       

# Write the EC2 instances information to a CSV file
if not os.path.exists(output_path):
    os.makedirs(output_path)

with open(os.path.join(output_path, output_file), mode='w', newline='') as csv_file:
    fieldnames = ['Instance ID','AMI_ID','LAUNCHTIME', 'State', 'Region','Private IP Address', 'Public IP Address',
            'Instance Type', 'Name', 'OwnerEmail', 'BE', 'BU','AMI NAME','AMI CREATE DATE','AMIBU','RELEASE',
            'Version','POD','CPEVAL','QUALYSEVAL','APPENV']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for instance in instance_info:
        writer.writerow(instance)

print(f"EC2 instances information has been saved to {output_path}/{output_file}")

