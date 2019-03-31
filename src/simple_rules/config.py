import os
import toml
from .consts import *

class Config(object):
    CONFIG = {}

    @classmethod
    def from_json(cls, json_data):
        download_finder = json_data.get(SIMPLE_RULES_BLOCK, {})
        # parse ignore rules
        cls.CONFIG[IGNORE_REGEX_RULES] = {}
        for name, regex in download_finder.get(IGNORE_REGEX_RULES, {}).items():
            cls.CONFIG[IGNORE_REGEX_RULES][name] = regex

        # parse regex rule
        cls.CONFIG[REGEX_RULES] = {}
        for name, regex in download_finder.get(REGEX_RULES, {}).items():
            cls.CONFIG[REGEX_RULES][name] = regex

    @classmethod
    def parse_config(cls, config):
        try:
            os.stat(config)
            toml_data = toml.load(open(config))
            cls.from_json(toml_data)
        except:
            raise