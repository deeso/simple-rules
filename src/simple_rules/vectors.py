import jellyfish
from itertools import permutations
import numpy as np


class BaseVectorOp(object):
    @classmethod
    def build_substrings(cls, target: str, input: str, max_sz=None) -> list[str]:
        '''
        :param target: Y or target string we will compare against
        :param input: X input string we want to slide and compare the target too
        :param max_sz: Max size of the comparison window
        :return: list of substrings that create the window
        '''

        pos = 0
        max_sz = len(target) if max_sz is None else max_sz
        sub_strings = []
        while pos < len(input) - max_sz:
            sub_strings.append(input[pos:pos + max_sz])
            pos += 1
        return sub_strings

    @classmethod
    def build_vector(cls, string: str, letters: list = None) -> (list[str], np.array[int]):
        '''

        :param string: input string to build the counted vector for using letters, if not None
        :param letters: letters used to construct the sorted vector, otherwise letters are derived from string
        :return: frequency of letter occurrences for ML/stats
        '''
        letters = letters if letters is not None else sorted(set(string))
        vector = {k: 0 for k in letters}
        for l in string:
            vector[l] += 1
        return letters, np.array([vector[l] for l in letters])

    @classmethod
    def _calculate_levenshtein(cls, input: str, target: str) -> float:
        return jellyfish.levenshtein_distance(input, target)

    @classmethod
    def cosine_similarity_from_string(cls, input: str, target: str) -> float:
        letters = sorted(set(input) | set(target))
        target_vector = cls.build_vector(target, letters)
        input_vector = cls.build_vector(input, letters)
        return cls.cosine_similarity(input_vector, target_vector)

    @classmethod
    def cosine_similarity(cls, input: np.array(int), target: np.array(int)):
        dp = np.dot(input, target)
        nm = (np.linalg.norm(target)*np.linalg.norm(input))
        return dp/nm


class SimpleWordVector(BaseVectorOp):

    def __init__(self, input: str, target: str):
        super(BaseVectorOp, self).__init__()
        self.input = input
        self.target = target
        self.letters = sorted(set(input) | set(target))
        _, self.target_vector = self.build_vector(self.target, letters=self.letters)
        _, self.input_vector = self.build_vector(self.input, letters=self.letters)

    def calculate_levenshtein_substrings(self) -> list[float]:
        return [self._calculate_levenshtein(input, self.target) for input in self.substrings]

    def calculate_levenshtein(self) -> float:
        return self._calculate_levenshtein(self.input, self.target)

class OrderedWordVectors(SimpleWordVector):

    def __init__(self, input, target):
        '''
        :param input:  input string to compare the target too
        :param target: target string
        '''
        super(OrderedWordVectors, self).__init__(input, target)

        self.substrings = self.build_substrings(max_sz=len(self.target))
        self.substrings_count = np.array()
        substrings_count = []
        for substring in self.substrings:
            _, vec = self.build_vector(substring, self.letters)
            self.substrings_count = np.vstack([self.substrings_count, vec])


class FlippyWordsVectors(object):
    def __init__(self, targets: list):
        self.targets = targets
        self.input = input
        self.permuted_targets = self.build_target_permutations(targets)

    def get_orderd_word_vectors(self, input):
        return {k: OrderedWordVectors(k, input) for k in self.permuted_targets}

    @classmethod
    def build_target_permutations(cls, targets: list):
        r = []
        if len(targets) > 1:
            r = [t for t in targets]
        return r + ["".join(i) for i in permutations(targets)]

    @classmethod
    def build_substrings(cls, target: str, input: str, max_sz=None) -> list:
        '''
        :param target: Y or target string we will compare against
        :param input: X input string we want to slide and compare the target too
        :param max_sz: Max size of the comparison window
        :return: list of substrings that create the window
        '''

        pos = 0
        max_sz = len(target) if max_sz is None else max_sz
        sub_strings = []
        while pos < len(input) - max_sz:
            sub_strings.append(input[pos:pos + max_sz])
            pos += 1
        return sub_strings

    @classmethod
    def build_vector(cls, string: str, letters: list = None) -> dict:
        letters = letters if letters is not None else sorted(set(string))
        vector = {k: 0 for k in letters}
        for l in string:
            vector[l] += 1
        return vector
