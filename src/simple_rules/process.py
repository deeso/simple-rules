from .consts import *
from .validate import TokenStreamValidator
from .parser import Parser
import regex

class MatchClass(object):
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


class RegexMatch(MatchClass):
    def __init__(self, name, regex):
        super(MatchClass, self).__init__()
        self._name = name
        self.regex = regex.compile(regex)
        self.register_class(str, self.match_string)

    @property
    def name(self):
        return self._name

    def match_string(self, input_string):
        return self.regex.match(input_string)

    def match_default(self, obj):
        return self.regex.match(str(obj))


class Rule(object):

    def __init__(self, name, ast, main_predicate=0):
        self.predicates = ast
        self.name = name
        self.main_predicate = main_predicate

    def execute(self, input, state={}):
        return self.process_predicate(self.main_predicate, input, state=state)

    def process_predicate(self, group_key, input, last_result=None, state={}):
        rule_group = self.predicates[group_key]
        for node in rule_group:
            if node.TYPE == ACTION:
                last_result = node.execute(input, state)
            if node.TYPE == PREDICATE:
                last_result = self.process_predicate(node.num, input, state=state)
            elif node.TYPE == OR and last_result:
                return last_result
            elif node.TYPE == AND and not last_result:
                return last_result
        return last_result

    @classmethod
    def from_token_stream(cls, name, token_stream, sym_maps):
        validator = TokenStreamValidator(token_stream)
        ast = None
        if validator.validate_with_symbols(sym_maps):
            ast = cls.build_mapped_rule(validator, sym_maps)
        if ast is None:
            return None
        return cls(name, ast)

    @classmethod
    def from_token_string(cls, name, token_stream, sym_maps):
        token_stream = Parser.parse_string(token_stream)
        return cls.from_token_stream(name, token_stream, sym_maps)


    @classmethod
    def build_mapped_rule(cls, validator: TokenStreamValidator, sym_maps):
        default_match_node = None
        ast = {k: [] for k, in validator.groups.keys()}
        for node_name in ast:
            for node in validator.groups[node_name]:
                value = node.get_value()
                if node.TYPE == SYMBOL:
                    ast[node_name].append(sym_maps.get(value, default_match_node))
                else:
                    ast[node_name].append(node)
        return ast

    def __str__(self):
        return str(self.predicates[self.main_predicate])
