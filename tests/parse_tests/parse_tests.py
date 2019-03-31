from unittest import TestCase
from simple_rules.consts import *
import logging
import sys


RULE_0 = '''adam OR pridgen'''

RULE_1 = '''adam OR pridgen ( why AND not)'''

RULE_2_FAIL = '''adam OR pridgen ( why AND not'''

RULE_3 = '''adam OR pridgen AND why AND not'''

RULE_3 = '''adam OR pridgen AND  ()   why AND not'''


class TestParsing(TestCase):

