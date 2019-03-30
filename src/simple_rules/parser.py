import string
from .consts import *


class BaseEntity(object):
    TYPE = ''
    VALUE = ''
    LEN = 0
    TERMINATORS = []

    def __init__(self, value=''):
        self.value = value

    def get_value(self):
        if self.TYPE == SYMBOL:
            return self.value
        else:
            return self.VALUE

    @classmethod
    def len(cls):
        return cls.LEN

    @classmethod
    def is_and(cls):
        return cls.TYPE == AND

    @classmethod
    def is_or(cls):
        return cls.TYPE == OR

    @classmethod
    def is_symbol(cls):
        return cls.TYPE == SYMBOL

    @classmethod
    def is_enter_group(cls):
        return cls.TYPE == ENTER_GROUP

    @classmethod
    def is_exit_group(cls):
        return cls.TYPE == EXIT_GROUP

    @classmethod
    def is_group(cls):
        return cls.is_enter_group() or cls.is_exit_group()

    @classmethod
    def build_object(cls, tokens):
        raise Exception("Operator must implement this")

    @classmethod
    def in_terminators(cls, v):
        if len(cls.TERMINATORS) == 0:
            return True
        return v in cls.TERMINATORS

    def __repr__(self):
        return "[{}::'{}']".format(self.TYPE, self.get_value())

    def __str__(self):
        return "{}".format(self.get_value())


class Space(BaseEntity):
    TYPE = SPACE
    VALUE = SPACE_VALUE
    LEN = len(SPACE_VALUE)
    TERMINATORS = []

    @classmethod
    def in_terminators(cls, v):
        return v not in string.whitespace

    @classmethod
    def can_parse(cls, tokens):
        if len(tokens) == 0:
            return False
        if not cls.in_terminators(tokens[0]):
            return True
        return False

    @classmethod
    def parse(cls, tokens):
        if cls.can_parse(tokens):
            while len(tokens) > 0:
                if cls.in_terminators(tokens[0]):
                    break
                tokens.pop(0)
            return Space()
        return None


class AndOp(BaseEntity):
    TYPE = AND
    VALUE = AND
    LEN = len(AND)
    TERMINATORS = AND_TERMINATORS

    def __init__(self):
        super(AndOp, self).__init__()

    @classmethod
    def can_parse(cls, tokens):
        if len(tokens) < cls.len()+2:
            return False
        if "".join(tokens[:cls.len()]) == cls.VALUE and cls.in_terminators(tokens[cls.len()]):
            return True
        return False

    @classmethod
    def parse(cls, tokens):
        if cls.can_parse(tokens):
            for _ in cls.VALUE:
                tokens.pop(0)
            return AndOp()
        return None


class OrOp(BaseEntity):
    TYPE = OR
    VALUE = OR
    LEN = len(OR)
    TERMINATORS = OR_TERMINATORS

    def __init__(self):
        super(OrOp, self).__init__()

    @classmethod
    def can_parse(cls, tokens):
        if len(tokens) < cls.len() + 2:
            return False
        if "".join(tokens[:cls.len()]) == cls.VALUE and cls.in_terminators(tokens[cls.len()]):
            return True
        return False

    @classmethod
    def parse(cls, tokens):
        if cls.can_parse(tokens):
            for _ in cls.VALUE:
                tokens.pop(0)
            return AndOp()
        return None

class EnterGroupOp(BaseEntity):
    TYPE = ENTER_GROUP
    VALUE = ENTER_GROUP_VALUE
    LEN = len(ENTER_GROUP_VALUE)
    TERMINATORS = []

    def __init__(self):
        super(EnterGroupOp, self).__init__()

    @classmethod
    def can_parse(cls, tokens):
        if len(tokens) < cls.len() + 2:
            return False
        if "".join(tokens[:cls.len()]) == cls.VALUE:
            return True
        return False

    @classmethod
    def parse(cls, tokens):
        if cls.can_parse(tokens):
            for _ in cls.VALUE:
                tokens.pop(0)
            return EnterGroupOp()
        return None


class ExitGroupOp(BaseEntity):
    TYPE = EXIT_GROUP
    VALUE = EXIT_GROUP_VALUE
    LEN = len(EXIT_GROUP_VALUE)
    TERMINATORS = []

    def __init__(self):
        super(ExitGroupOp, self).__init__()

    @classmethod
    def can_parse(cls, tokens):
        if "".join(tokens[:cls.len()]) == cls.VALUE:
            return True
        return False

    @classmethod
    def parse(cls, tokens):
        if cls.can_parse(tokens):
            for _ in cls.VALUE:
                tokens.pop(0)
            return ExitGroupOp()
        return None


class Symbol(BaseEntity):
    TYPE = SYMBOL
    VALUE = ''
    LEN = -1
    TERMINATORS = SYM_TERMINATORS

    def __init__(self, value):
        super(Symbol, self).__init__(value)

    @classmethod
    def can_parse(cls, tokens):
        if len(tokens) > 0 and not cls.in_terminators(tokens[0]):
            return True
        return False

    @classmethod
    def parse(cls, tokens):
        if cls.can_parse(tokens):
            value = []
            while len(tokens) > 0:
                if cls.in_terminators(tokens[0]):
                    break
                v = tokens.pop(0)
                value.append(v)
            return Symbol("".join(value))
        return None

class Parser(object):

    @classmethod
    def parse_string(cls, token_string):
        return cls.parse_tokens([i for i in token_string])

    @classmethod
    def parse_tokens(cls, tokens):
        parsed = []
        while len(tokens) > 0:
            v = None
            if Space.can_parse(tokens):
                v = Space.parse(tokens)
            elif EnterGroupOp.can_parse(tokens):
                v = EnterGroupOp.parse(tokens)
            elif ExitGroupOp.can_parse(tokens):
                v = ExitGroupOp.parse(tokens)
            elif AndOp.can_parse(tokens):
                v = AndOp.parse(tokens)
            elif OrOp.can_parse(tokens):
                v = OrOp.parse(tokens)
            elif Symbol.can_parse(tokens):
                v = Symbol.parse(tokens)
            parsed.append(v)
            if v is None:
                break
        return parsed
