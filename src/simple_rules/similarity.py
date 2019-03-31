class WordSimilarity(object):

    def __init__(self, word):
        self.word = word

    def in_phrase(self, phrase):
        return False

    def similarity(self, phrase):
        return -1.0

    def euclidean(self, phrase):
        return -1.0

    def cosine(self, phrase):
        return -1.0

    def jaccard(self, phrase):
        return -1.0

    def manhattan(self, phrase):
        return -1.0

    def apply(self, phrase, fn):
        return -1.0

    def filter(self, phrase, chars=ASCII_CHARS):
        return "".join([i for i in phrase if i in chars])
