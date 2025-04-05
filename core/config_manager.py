import os
import pathlib
from dotenv import load_dotenv



SCRIPT_DIR = pathlib.Path(__file__).resolve().parent.parent


class _ConfigManager:
    """🔹 Singleton Configuration Manager with Auto-Generated Read-Only Properties & Boolean Conversion."""

    _instance = None  # Singleton instance
    
    _CONFIG_KEYS = {
        "LOG_LEVEL": "INFO",
        "ENABLE_FILE_LOGGING": "False",
        "LOG_FOLDER": "logs",
        "APP_NAME": "",
        "MCP_CONFIG_FILE_NAME": "",
        "MODEL_NAME": "mistral-nemo",
        "ENABLE_TREE_DISPLAY": "True"
    }
    
    
    _BOOLEAN_KEYS = {"ENABLE_FILE_LOGGING", "ENABLE_TREE_DISPLAY"}
        
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_ConfigManager, cls).__new__(cls)
            load_dotenv()  # Load environment variables

            # 🔹 Load values dynamically & convert booleans
            cls._instance._config = {
                key: cls._convert_value(key, os.getenv(key, default))
                for key, default in cls._CONFIG_KEYS.items()
            }

        # 🔹 Ensure log folder exists
        
        return cls._instance

    @staticmethod
    def _convert_value(key, value):
        """🔹 Automatically convert boolean-like values."""
        if key in _ConfigManager._BOOLEAN_KEYS:
            return value.lower() == "true" if isinstance(value, str) else bool(value)
        return value  # Return as-is for non-boolean keys

    def __getattr__(self, name):
        """🔹 Dynamically return config values as read-only properties with improved error handling."""
        if "_config" not in self.__dict__:
            raise AttributeError("❌ Configuration not initialized. Ensure ConfigManager is instantiated before use.")

        if name in self._config:
            return self._config[name]  # Read-only access

        available_keys = ", ".join(self._config.keys())
        raise AttributeError(f"❌ Configuration key '{name}' not found. Available keys: {available_keys}")


    def __setattr__(self, name, value):
        """🔹 Prevent modification of config values."""
        if "_config" in self.__dict__ and name in self._config:
            raise AttributeError(f"❌ Cannot modify read-only config key: {name}")
        super().__setattr__(name, value)

# ✅ Usage:
config_manager = _ConfigManager()
