from GitHub_PushToken import PushingToken as PT
import base64
import requests
import json

# Headers for Authorization
def get_headers(token): 
   return {
         'Authorization': f'Bearer {token}',
         "Accept": "application/vnd.github+json",
         "X-GitHub-Api-Version": "2022-11-28"
      }

def get_repo_data(token):
   owner = "KrisshDiwedy38"
   repo = "GitHub-Management"
   url = f"https://api.github.com/repos/{owner}/{repo}/contents"

   headers = get_headers(token)

   response = requests.get( url , headers=headers)

   if response.status_code == 200:
      print(response.json())
   else:
      print(f"Error: {response.status_code}")

def get_last_commit(token):
   owner = "KrisshDiwedy38"
   repo = "GitHub-Management"
   url = f"https://api.github.com/repos/{owner}/{repo}/branches/main"
   headers = get_headers(token)
   response = requests.get(url, headers=headers)

   last_commit_sha = response.json()['commit']['sha']
   print(last_commit_sha)

def create_commit():
   with open(FILE_PATH, 'rb') as file:
      content = file.read()
   encoded_content = base64.b64encode(content).decode('utf-8')

   # Get the SHA of the file (if it exists)
   url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}'
   headers = {'Authorization': f'token {GITHUB_TOKEN}'}
   response = requests.get(url, headers=headers)

   if response.status_code == 200:
      sha = response.json()['sha']
   else:
      sha = None

   # Create the commit
   commit_data = {
      'message': COMMIT_MESSAGE,
      'content': encoded_content,
      'branch': BRANCH_NAME
   }
   if sha:
      commit_data['sha'] = sha

   response = requests.put(url, headers=headers, data=json.dumps(commit_data))

   if response.status_code in [200, 201]:
      print('File committed successfully.')
   else:
      print(f'Failed to commit file: {response.json()}')


def main():
   get_repo_data(PT)
   get_last_commit(PT)

if __name__ == "__main__":
   main()
