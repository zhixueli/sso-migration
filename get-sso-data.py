import boto3
import csv

#需要配置的三个参数
IdentityCenterInstanceArn = 'arn:aws:sso:::instance/ssoins-xxxxxxxxxxxxx'
Account_Id = '123456789012'
IdentityStoreID = 'd-xxxxxxxxx'

# Custom Policy
IAMCustomPolicyPrefix="arn:aws:iam::{}:policy/".format(Account_Id)

# CSV 文件表头
new_data = [
    ['AccountId','UserOrGroupName','PrincipalType','PrincipalId','PermissSetName','ManagedPolicies','ManagedPoliciesArn','CustomPolicies','CustomPoliciesArn','InlinePolicy','PermissionSetArn']
]
csv_file_path =Account_Id + '.csv'
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    for row in new_data:
        writer.writerow(row)

# 创建SSOAdmin客户端
ssoadmin_client = boto3.client('sso-admin')

# 创建 IdentityStore 客户端
identitystore_client = boto3.client('identitystore')

# 列出所有Permission Set
response = ssoadmin_client.list_permission_sets_provisioned_to_account(AccountId=Account_Id,InstanceArn=IdentityCenterInstanceArn,MaxResults=100)
#print(response)
# 遍历每个Permission Set
for permission_set in response['PermissionSets']:
    permission_set_arn = permission_set
    #print(permission_set_arn)

    
    # 获取Permission Set的详细信息，包括名称
    permission_set_details = ssoadmin_client.describe_permission_set(
        InstanceArn=IdentityCenterInstanceArn,
        PermissionSetArn=permission_set_arn)
    permission_set_name = permission_set_details['PermissionSet']['Name']
    print ('****SetName****:',permission_set_name)
    # 获取与该Permission Set相关联的用户
    response_users = ssoadmin_client.list_account_assignments(
        InstanceArn=IdentityCenterInstanceArn,
        AccountId=Account_Id,
        PermissionSetArn=permission_set_arn)
    #print(response_users)

    # 输出与该Permission Set关联的用户，如果没有关联user或group 则跳过
    if  response_users['AccountAssignments']:
        for AccountAssignmentsRelation in response_users['AccountAssignments']:
            Permission_set_data = [[]]
            print('AccountId:', AccountAssignmentsRelation['AccountId'])
            Permission_set_data[0].append(AccountAssignmentsRelation['AccountId'])
            
            if 'GROUP' == AccountAssignmentsRelation['PrincipalType']:
                principal_id = AccountAssignmentsRelation['PrincipalId']
                responseGroup = identitystore_client.describe_group(IdentityStoreId=IdentityStoreID,GroupId=principal_id)
                print('GroupName:',responseGroup['DisplayName'])
                Permission_set_data[0].append(responseGroup['DisplayName'])
            elif 'USER' == AccountAssignmentsRelation['PrincipalType']:
                principal_id = AccountAssignmentsRelation['PrincipalId']
                responseUser = identitystore_client.describe_user(IdentityStoreId=IdentityStoreID, UserId=principal_id)
                Permission_set_data[0].append(responseUser['UserName'])
                print('UserName:', responseUser['UserName'])

            print('PrincipalType:', AccountAssignmentsRelation['PrincipalType'])
            Permission_set_data[0].append(AccountAssignmentsRelation['PrincipalType'])
            
            print('PrincipalId:', AccountAssignmentsRelation['PrincipalId'])  
            Permission_set_data[0].append(AccountAssignmentsRelation['PrincipalId'])
            
            print('PermissionSetName:',permission_set_name)
            Permission_set_data[0].append(permission_set_name)

            # 获取PermissionSet所配置的IAM Managed Policies
            managedPolicies=ssoadmin_client.list_managed_policies_in_permission_set(
                InstanceArn=IdentityCenterInstanceArn,
                PermissionSetArn=permission_set_arn)
            ManagedPolicyString=""
            ManagedPolicyArnString=""
            if managedPolicies['AttachedManagedPolicies']:
                ManagedPolicyData = []
                ManagedPolicyArnData = []
                for ManagedPolicy in managedPolicies['AttachedManagedPolicies']:
                    ManagedPolicyData.append(ManagedPolicy['Name'])
                    ManagedPolicyArnData.append(ManagedPolicy['Arn'])
                ManagedPolicyString=','.join(ManagedPolicyData)
                ManagedPolicyArnString=','.join(ManagedPolicyArnData)
            Permission_set_data[0].append(ManagedPolicyString)
            print('ManagedPolicies:',ManagedPolicyString)
            Permission_set_data[0].append(ManagedPolicyArnString)
            print('ManagedPoliciesArn:',ManagedPolicyArnString)

             # 获取PermissionSet所配置的IAM自定义Policies
            customPolicies=ssoadmin_client.list_customer_managed_policy_references_in_permission_set(
                InstanceArn=IdentityCenterInstanceArn,
                PermissionSetArn=permission_set_arn)
            CustomPolicyString=""
            CustomPolicyArnString=""
            if customPolicies['CustomerManagedPolicyReferences']:
                CustomPolicyData = []
                CustomPolicyArnData = []
                for CustomPolicy in customPolicies['CustomerManagedPolicyReferences']:
                    CustomPolicyData.append(CustomPolicy['Name'])
                    CustomPolicyArnData.append(IAMCustomPolicyPrefix+CustomPolicy['Name'])
                CustomPolicyString=','.join(CustomPolicyData)
                CustomPolicyArnString=','.join(CustomPolicyArnData)
            Permission_set_data[0].append(CustomPolicyString)
            print('CustomPolicies:',CustomPolicyString)
            Permission_set_data[0].append(CustomPolicyArnString)
            print('CustomPoliciesArn:',CustomPolicyArnString)

             # 获取PermissionSet所配置的Inline Policy
            inlinePolicy=ssoadmin_client.get_inline_policy_for_permission_set(
                InstanceArn=IdentityCenterInstanceArn,
                PermissionSetArn=permission_set_arn)
            InlinePolicyString=""
            if inlinePolicy['InlinePolicy']:
                InlinePolicyString=inlinePolicy['InlinePolicy']
            Permission_set_data[0].append(InlinePolicyString)
            
            print('PermissionSetArn:', AccountAssignmentsRelation['PermissionSetArn'])
            Permission_set_data[0].append(AccountAssignmentsRelation['PermissionSetArn'])

            print('**********************************************')
            #Permission_set_data = [[AccountAssignmentsRelation['AccountId'],
            #                        AccountAssignmentsRelation['PermissionSetArn'],
            #                        permission_set_name,AccountAssignmentsRelation['PrincipalType'],
            #                        AccountAssignmentsRelation['PrincipalId'],
            #                        responseGroup['DisplayName']]]
            with open(csv_file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                for row in Permission_set_data:
                    writer.writerow(row)
        # print('PrincipalType:',response_users['AccountAssignments'][0]['PrincipalType'])
            

