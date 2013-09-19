#! /usr/bin/env python

'''This module is for creating n-back sequences.

An n-back sequence is a sequence of stimuli consisting of three stimulus
types: targets, lures, and fillers. A target is a stimulus that is identical to
the stimulus that appeared n positions prior in the sequence. A filler is a
stimulus that has not appeared previously in the sequence. A lure of level k is
a non-target stimulus that is identical to the stimulus that appeared k
positions prior in the sequence.

The lure level cannot be the same as the n-level. A sequence may contain any
number of lure types. For example, a 3-back sequence may contain 1-back lures,
2-back lures, 4-back lures, 5-back lures, etc.'''


import random

class UnsatisfiableException(Exception):
    '''Raised when a solution cannot be found given the constraints'''
    pass


class Nback(object):
    '''A family of nback sequences'''
    def __init__(self, level, targets, fillers, lures=None, max_repeat=0):
        '''Describes a family of n-back sequences.

        Args:
            level: the n-level for the sequence (>= 1)
            targets: number of targets in the sequence (>= 0)
            fillers: number of fillers in the sequence (>= 0)
            lures: dictionary mapping n to count (analogous to n, targets). So,
                lures={2: 4} produces 4 2-lures
            max_repeat: optional maximum number of times an item repeats itself

        Raises:
            ValueError: Parameters set to impossible values
        '''
        # Sanity checking
        if level < 1:
            raise ValueError('n level must be >= 1')
        if (targets < 0) or (fillers < 0) or min(lures.values()) < 0:
            raise ValueError('Cannot have negative numbers of items')
        if fillers < min(lures.keys() + [level]):
            raise ValueError('Need more fillers than lowest lure / n level')
        if min(lures.keys()) <= 0:
            raise ValueError('Lure levels must be positive numbers')
        if max_repeat < 0:
            raise ValueError("max_repeat cannot be negative")
        if max_repeat == 1:
            if level == 1:
                raise ValueError('max_repeat and n-level cannot both be 1')
            if lures.get(1, 1) > 0:
                raise ValueError('max_repeat cannot be 1 with 1-lures')

        self._level = level
        self._targets = targets
        self._fillers = fillers
        self._lures = lures or {}
        self._max_repeat = max_repeat

        # Targets and lures are conceptually no different, so we'll call them
        # both 'pairs'
        self._pairs = [level] * targets
        for distance, count in self._lures.items():
            self._pairs.extend([distance] * count)

        # Since each pair needs two tokens, the total length is twice the number
        # of pairs, plus however many fillers we need
        self._length = len(self._pairs) + fillers
        # And we'll only have fillers unique tokens in the output, since each
        # pair only repeats a previous value
        self._unique = fillers

        # Lastly, check if any of the lures is too long for that sequence lenght
        if max(k + v for k, v in self._lures.items()) > self._length:
            raise ValueError(
                'Lure levels / counts too high for length %s' % self._length)

    def sequence(self, tokens):
        '''Generate a sequence from this family of n-back sequences'''
        # Check to make sure we have enough tokens
        if len(tokens) < self._unique:
            raise ValueError('Need at least %s tokens' % self._unique)

        # We'll make a shuffled copy of tokens
        tokens = random.sample(tokens, len(tokens))
        placements = self.place(self._fillers, self._pairs)
        return [tokens[i] for _, i in sorted(placements)]

    @classmethod
    def place(cls, fillers, pairs, available=None, item=0):
        '''Return an array of tuples of (position, item) representing a
        sequence that can later be merged with a set of tokens. For example,
        [1, 2, 3, 1, 2, 2]. Available describes the spots where items can still
        be placed, fillers is a count of fillers we have left to place, and the
        same with pairs'''
        # If no 'available' was provided, we'll initialize it to the set of all
        # positions we have to choose from.
        available = available or set(range())

        # You could do one of two things here -- go through each position, and
        # randomly select an item to place there, OR place each item in a random
        # available spot. They're equivalent, but one will make more sense to
        # you. For instance, placing each item in a random spot makes more sense
        # to me :-)

        # If we've run out of items to place, then we've not voilated any
        # constraints on the way down, so we can return our solution
        if (fillers == 0) and (len(pairs) == 0):
            return []

        # Let's say we're going to put a filler in first. We'll go through each
        # spot we could place it in, but in a random order
        spots = random.sample(available, len(available))
        for spot in spots:
            # Place our filler at this spot, and check to see if it would
            # voilate any condition. If so, we'll skip this branch
            if voilates_constraints:
                continue

            # Othewrise, let's see if this branch yields a solution. If not,
            # then we'll try something else.
            try:
                return [(spot, item)] + cls.place(
                    fillers - 1, pairs, available - set([spot]), item + 1)
            except UnsatisfiableException:
                continue

        # The code for choosing a pair is left as an exercise.

        # If we've exhausted all the possible placements for this item, then
        # there is no solution and it's unsatisfiable
        raise UnsatisfiableException('Nuff said')
