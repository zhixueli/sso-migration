# AWS IAM Identity Center (SSO) 迁移到 IAM Identity Provider 集成 SSO 方案
## 代码文件功能解释
### get-sso-data.py
主要用于从 IAM Identity Center 读取用户组（Group），用户（User）以及其对应的权限集合（Permission Sets）所包含的 IAM 策略（Policies），并将其按照对应关系输出为 CSV 文件
### create-roles.py
根据从 IAM Identity Center 读取 CSV 文件作为输入，在 IAM 创建相应的角色（Roles）以及添加相应的权限策略（Policies）
### delete-roles.py
根据从 IAM Identity Center 读取 CSV 文件作为输入，用于清理其定义的角色和相应的权限
## 使用方法
1. 修改 get-sso-data.py 文件中的下列三个参数，其中 IdentityCenterInstanceArn 为需要迁移的 IAM Identity Center 实例的 ARN，Account_Id 为 AWS Organization 管理账号 ID，IdentityStoreID 为需要迁移的 IAM Identity Center 的 Identity Source 的 Identity Store ID
```
#需要配置的三个参数
IdentityCenterInstanceArn = 'arn:aws:sso:::instance/ssoins-xxxxxxxxxxxxx'
Account_Id = '123456789012'
IdentityStoreID = 'd-xxxxxxxxx'
```
![alt text](https://github.com/zhixueli/sso-migration/blob/main/screenshots/getssodata1.jpeg?raw=true)
![alt text](https://github.com/zhixueli/sso-migration/blob/main/screenshots/getssodata2.jpeg?raw=true)
2. 运行 get-sso-data.py，结果将会以 CSV 的格式保存在同目录下，文件名为第一步设置中的 Account_Id
3. 修改 create-roles.py 脚本中的下列参数，其中 Account_Id 为 AWS Organization 管理账号 ID，trust_policy 根据实际情况更改为 IAM Identity Provider 中配置的 Idp
```
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
```
3. 运行 create-roles.py，脚本将以第二部得到的 CSV 文件结果作为输入，在 IAM 创建相应的角色（Roles）以及添加相应的权限策略（Policies）。如果遇到问题，可以运行 delete-roles.py 来进行清理（注意需要修改文件中的Account_Id参数）。