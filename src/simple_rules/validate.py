from .consts import *
from .parser import AndOp

class Predicate(object):
    TYPE = PREDICATE
    def __init__(self, num, parent=None):
        self.num = num
        self.parent = parent
        self.members = []

    def add_member(self, token):
        self.members.append(token)

    def get_members(self):
        return self.members

    def count(self):
        return len(self.members)

    def __str__(self):
        r = []
        for i in self.members:
            if i.TYPE == PREDICATE:
                r.append("({})".format(str(i)))
            else:
                r.append(str(i))
        return "{}".format(" ".join(r))

    def __repr__(self):
        r = []
        for i in self.members:
            if i.TYPE == PREDICATE:
                r.append("({})".format(repr(i)))
            else:
                r.append(repr(i))
        return "{}".format(" ".join(r))


class TokenStreamValidator(object):
    STATE_MACHINE = {
        SYMBOL: SYMBOL_NEXT,
        SPACE: SPACE_NEXT,
        OR: OR_NEXT,
        AND: AND_NEXT,
        ENTER_GROUP: ENTER_GROUP_NEXT,
        EXIT_GROUP: EXIT_GROUP_NEXT,
    }

    def __init__(self, token_stream, sym_maps={}):
        self.old_token_stream = token_stream
        self.pos = 0
        self.groups = {}
        self.group_stack = []

        self.last_group = 0
        self.current_group = Predicate(self.last_group, None)
        self.main_group = self.current_group
        self.group_stack.insert(0, self.current_group)
        self.groups[self.last_group] = self.main_group

        self.token_stream = [i for i in self.old_token_stream if i.TYPE != SPACE]

        self.sym_maps = sym_maps

    def enter_group(self):
        self.last_group += 1
        parent = self.current_group
        num = self.last_group
        new_group = Predicate(num, parent)
        if self.current_group is not None:
            self.current_group.add_member(new_group)

        self.group_stack.insert(0, self.current_group)
        self.current_group = new_group
        self.groups[num] = new_group

    def add_group_member(self, token):
        self.current_group.add_member(token)

    def exit_group(self):
        if len(self.group_stack) > 0:
            self.current_group = self.group_stack.pop(0)
        else:
            self.current_group = None

    def validate_without_symbols(self):
        pos = 0
        # Rewriting changes stream length, need to be dynamic
        # end = len(self.token_stream)

        while pos < len(self.token_stream)-1:
            t = self.token_stream[pos]
            n = self.token_stream[pos+1]
            next_state = self.STATE_MACHINE[t.TYPE]

            # Rewriting token stream, and injecting implicit AND
            if t.TYPE == SYMBOL and n.TYPE == ENTER_GROUP:
                self.token_stream.insert(pos+1, AndOp())
                n = self.token_stream[pos+1]


            if n.TYPE != SPACE and n.TYPE not in next_state:
                print ("Current: ", t, "Next: ",n)
                raise Exception("Failed validation for {}, expected: {}".format(t, next_state))

            pos += 1
            if t.TYPE == SPACE:
                continue
            elif t.TYPE == ENTER_GROUP:
                self.enter_group()
            elif t.TYPE == EXIT_GROUP:
                self.exit_group()
            else:
                self.add_group_member(t)

        # process last token
        t = self.token_stream[-1]
        pos += 1
        if t.TYPE == SPACE:
            pass
        elif t.TYPE == ENTER_GROUP:
            raise Exception("Unexpected grouping at the end of the stream")
        elif t.TYPE == EXIT_GROUP:
            self.exit_group()
        else:
            self.add_group_member(t)

        if len(self.group_stack) != 1:
            raise Exception("Unbalanced grouping for the rule")
        if self.main_group.count() == 0:
            raise Exception("Empty rule")
        return True

    def validate_with_symbols(self, sym_maps={}):
        sym_maps = sym_maps if len(sym_maps) else self.sym_maps
        failed = False
        failed_groups = {}
        for num, group in self.groups.items():
            failed_groups[num] = []
            for t in group.get_members():
                v = t.get_value()
                if t.TYPE == SYMBOL and v not in sym_maps:
                    failed_groups[num].append(v)
                    failed = True
        return failed, failed_groups
