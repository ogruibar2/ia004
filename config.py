import json
import os
from pathlib import Path

class Config:
    _instance = None
    _config_file = 'config.json'
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        default_config = {
            'theme': 'light',
            'window_size': '1000x700',
            'last_directory': '',
            'auto_backup': True,
            'max_recent_files': 5
        }
        
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r') as f:
                    self._config = {**default_config, **json.load(f)}
            except:
                self._config = default_config
        else:
            self._config = default_config
            self._save_config()
    
    def _save_config(self):
        with open(self._config_file, 'w') as f:
            json.dump(self._config, f, indent=4)
    
    def get(self, key):
        return self._config.get(key)
    
    def set(self, key, value):
        self._config[key] = value
        self._save_config()
