import jellyfish
from itertools import permutations
import numpy as np

from .contrib import levenshtein


class BaseVectorOp(object):

    @classmethod
    def build_substrings(cls, input: str, max_sz=4) -> list:
        '''
        :param target: Y or target string we will compare against
        :param input: X input string we want to slide and compare the target too
        :param max_sz: Max size of the comparison window
        :return: list of substrings that create the window
        '''

        pos = 0
        sub_strings = []
        while pos < len(input) - max_sz:
            sub_strings.append(input[pos:pos + max_sz])
            pos += 1
        return sub_strings

    @classmethod
    def build_vector(cls, string: str, letters: list = None) -> (list, np.ndarray):
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
    def build_vectors(cls, strings: list, letters: list) -> list:
        '''

        :param string: input string to build the counted vector for using letters, if not None
        :param letters: letters used to construct the sorted vector, otherwise letters are derived from string
        :return: frequency of letter occurrences for ML/stats
        '''
        result = []
        for string in strings:
            _, vec = cls.build_vector(string, letters)
            result.append(vec)
        return result

    @classmethod
    def calculate_levenshtein(cls, input: str, target: str) -> float:
        return jellyfish.levenshtein_distance(input, target)

    @classmethod
    def calculate_levenshtein_list_string(cls, inputs: list, target: str) -> list:
        return [cls.calculate_levenshtein(input, target) for input in inputs]

    @classmethod
    def cosine_similarity_from_string(cls, input: str, target: str) -> float:
        letters = sorted(set(input) | set(target))
        _, target_vector = cls.build_vector(target, letters)
        _, input_vector = cls.build_vector(input, letters)
        return cls.cosine_similarity(input_vector, target_vector)

    @classmethod
    def cosine_similarity(cls, input: np.ndarray, target: np.ndarray) -> float:
        dp = np.dot(input, target)
        nm = (np.linalg.norm(target)*np.linalg.norm(input))
        return dp/nm

    @classmethod
    def build_substring_vectors(cls, substrings: list, letters: list) -> np.ndarray:
        vecs = np.array()
        for substring in substrings:
            _, vec = cls.build_vector(substring, letters)
            vecs = np.vstack([vecs, vec])
        return vecs

    @classmethod
    def union(cls, strings:list=None) -> set:
        letters = set()
        for i in strings:
            letters |= set(i)
        return letters

    @classmethod
    def intersect(cls, strings:list=None) -> set:
        '''
        :param strings: list of input strings
        :return: interection of the letters from the list, note 1 item results in empty set,
        intersection with an "empty set" is an "empty set"
        '''
        string_sets = [set(i) for i in strings]
        letters = set()
        if len(string_sets) < 2:
            return letters

        # Empty Set Intersect any set is Empty Set
        letters = string_sets[0]
        for i in strings:
            letters &= set(i)
        return letters

    @classmethod
    def jaccard_distance(cls, input:str, target:str, other_inputs:str=None):
        if input is None and other_inputs is None:
            return 1.0
        v = [input] if input is not None else []
        v = v + other_inputs if other_inputs is not None else v

        total_area = cls.union(v)
        area_overlap = total_area & set(target)
        if len(total_area) == 0:
            return 0.0
        return len(area_overlap)/len(total_area)

    @classmethod
    def jaro_distance(cls, input: str, target:str) -> float:
        return jellyfish.jaro_distance(input, target)

    @classmethod
    def jaro_distances(cls, inputs: list, target:str) -> list:
        return [cls.jaro_distance(input, target) for input in inputs]

    @classmethod
    def jaro_winkler_distance(cls, input: str, target:str) -> float:
        return jellyfish.jaro_winkler(input, target)

    @classmethod
    def jaro_winkler_distances(cls, inputs: list, target:str) -> list:
        return [cls.jaro_winkler_distance(input, target) for input in inputs]

    @classmethod
    def damerau_levenshtein_distance(cls, input:str, target:str) -> float:
        return jellyfish.damerau_levenshtein_distance(input, target)

    @classmethod
    def damerau_levenshtein_distances(cls, inputs:list, target:str) -> list:
        return [cls.damerau_levenshtein_distance(input, target) for input in inputs]


    @classmethod
    def levenshtein_similarity(clscls, input:str, target:str)->float:
        distance = levenshtein(input, target)
        mlen = max(len(input), len(target))
        return 1 - float(distance / mlen)


class SimpleWordVector(BaseVectorOp):

    def __init__(self, input: str, target: str):
        super(BaseVectorOp, self).__init__()
        self.input = input
        self.target = target
        self.letters = sorted(set(input) | set(target))
        self.target_letters = sorted(set(target))
        _, self.target_vector = self.build_vector(self.target, letters=self.letters)
        _, self.input_vector = self.build_vector(self.input, letters=self.letters)
        self.substring = self.build_substrings(input, len(target))
        self.substring_vectors = self.build_substrings(input, len(target))

    def get_result(self, input, target, input_vector, target_vector, fn):
        return {'input': input, 'target': target, 'result': fn(input_vector, target_vector)}

    def get_all_results(self, name="cosine"):
        fn = getattr(self, name, None)
        return self.create_result(fn)

    def create_result(self, fn):
        results = []
        results.append(self.get_result(self.input, self.target, self.input_vector, self.target_vector, fn))
        for ss_value, ss_vector in zip(self.substring, self.substring_vectors):
            results.append(self.get_result(ss_value, self.target, ss_vector, self.target_vector, fn))
        return results

    def cosine(self):
        return self.get_all_results(name="cosine_similarity")

    def damerau_levenshtein(self):
        results = []
        get_result = lambda i, t: {'input': i, 'target':t, 'result': self.damerau_levenshtein_distance(i, t)}
        results.append(get_result(self.input, self.target))
        for ss_value, ss_vector in zip(self.substring, self.substring_vectors):
            results.append(get_result(ss_value, self.target))
        return results

    def jacard(self):
        results = []
        get_result = lambda i, t: {'input': i, 'target':t, 'result': self.jaccard_distance(t, input=i)}
        results.append(get_result(self.input, self.target))
        for ss_value, ss_vector in zip(self.substring, self.substring_vectors):
            results.append(get_result(ss_value, self.target))
        return results

class OrderedWordVectors(SimpleWordVector):

    def __init__(self, input, target):
        '''
        :param input:  input string to compare the target too
        :param target: target string
        '''
        super(OrderedWordVectors, self).__init__(input, target)

        self.substrings = self.build_substrings(input, max_sz=len(self.target))
        self.substrings_count = np.array()
        for substring in self.substrings:
            _, vec = self.build_vector(substring, self.letters)
            self.substrings_count = np.vstack([self.substrings_count, vec])


class FlippyWordsVectors(object):
    def __init__(self, targets: list):
        self.targets = targets
        self.permuted_targets = self.build_target_permutations(targets)

    def get_orderd_word_vectors(self, input):
        return {k: OrderedWordVectors(k, input) for k in self.permuted_targets}

    @classmethod
    def build_target_permutations(cls, targets: list):
        r = []
        if len(targets) > 1:
            r = [t for t in targets]
        return r + ["".join(i) for i in permutations(targets)]
