# ============================================================================
# FILE: sorter/sublime.py
# AUTHOR: Tomoki Ohno <wh11e7rue@icloud.com>
# DESCRIPTION: Base code is from
# https://github.com/forrestthewoods/lib_fts/blob/master/code/fts_fuzzy_match.js
#              See explanation in
#              http://bit.ly/reverse-engineering-sublime-text-s-fuzzy-match
# License: MIT license
# ============================================================================

from unicodedata import category

from denite.base.filter import Base
from denite.util import Nvim, UserContext, Candidates


# Score consts
# bonus for adjacent matches
ADJACENCY_BONUS = 5
# bonus if match occurs after a separato
SEPARATOR_BONUS = 10
# bonus if match is uppercase and prev is lower
CAMEL_BONUS = 10
# penalty applied for every letter in str before the first match
LEADING_LETTER_PENALTY = -3
# maximum penalty for leading letters
MAX_LEADING_LETTER_PENALTY = -9
# penalty for every letter that doesn't matter
UNMATCHED_LETTER_PENALTY = -1


class Filter(Base):
    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'sorter/sublime'
        self.description = 'sorter for fuzzy matching like sublime text'

    def filter(self, context: UserContext) -> Candidates:
        if len(context['input']) == 0:
            return context['candidates']  # type: ignore

        for candidate in context['candidates']:
            candidate['filter__rank'] = get_score(
                context['input'], candidate['word'])

        return sorted(
            context['candidates'],
            key=lambda candidate: -candidate['filter__rank']
        )


def get_score(pattern: str, candidate: Candidates) -> int:
    # Loop variables
    score = 0
    pattern_index = 0
    pattern_length = len(pattern)
    candidate_index = 0
    candidate_length = len(candidate)
    prev_matched = False
    prev_lower = False
    prev_separator = True  # true so if first letter match gets separator bonus

    # Use "best" matched letter if multiple string letters match the pattern
    best_letter = None
    best_lower = None
    best_letter_index = None
    best_letter_score = 0

    matched_indices = []

    # Loop over strings
    while candidate_index != candidate_length:
        pattern_char = pattern[pattern_index] if (pattern_index !=
                                                  pattern_length) else None
        candidate_char: str = str(candidate[candidate_index])

        pattern_lower = pattern_char.lower() if (pattern_char is not
                                                 None) else None
        candidate_lower = candidate_char.lower()
        candidate_upper = candidate_char.upper()

        next_match = pattern_char and pattern_lower == candidate_lower
        rematch = best_letter and best_lower == candidate_lower

        advanced = next_match and best_letter
        pattern_repeat = (best_letter and pattern_char and
                          best_lower == pattern_lower)
        if advanced or pattern_repeat:
            score += best_letter_score
            matched_indices.append(best_letter_index)
            best_letter = None
            best_lower = None
            best_letter_index = None
            best_letter_score = 0

        if next_match or rematch:
            new_score = 0

            # Apply penalty for each letter before the first pattern match
            # Note: std::max because penalties are negative values.
            # So max is smallest penalty.
            if pattern_index == 0:
                penalty = max(
                    candidate_index * LEADING_LETTER_PENALTY,
                    MAX_LEADING_LETTER_PENALTY
                )
                score += penalty

            # Apply bonus for consecutive bonuses
            if prev_matched:
                new_score += ADJACENCY_BONUS

            # Apply bonus for matches after a separator
            if prev_separator:
                new_score += SEPARATOR_BONUS

            # Apply bonus across camel case boundaries.
            # Includes "clever" isLetter check.
            if all([
                prev_lower,
                candidate_char == candidate_upper,
                candidate_lower != candidate_upper
            ]):
                new_score += CAMEL_BONUS

            # Update patter index IFF the next pattern letter was matched
            if next_match:
                pattern_index += 1

            # Update best letter in str which may be for a "next" letter
            # or a "rematch"
            if new_score >= best_letter_score:
                # Apply penalty for now skipped letter
                if best_letter is not None:
                    score += UNMATCHED_LETTER_PENALTY

                best_letter = candidate_char
                best_lower = best_letter.lower()
                best_letter_index = candidate_index
                best_letter_score = new_score

            prev_matched = True
        else:
            # Append unmatch characters
            score += UNMATCHED_LETTER_PENALTY
            prev_matched = False

        # Includes "clever" isLetter check.
        prev_lower = all([
            candidate_char == candidate_lower,
            candidate_lower != candidate_upper
        ])
        prev_separator = category(candidate_char)[0] != 'L'
        # Modified from the original.
        # See http://www.fileformat.info/info/unicode/category/index.htm

        candidate_index += 1

    # Apply score for last match
    if best_letter:
        score += best_letter_score
        matched_indices.append(best_letter_index)

    return score
