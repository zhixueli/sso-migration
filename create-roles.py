import boto3
import botocore
import csv
import json

# 创建IAM客户端
iam_client = boto3.client('iam')

# 需要配置的参数 - AcountId
Account_Id = '066198483852'
# 需要配置的参数 - 角色信任策略
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::123456789012:saml-provider/xxxxxxxx"
            },
            "Action": "sts:AssumeRoleWithSAML",
            "Condition": {
                "StringEquals": {
                    "SAML:name": "someone@sample.com"
                }
            }
        }
    ]
}

with open(Account_Id + '.csv', mode ='r') as file:    
    csvFile = csv.DictReader(file)
    for row in csvFile:
        if row['PrincipalType'] == 'GROUP':
            role_name=row['UserOrGroupName']
            # 创建角色
            try:
                role = iam_client.create_role(
                    RoleName=role_name, 
                    AssumeRolePolicyDocument=json.dumps(trust_policy),
                    MaxSessionDuration=7200
                )
                print("Created role {}.".format(role_name))
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'EntityAlreadyExists':
                    print("Role {} already exists.".format(role_name))
                else:
                    print("Unexpected error when creating role: {}".format(e))
                    raise
            # attach managed policies
            if row['ManagedPoliciesArn'] != "":
                ManagedPoliciesArn =row['ManagedPoliciesArn'].split(",")
                for policyArn in ManagedPoliciesArn:
                    try:
                        response = iam_client.attach_role_policy(
                            RoleName=role_name,
                            PolicyArn=policyArn
                        )
                        print("Managed policy {} attached to role {}.".format(policyArn, role_name))
                    except botocore.exceptions.ClientError as e:
                        print("Unexpected error when attaching managed policy: {}".format(e))
                        raise
            # attach custom policies
            if row['CustomPoliciesArn'] != "":
                CustomPoliciesArn =row['CustomPoliciesArn'].split(",")
                for policyArn in CustomPoliciesArn:
                    try:
                        response = iam_client.attach_role_policy(
                            RoleName=role_name,
                            PolicyArn=policyArn
                        )
                        print("Custom policy {} attached to role {}.".format(policyArn, role_name))
                    except botocore.exceptions.ClientError as e:
                        print("Unexpected error when attaching custom policy: {}".format(e))
                        raise
            # attach inline policy
            if row['InlinePolicy'] != "":
                InlinePolicy =row['InlinePolicy']
                try:
                    response = iam_client.put_role_policy(
                        RoleName=role_name,
                        PolicyName=role_name+"_inline_policy",
                        PolicyDocument=InlinePolicy
                    )
                    print("Inline policy {} attached to role {}.".format(role_name+"_inline_policy", role_name))
                except botocore.exceptions.ClientError as e:
                    print("Unexpected error when attaching inline policy: {}".format(e))
                    raise
                    