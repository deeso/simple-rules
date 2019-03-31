

class LetterVector:

    @classmethod
    def letter_union_vector(cls, word, input_string):
        letters = set(word) | set(input_string)

