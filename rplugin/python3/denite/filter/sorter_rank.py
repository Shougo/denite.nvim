# ============================================================================
# FILE: sorter_rank.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# CONTRIBUTOR: David Lee
#              Jean Cavallo
# DESCRIPTION: Base code is from "sorter_selecta.py" in unite.vim
#              Scoring code by Gary Bernhardt
#     https://github.com/garybernhardt/selecta
# License: MIT license
# ============================================================================

import string
from .base import Base
from denite.util import split_input


class Filter(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'sorter_rank'
        self.description = 'rank matcher'

    def filter(self, context):
        if len(context['input']) < 1:
            return context['candidates']
        for c in context['candidates']:
            c['filter__rank'] = 0

        for pattern in split_input(context['input']):
            for c in context['candidates']:
                c['filter__rank'] += get_score(c['word'], pattern)
        return sorted(context['candidates'],
                      key=lambda x: x['filter__rank'])


BOUNDARY_CHARS = string.punctuation + string.whitespace


def get_score(string, query_chars):
    # Highest possible score is the string length
    best_score = len(string)
    head, tail = query_chars[0], query_chars[1:]

    # For each occurence of the first character of the query in the string
    for first_index in (idx for idx, val in enumerate(string)
                        if val == head):
        # Get the score for the rest
        score, last_index = find_end_of_match(string, tail, first_index)

        if last_index and score < best_score:
            best_score = score

    # Solve equal scores by sorting on the string length. The ** 0.5 part makes
    # it less and less important for big strings
    best_score = best_score * (len(string) ** 0.5)
    return best_score


def find_end_of_match(to_match, chars, first_index):
    score, last_index, last_type = 1.0, first_index, None

    for char in chars:
        try:
            index = to_match.index(char, last_index + 1)
        except ValueError:
            return None, None
        if not index:
            return None, None

        # Do not count sequential characters more than once
        if index == last_index + 1:
            if last_type != 'sequential':
                last_type = 'sequential'
                score += 1
        # Same for first characters of words
        elif to_match[index - 1] in BOUNDARY_CHARS:
            if last_type != 'boundary':
                last_type = 'boundary'
                score += 1
        # Same for camel case
        elif (char in string.ascii_uppercase and
              to_match[index - 1] in string.ascii_lowercase):
            if last_type != 'camelcase':
                last_type = 'camelcase'
                score += 1
        else:
            last_type = 'normal'
            score += index - last_index
        last_index = index
    return (score, last_index)
