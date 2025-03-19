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

   # Checks to see if files were modified
   def on_modified(self, event):
      if not event.is_directory:
         relative_path = self._get_relative_path(event.src_path)
         if relative_path and not self._should_ignore(relative_path):
            self.modifications[relative_path] = "Modified"
   
   # Checks to see if new file/dir was created
   def on_created(self, event):
      relative_path = self._get_relative_path(event.src_path)
      if relative_path and not self._should_ignore(relative_path):
         self.modifications[relative_path] = "Created"

   # Checks to see if file/dir is deleted
   def on_deleted(self, event):
      relative_path = self._get_relative_path(event.src_path)
      if relative_path and not self._should_ignore(relative_path):
         self.modifications[relative_path] = "Deleted"
         
   def _get_relative_path(self, abs_path):
      """Convert absolute path to repository-relative path"""
      try:
         return os.path.relpath(abs_path, self.repo_root)
      except ValueError:
         return None
         
   def _should_ignore(self, path):
      """Check if a file should be ignored (like .git files)"""
      ignore_patterns = ['.git/', '__pycache__/', '.pyc', '.pyo', '.swp', '.#']
      return any(pattern in path for pattern in ignore_patterns)

   def get_commit_msg(self):
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        commit_msg = simpledialog.askstring("GitHub Commit", "Enter commit message:")
        root.destroy()
        return commit_msg if commit_msg else "Auto commit"

   def commit_and_push(self):
      if not self.modifications:
         print("No Changes in directory")
         return
      
      print(f"Changes detected: {self.modifications}")
         
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
            response = requests.get(url,headers=headers)
            if response.status_code == 200:
               file_sha = response.json()['sha']
            else:
               print(f"Error fetching file: {response.status_code}")
               print(response.json())
               exit()
            
            commit_message = self.get_commit_msg()
            payload = {
               'message': commit_message,
               'sha': file_sha
            }

            # Delete the file
            response = requests.delete(url, headers=headers,json=payload)
            if response.status_code == 200:
               print("File deleted successfully.")
            else:
               print(f"Error deleting file: {response.status_code}")
               print(response.json())


def main(): 
   dir_to_watch = "."
   # Setting up an observer
   observer = Observer()
   eventHandler = GitAutoCommit()

   observer.schedule(eventHandler, dir_to_watch, recursive=True)

   observer.start()

   try:
      # Keep running script until intrupted by "Ctrl + C"
      while True:
         pass
   except KeyboardInterrupt:
      eventHandler.commit_and_push()
      observer.stop()

   # Shuts down observer
   observer.join()

if __name__ == "__main__":
   main()