from .actions import ActionBaseClass

class RegexMatch(ActionBaseClass):
    def __init__(self, name, regex):
        super(RegexMatch, self).__init__()
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
