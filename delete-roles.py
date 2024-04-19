import boto3
import botocore
import csv
import json

# 创建IAM客户端
iam_client = boto3.client('iam')

# 需要配置的参数 - AcountId
Account_Id = '123456789012'

with open(Account_Id + '.csv', mode ='r') as file:   
    csvFile = csv.DictReader(file)
    for row in csvFile:
        if row['PrincipalType'] == 'GROUP':
            role_name=row['UserOrGroupName']

            # Detach policies from role first before deleting the role
            try:
                # Detach managed policies
                response = iam_client.list_attached_role_policies(
                    RoleName=role_name
                )
                for policy in response['AttachedPolicies']:
                    response = iam_client.detach_role_policy(
                        RoleName=role_name,
                        PolicyArn=policy["PolicyArn"]
                    )
                    print("Policy {} detached from role {}.".format(policy["PolicyArn"],role_name))
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchEntity':
                    print("Role {} doesn't exist or have been deleted.".format(role_name))
                else:
                    print("Unexpected error when detach policies from role: {}".format(e))

            try:
                # Detach inline policies
                response = iam_client.list_role_policies(
                    RoleName=role_name
                )
                for policy in response['PolicyNames']:
                    response = iam_client.delete_role_policy(
                        RoleName=role_name,
                        PolicyName=policy
                    )
                    print("Inline policy {} detached from role {}.".format(policy,role_name))
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchEntity':
                    print("Role {} doesn't exist or have been deleted.".format(role_name))
                else:
                    print("Unexpected error when detach inline policies from role: {}".format(e))

            # 删除角色
            try:
                role = iam_client.delete_role(
                    RoleName=role_name
                )
                print("Deleted role {}.".format(role_name))
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'NoSuchEntity':
                    print("Role {} doesn't exist or have been deleted.".format(role_name))
                else:
                    print("Unexpected error when deleting role: {}".format(e))
        