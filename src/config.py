import yaml
from pathlib import Path

DEFAULT_CONFIG = \
"""

"""

try:
    _CONFIG = yaml.safe_load(open(Path(__file__).parent / "config.yaml"))
except FileNotFoundError:
    _CONFIG = yaml.safe_load(DEFAULT_CONFIG)


class Config:
    def __init__(self, **entries):
        self.__dict__.update(entries)


CONFIG = Config(**_CONFIG)
