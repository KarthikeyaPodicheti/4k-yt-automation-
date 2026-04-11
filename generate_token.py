import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing token...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}")
                print("Will require re-authorization.")
                creds = None

        if not creds:
            if not os.path.exists('client_secret.json'):
                print("❌ ERROR: 'client_secret.json' not found!")
                print("Please download your OAuth 2.0 Client credentials from Google Cloud Console")
                print("Rename the file to 'client_secret.json' and place it in this folder.")
                return
                
            print("Starting authorization flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print("✅ token.pickle has been successfully created!")

    # Now encode to Base64 to make it easy for GitHub Actions
    with open('token.pickle', 'rb') as token:
        base64_bytes = base64.b64encode(token.read())
        base64_str = base64_bytes.decode('utf-8')
        
    with open('github_secret.txt', 'w') as f:
        f.write(base64_str)

    print("\n" + "="*50)
    print("Replace your GitHub Secret TOKEN_PICKLE_BASE64 with the following string:")
    print("(This string has also been saved to 'github_secret.txt' in this folder)")
    print("="*50 + "\n")
    print(base64_str)
    print("\n" + "="*50)

if __name__ == '__main__':
    main()
