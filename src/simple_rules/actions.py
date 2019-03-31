from .consts import *
import regex

class ActionBaseClass(object):
    TYPE = ACTION

    def __init__(self):
        self.match_mapping = {}

    def register_class(self, klass, transform):
        self.match_mapping[klass] = transform

    def execute(self, obj):
        return self.match(obj)

    def match(self, obj):
        typ = type(obj)
        if typ in self.match_mapping:
            return self.match_mapping[typ](obj)
        return self.match_default(obj)

    def match_default(self, obj):
        return False

