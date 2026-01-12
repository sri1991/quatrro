import json
import logging
import os
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class TrainingService:
    def __init__(self, config_path: str = "training_config.json"):
        self.config_path = config_path
        self._configs: List[Dict[str, Any]] = []
        self.load_config()

    def load_config(self):
        """Loads the configuration from the JSON file."""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"Config file {self.config_path} not found. Starting with empty config.")
                self._configs = []
                return

            with open(self.config_path, 'r') as f:
                self._configs = json.load(f)
            logger.info(f"Loaded {len(self._configs)} training configurations from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            self._configs = []

    def get_all_configs(self) -> List[Dict[str, Any]]:
        """Returns all active document configurations."""
        return self._configs

    def get_config_by_type(self, doc_type: str) -> Optional[Dict[str, Any]]:
        """Returns a specific configuration by doc_type."""
        for config in self._configs:
            if config.get("doc_type") == doc_type:
                return config
        return None

    def refresh_config(self):
        """Triggers a reload of the configuration."""
        self.load_config()
