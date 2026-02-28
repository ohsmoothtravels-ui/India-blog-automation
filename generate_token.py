"""
Run this script ONCE on your local computer to generate the Blogger OAuth token.
It will create a base64-encoded token you paste into GitHub Secrets.

Requirements:
  pip install google-auth google-auth-oauthlib google-api-python-client

Steps:
  1. Download your OAuth 2.0 credentials JSON from Google Cloud Console
     (APIs & Services → Credentials → OAuth 2.0 Client → Download JSON)
     Save it as client_secrets.json in the same folder as this script.
  2. Run:  python generate_token.py
  3. A browser window opens — log in with your Google account and allow access.
  4. Copy the printed BLOGGER_TOKEN_B64 value into GitHub Secrets.
"""

import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/blogger"]

def main():
    flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
    creds = flow.run_local_server(port=0)

    token_bytes = pickle.dumps(creds)
    token_b64 = base64.b64encode(token_bytes).decode("utf-8")

    print("\n" + "="*60)
    print("✅ SUCCESS! Copy this value into GitHub Secrets")
    print("   Secret name: BLOGGER_TOKEN_B64")
    print("="*60)
    print(token_b64)
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
