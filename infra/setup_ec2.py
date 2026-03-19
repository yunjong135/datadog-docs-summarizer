#!/usr/bin/env python3
"""EC2 인스턴스 생성 및 초기 설정 스크립트"""
import boto3
import time
import sys

REGION = "ap-northeast-2"
INSTANCE_TYPE = "t3.small"
AMI_ID = "ami-0c9c942bd7bf113a2"  # Amazon Linux 2023 (ap-northeast-2)
KEY_NAME = "datadog-summarizer-key"
SG_NAME = "datadog-summarizer-sg"
INSTANCE_NAME = "datadog-docs-summarizer"

ec2 = boto3.client("ec2", region_name=REGION)
ec2_resource = boto3.resource("ec2", region_name=REGION)


def create_key_pair():
    try:
        response = ec2.describe_key_pairs(KeyNames=[KEY_NAME])
        print(f"키페어 '{KEY_NAME}' 이미 존재합니다.")
        return False
    except ec2.exceptions.ClientError:
        pass

    print(f"키페어 '{KEY_NAME}' 생성 중...")
    response = ec2.create_key_pair(KeyName=KEY_NAME)
    with open(f"{KEY_NAME}.pem", "w") as f:
        f.write(response["KeyMaterial"])
    import os
    os.chmod(f"{KEY_NAME}.pem", 0o400)
    print(f"키페어 저장: {KEY_NAME}.pem")
    return True


def create_security_group():
    try:
        response = ec2.describe_security_groups(GroupNames=[SG_NAME])
        sg_id = response["SecurityGroups"][0]["GroupId"]
        print(f"보안그룹 '{SG_NAME}' 이미 존재합니다: {sg_id}")
        return sg_id
    except ec2.exceptions.ClientError:
        pass

    print(f"보안그룹 '{SG_NAME}' 생성 중...")
    response = ec2.create_security_group(
        GroupName=SG_NAME,
        Description="Security group for Datadog Docs Summarizer"
    )
    sg_id = response["GroupId"]

    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22,
             "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "SSH"}]},
            {"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80,
             "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "HTTP"}]},
            {"IpProtocol": "tcp", "FromPort": 8000, "ToPort": 8000,
             "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "FastAPI"}]},
        ]
    )
    print(f"보안그룹 생성 완료: {sg_id}")
    return sg_id


def get_user_data():
    return """#!/bin/bash
set -e
dnf update -y
dnf install -y python3 python3-pip git nginx

# Node.js 설치 (프론트엔드 빌드용)
curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
dnf install -y nodejs

# 앱 디렉토리 생성
mkdir -p /app
cd /app

# pip 패키지 설치 (앱 배포 시 requirements.txt 사용)
pip3 install fastapi uvicorn[standard] requests beautifulsoup4 anthropic python-dotenv lxml

# nginx 설정
cat > /etc/nginx/conf.d/datadog-summarizer.conf << 'NGINX_EOF'
server {
    listen 80;
    server_name _;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 60s;
    }

    location / {
        root /app/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
NGINX_EOF

# nginx 기본 설정 비활성화
rm -f /etc/nginx/conf.d/default.conf

systemctl enable nginx
systemctl start nginx

# systemd 서비스 생성 (백엔드용)
cat > /etc/systemd/system/datadog-summarizer.service << 'SERVICE_EOF'
[Unit]
Description=Datadog Docs Summarizer API
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/app/backend
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
EnvironmentFile=/app/backend/.env

[Install]
WantedBy=multi-user.target
SERVICE_EOF

systemctl daemon-reload
echo "EC2 초기화 완료!" > /var/log/app-init.log
"""


def launch_instance(sg_id):
    print("EC2 인스턴스 시작 중...")
    instances = ec2_resource.create_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        SecurityGroups=[SG_NAME],
        MinCount=1,
        MaxCount=1,
        UserData=get_user_data(),
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [
                {"Key": "Name", "Value": INSTANCE_NAME},
                {"Key": "Project", "Value": "datadog-docs-summarizer"}
            ]
        }],
        BlockDeviceMappings=[{
            "DeviceName": "/dev/xvda",
            "Ebs": {"VolumeSize": 20, "VolumeType": "gp3"}
        }]
    )
    instance = instances[0]
    print(f"인스턴스 생성됨: {instance.id}")
    print("인스턴스 실행 대기 중...")
    instance.wait_until_running()
    instance.reload()
    print(f"Public IP: {instance.public_ip_address}")
    print(f"Public DNS: {instance.public_dns_name}")
    return instance


def main():
    print("=" * 50)
    print("Datadog Docs Summarizer - EC2 셋업")
    print("=" * 50)

    create_key_pair()
    sg_id = create_security_group()
    instance = launch_instance(sg_id)

    print("\n" + "=" * 50)
    print("EC2 셋업 완료!")
    print(f"인스턴스 ID: {instance.id}")
    print(f"Public IP: {instance.public_ip_address}")
    print(f"\n접속 방법:")
    print(f"  ssh -i {KEY_NAME}.pem ec2-user@{instance.public_ip_address}")
    print(f"\n앱 배포:")
    print(f"  python3 deploy.py {instance.public_ip_address}")
    print("=" * 50)

    # 인스턴스 정보 저장
    with open("instance_info.txt", "w") as f:
        f.write(f"INSTANCE_ID={instance.id}\n")
        f.write(f"PUBLIC_IP={instance.public_ip_address}\n")
        f.write(f"PUBLIC_DNS={instance.public_dns_name}\n")
        f.write(f"KEY_FILE={KEY_NAME}.pem\n")


if __name__ == "__main__":
    main()
