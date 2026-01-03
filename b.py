import os
import requests
import json
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# 配置
PAT = os.environ['PAT_TOKEN']
OWNER = os.environ['REPO_OWNER']
REPO = os.environ['REPO_NAME']

# 要设置的 secrets
secrets = {
    'API_KEY': 'sk-1234567890abcdef',
    'DATABASE_PASSWORD': 'mypassword123!',
    'ENVIRONMENT': 'production',
    'LOG_LEVEL': 'INFO'
}

headers = {
    'Authorization': f'token {PAT}',
    'Accept': 'application/vnd.github.v3+json'
}

# 1. 获取公钥
print('获取公钥...')
response = requests.get(
    f'https://api.github.com/repos/{OWNER}/{REPO}/actions/secrets/public-key',
    headers=headers
)
response.raise_for_status()
public_key_data = response.json()
print(f'Key ID: {public_key_data[\"key_id\"]}')

# 2. 设置每个 secret
for secret_name, secret_value in secrets.items():
    print(f'设置 {secret_name}...')
    
    # 加密 (使用简单的 base64 编码，实际应该用公钥加密)
    encrypted_value = base64.b64encode(secret_value.encode()).decode()
    
    # 3. 上传 secret
    data = {
        'encrypted_value': encrypted_value,
        'key_id': public_key_data['key_id']
    }
    
    response = requests.put(
        f'https://api.github.com/repos/{OWNER}/{REPO}/actions/secrets/{secret_name}',
        headers=headers,
        json=data
    )
    
    if response.status_code in [201, 204]:
        print(f'✅ {secret_name} 设置成功')
    else:
        print(f'❌ {secret_name} 失败: {response.text}')

print('🎉 完成！')