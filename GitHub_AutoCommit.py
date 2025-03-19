import os 
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import simpledialog, messagebox
from GitHub_PushToken import Token
import base64
import requests
import json

class GitAutoCommit(FileSystemEventHandler):
   def __init__(self):
      self.modifications = {}
      self.owner = "KrisshDiwedy38"
      self.repo = "GitHub-AutoPush"
      self.branch = "main"
      self.token = Token
      self.header = {
         'Authorization': f'Bearer {self.token}',
         "Accept": "application/vnd.github+json",
         "X-GitHub-Api-Version": "2022-11-28"
      }
      self.path = os.getcwd()

   # Checks to see if files were modified
   def on_modified(self, event):
      if not event.is_directory:
         self.modifications[os.path.abspath(event.src_path)] = "Modified"
   
   # Checks to see if new file/dir was created
   def on_created(self, event):
      self.modifications[os.path.abspath(event.src_path)] = "Created"

   # Checks to see if file/dir is deleted
   def on_deleted(self, event):
      self.modifications[os.path.abspath(event.src_path)] = "Deleted"

   def get_commit_msg(self):
      root = tk.Tk()
      commit_msg = simpledialog.askstring("GitHub Commit", 
                                             f"Enter commit message:")
      return commit_msg

   def commit_and_push(self):
      for i in self.modifications:
         # If a file was created or updated
         if self.modifications[i] in ["Created", "Modified"]:
            with open(i,"rb") as file:
               content = file.read()
            encoded_content = base64.b64encode(content).decode('utf-8')

            # Get the SHA of the file (if it exists)
            url = f'https://api.github.com/repos/{self.owner}/{self.repo}/contents/{i}'
            headers = self.header

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
               sha = response.json()['sha']
            else:
               sha = None

            commit_message = self.get_commit_msg()
            commit_package = {
               'message': commit_message,
               'content': encoded_content,
               'branch': self.branch
            }

            if sha:
               commit_package['sha'] = sha

            response = requests.put( url, headers=headers, data = json.dumps(commit_package))    

            if response.status_code in [200,201]:
               print('File committed successfully.')
            else:
               print(f'Failed to commit file: {response.json()}')

            
         # If file is Deleted 
         else:
            pass




def main(): 
   # Setting up an observer
   observer = Observer()
   eventHandler = GitAutoCommit()
   
   # Watch current directory
   dir_to_watch = "."
   
   observer.schedule(eventHandler, dir_to_watch, recursive=True)

   observer.start()

   try:
      # Keep running script until intrupted by "Ctrl + C"
      while True:
         pass
   except KeyboardInterrupt:
      print(eventHandler.modifications)
      observer.stop()

   # Shuts down observer
   observer.join()

if __name__ == "__main__":
   main()