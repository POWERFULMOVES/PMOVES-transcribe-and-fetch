import json
import os
from typing import Dict
from .app_config import WORKSPACE_ROOT, SUBFOLDERS

class FolderManager:
    def __init__(self, config_file: str = 'folder_config.json'):
        self.config_file = config_file
        self.folders = self.load_config()

    # Load folder configuration from a JSON file
    def load_config(self) -> Dict[str, str]:
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        # Use centralized config for defaults
        return {
            'main': WORKSPACE_ROOT,
            'audio': os.path.join(WORKSPACE_ROOT, 'transcriptions', SUBFOLDERS['transcriptions']['audio']),
            'markdown': os.path.join(WORKSPACE_ROOT, 'transcriptions', SUBFOLDERS['transcriptions']['markdown']),
            'pdf': os.path.join(WORKSPACE_ROOT, 'transcriptions', SUBFOLDERS['transcriptions']['pdf']),
            'downloads': os.path.join(WORKSPACE_ROOT, 'downloads'),
            'fetches': os.path.join(WORKSPACE_ROOT, 'fetches'),
            'uploads': os.path.join(WORKSPACE_ROOT, 'uploads')
        }

    # Save the current folder configuration to the JSON file
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.folders, f, indent=2)

    # Get the current folder configuration
    def get_folders(self) -> Dict[str, str]:
        return self.folders

    # Update a folder path and move its contents
    def update_folder(self, key: str, new_path: str) -> bool:
        if key in self.folders:
            old_path = self.folders[key]
            if os.path.exists(old_path):
                os.makedirs(new_path, exist_ok=True)
                for item in os.listdir(old_path):
                    os.rename(os.path.join(old_path, item), os.path.join(new_path, item))
                os.rmdir(old_path)
            self.folders[key] = new_path
            self.save_config()
            return True
        return False

# Create a global instance of FolderManager
folder_manager = FolderManager()