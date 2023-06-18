import yaml
from pathlib import Path

DEFAULT_CONFIG = \
"""
minimal_password_length: 5
banned_passwords:
  - "12345"
  - "1234567890"
  - "qwerty"

minimal_username_length: 1
banned_usernames:
  -
"""

try:
    _CONFIG = yaml.safe_load(open(Path(__file__).parent / "config.yaml"))
except FileNotFoundError:
    _CONFIG = yaml.safe_load(DEFAULT_CONFIG)


class Config:
    def __init__(self, **entries):
        self.__dict__.update(entries)


CONFIG = Config(**_CONFIG)
