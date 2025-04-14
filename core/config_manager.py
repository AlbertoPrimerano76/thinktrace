import os
import pathlib
from dotenv import load_dotenv

# Set the base directory two levels up from this file (usually the project root)
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent.parent

class _ConfigManager:
    """
    🔹 Singleton Configuration Manager

    Loads configuration values from environment variables, applying defaults when needed.
    Automatically converts boolean-like values and provides them as read-only properties.

    Usage:
        config = _ConfigManager()
        print(config.LOG_LEVEL)
    """

    _instance = None  # Singleton instance placeholder

    # 🔹 Default values for expected environment variables
    _CONFIG_KEYS = {
        "LOG_LEVEL": "INFO",
        "APP_NAME": "",
        "ENABLE_FILE_LOGGING" :"",
        "LOG_FOLDER_PATH": "logs",
        "CONFIG_FOLDER_PATH" : "",
        "PROMPT_FILE_NAME": "",
        "MCP_CONFIG_FILE_NAME" : ""
        
         }

    # 🔹 Keys to be interpreted as booleans
    _BOOLEAN_KEYS = {"ENABLE_FILE_LOGGING"}


    def __new__(cls):
        """Ensures only one instance is created (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(_ConfigManager, cls).__new__(cls)
            load_dotenv()  # Load .env file variables into environment

            # 🔹 Populate the internal config dict with loaded or default values
            cls._instance._config = {
                key: cls._convert_value(key, os.getenv(key, default))
                for key, default in cls._CONFIG_KEYS.items()
            }

            # 🔹 Ensure log directory exists if file logging is enabled
            if cls._instance._config["ENABLE_FILE_LOGGING"]:
                log_folder = os.path.join(SCRIPT_DIR, cls._instance._config["LOG_FOLDER_PATH"])
                try:
                    os.makedirs(log_folder, exist_ok=True)
                except Exception as e:
                    raise RuntimeError(f"❌ Failed to create log directory at '{log_folder}': {e}")

        return cls._instance

    @staticmethod
    def _convert_value(key, value):
        """
        🔹 Converts configuration values to the appropriate type.
        Booleans are recognized from strings (e.g., 'true', 'false').
        """
        if key in _ConfigManager._BOOLEAN_KEYS:
            return value.lower() == "true" if isinstance(value, str) else bool(value)
        return value  # Return as-is for non-boolean keys

    def __getattr__(self, name):
        """
        🔹 Provides read-only dynamic access to configuration values.
        Raises helpful errors if keys are not found.
        """
        if "_config" not in self.__dict__:
            raise AttributeError("❌ Configuration not initialized. Ensure ConfigManager is instantiated before use.")

        if name in self._config:
            return self._config[name]

        available_keys = ", ".join(self._config.keys())
        raise AttributeError(f"❌ Configuration key '{name}' not found. Available keys: {available_keys}")

    def __setattr__(self, name, value):
        """
        🔹 Prevents modification of configuration after initialization.
        Ensures immutability of config values.
        """
        if "_config" in self.__dict__ and name in self._config:
            raise AttributeError(f"❌ Cannot modify read-only config key: {name}")
        super().__setattr__(name, value)

# ✅ Initialize the singleton at module load (can be reused across imports)
config_manager = _ConfigManager()
