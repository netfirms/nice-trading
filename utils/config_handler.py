import yaml
import os
from dotenv import load_dotenv

load_dotenv()

def load_config(config_path: str = "config.yaml"):
    """Loads YAML configuration and merges with environment variables for secrets."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Add secrets from environment variables
    config['exchange']['api_key'] = os.getenv('BINANCE_API_KEY')
    config['exchange']['secret'] = os.getenv('BINANCE_SECRET')

    return config
