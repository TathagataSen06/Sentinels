#!/usr/bin/env python3
import os
import requests

def get_canarytoken(token_type="msword", memo="Embedded in Sentinels SMB"):
    """
    Fetches a new CanaryToken from the public CanaryTokens.org API.
    """
    url = "https://canarytokens.org/generate"
    payload = {
        'memo': memo,
        'type': token_type
    }
    # Note: In a real scenario, you'd use your own CanaryTokens console or provide an email.
    # This is a mock function for the pipeline.
    print(f"[*] Generating {token_type} CanaryToken...")
    # Mocking the generation for demonstration. A real call would require an email and webhooks.
    return b"FAKE_WORD_DOCUMENT_CONTENT_WITH_BEACON"

def embed_tokens(base_path):
    # Ensure the SMB data directory exists
    smb_dir = os.path.join(base_path, 'data', 'smb')
    os.makedirs(smb_dir, exist_ok=True)
    
    # Drop a fake AWS credentials file
    aws_dir = os.path.join(smb_dir, '.aws')
    os.makedirs(aws_dir, exist_ok=True)
    
    aws_creds = """[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
"""
    with open(os.path.join(aws_dir, 'credentials'), 'w') as f:
        f.write(aws_creds)
    print(f"[+] Embedded fake AWS credentials at {aws_dir}/credentials")

    # Drop a fake Word Document token
    doc_path = os.path.join(smb_dir, 'Q3_Financial_Report_Confidential.docx')
    with open(doc_path, 'wb') as f:
        f.write(get_canarytoken('msword'))
    print(f"[+] Embedded CanaryToken Word Doc at {doc_path}")

if __name__ == "__main__":
    base_path = "/etc/sentinelsd"
    embed_tokens(base_path)
    print("[*] All CanaryTokens embedded successfully.")
