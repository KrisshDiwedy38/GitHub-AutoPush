import requests
from GitHub_PushToken import PushingToken

def get_headers(token): 
   return {
         'Authorization': f'Bearer {token}',
         "Accept": "application/vnd.github+json",
         "X-GitHub-Api-Version": "2022-11-28"
      }

def getData(token):
   username = "KrisshDiwedy38"
   repo_name = "GitHub-Management"
   url = f"https://api.github.com/repos/{username}/{repo_name}/contents"
   headers = get_headers(token)
   
   
   response = requests.get(url , headers=headers)

   if response.status_code == 200:
      data = response.json()
      print(data)
   else:
      print(f"Could not get data" , response.status_code)
   

def main(token):
   getData(token)

if __name__ == "__main__":
   main(PushingToken)