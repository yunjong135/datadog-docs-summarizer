#!/usr/bin/env python3
"""EC2에 앱 배포 스크립트 (scp + ssh 사용)"""
import subprocess
import sys
import os
import time

KEY_FILE = "datadog-summarizer-key.pem"
USER = "ec2-user"
APP_DIR = "/app"

def run(cmd, check=True):
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=False)
    if check and result.returncode != 0:
        print(f"오류 발생: {cmd}")
        sys.exit(1)
    return result

def ssh(host, cmd, check=True):
    return run(f'ssh -i {KEY_FILE} -o StrictHostKeyChecking=no {USER}@{host} "{cmd}"', check=check)

def scp(host, src, dst):
    return run(f'scp -i {KEY_FILE} -o StrictHostKeyChecking=no -r {src} {USER}@{host}:{dst}')

def main():
    if len(sys.argv) < 2:
        # instance_info.txt에서 IP 읽기
        try:
            with open("instance_info.txt") as f:
                for line in f:
                    if line.startswith("PUBLIC_IP="):
                        host = line.strip().split("=")[1]
                        break
        except FileNotFoundError:
            print("사용법: python3 deploy.py <EC2_PUBLIC_IP>")
            sys.exit(1)
    else:
        host = sys.argv[1]

    print(f"배포 대상: {host}")

    # ANTHROPIC_API_KEY 확인
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        api_key = input("ANTHROPIC_API_KEY를 입력하세요: ").strip()

    print("\n1. EC2 초기화 완료 대기 중 (최대 2분)...")
    time.sleep(30)

    print("\n2. 백엔드 코드 업로드...")
    ssh(host, f"mkdir -p {APP_DIR}/backend {APP_DIR}/frontend")
    scp(host, "../backend/.", f"{APP_DIR}/backend/")

    print("\n3. 프론트엔드 빌드 및 업로드...")
    # 로컬에서 빌드 (node가 로컬에 있으면)
    local_build = subprocess.run("cd ../frontend && npm install && npm run build", shell=True)
    if local_build.returncode == 0:
        scp(host, "../frontend/dist", f"{APP_DIR}/frontend/dist")
    else:
        # EC2에서 빌드
        scp(host, "../frontend/.", f"{APP_DIR}/frontend/")
        ssh(host, f"cd {APP_DIR}/frontend && npm install && npm run build")

    print("\n4. 환경변수 설정...")
    ssh(host, f"echo 'ANTHROPIC_API_KEY={api_key}' > {APP_DIR}/backend/.env")

    print("\n5. 패키지 설치...")
    ssh(host, f"pip3 install -r {APP_DIR}/backend/requirements.txt -q")

    print("\n6. 서비스 시작...")
    ssh(host, "sudo systemctl restart datadog-summarizer || sudo systemctl start datadog-summarizer", check=False)
    ssh(host, "sudo systemctl restart nginx")

    print("\n7. 상태 확인...")
    time.sleep(3)
    ssh(host, "sudo systemctl status datadog-summarizer --no-pager -l", check=False)
    ssh(host, "sudo systemctl status nginx --no-pager", check=False)

    print(f"\n배포 완료!")
    print(f"웹사이트: http://{host}")
    print(f"API: http://{host}/api/search")

if __name__ == "__main__":
    main()
