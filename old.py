#! /usr/bin/env python

"""
Created on Aug 21, 2013

@author: Alan Mishler

This module is for creating n-back sequences.

An n-back sequence is a sequence of stimuli consisting of three stimulus types_ints: 
targets, lures, and fillers. A target is a stimulus that is identical to the 
stimulus that appeared n positions prior in the sequence. A filler is a stimulus 
that has not appeared previously in the sequence. A lure of level k is a
non-target stimulus that is identical to the stimulus that appeared k positions
prior in the sequence. The lure level cannot be the same as the n-level.
A sequence may contain any number of lure types_ints. For example, a 3-back sequence 
may contain 1-back lures, 2-back lures, 4-back lures, 5-back lures, etc.

"""
import random

FILLER = 0

class Nback:
    
    """An Nback object is used to construct an n-back sequence.""" #how should I list public methods and instance vars?
    
    def __init__(self, n, targets, fillers, lures = {1:0}, max_repeat = 0):
        """Sets up an nback sequence to be filled in later with set_items().
        
        Args:
            n: the n-level that defines targets (any positive integer)
            targets: The number of targets in the sequence (any non-negative integer)
            fillers: The number of fillers in the sequence (any non-negative integer)
            lures: An optional  dictionary of lure levels and numbers of lures.
                For example, {2:4, 5:8} produces a sequence with 4 2-back lures 
                and 8 5-back lures. Default produces no lures.
            max_repeat: An optional limit on the number of times in a row a
                stimulus can occur. May be set to any positive integer. By
                default, no limit is set.
        
        Returns:
            An Nback object with attributes set to corresponding parameters.
        
        Raises:
            ValueError: Parameters set to impossible values.
            WordlistError: Wordlist used to assign stimuli is too short.
            
        """
        if n < 1:
            raise ValueError("n level must be >= 1")
        if (targets < 0) or (fillers < 0) or any(lures[i] < 0 for i in lures):
            raise ValueError("Cannot have negative numbers of items")
        if fillers < min(lures.keys() + [n]):
            raise ValueError("Number of fillers must be >= the lesser of the n-level and the lowest lure level")
        if any(i < 0 for i in lures):
            raise ValueError("Lure levels must be positive numbers")
        if max_repeat < 0:
            raise ValueError("max_repeat cannot be negative")
        if max_repeat == 1:
            if n == 1:
                raise ValueError("n-level and max_repeat cannot both be set to 1")
            if (1 in lures) and (lures[1] > 0):
                raise ValueError("max_repeat cannot be set to 1 when there are level-1 lures")
        # target level
        self.n = n
        # max number of times a given stimulus can occur in a row, regardless of item type
        self.max_repeat = max_repeat
        self.items = []
        self.currentItem = {}
        # set dict of item types_ints
        self.targets = targets
        self.fillers = fillers
        self.lures = lures
        self.types_ints = dict(lures.items() + [(FILLER, fillers), (n, targets)])
        self.types_strings = dict([(i, str(i) + "lure") for i in lures] + 
                                  [(FILLER, "filler")] + [(self.n, "target")])
        self.seqlength = fillers + targets + sum(lures[key] for key in lures.keys())
        if (max([i + lures[i] for i in lures]) > self.seqlength):
            raise ValueError("Lure levels/numbers are too high for sequence of length " + str(self.seqlength))
        self.wordlist = range(fillers)
        self.wordlist.reverse()
        self.trace = []
        self.backtrack_count = 0
        
    def set_items(self):
        """Add items to self.items list until the sequence is populated."""
        while len(self.items) < self.seqlength:
            self.add_item()
            
    def add_item(self):
        """Add a single item to the sequence."""
        self.currentItem = {}   # empty item
        self.currentItem['types_available'] = self.get_types() # candidate item types_ints
        while self.currentItem['types_available'] == []:
            try:
                self.backtrack()
            except IndexError:
                print('Couldn\'t construct list! Try again  with different parameters.')
                exit()
        self.currentItem['type'] = self.choose_random_itemtype()
        self.types_ints[self.currentItem['type']] -= 1
        self.currentItem['stim'] = self.get_stim() ##
        self.items.append(self.currentItem)
        
    def choose_random_itemtype(self):
        """Randomly select an itemtype from the types_ints available for the given
        item, weighted by the number of items of each available type remaining.
        in the sequence.
        """
        available = [itemtype for itemtype in self.currentItem['types_available']]
        expanded = []
        map(expanded.extend, [[item]*self.types_ints[item] for item in available])
        return(random.choice(expanded))
    
    def backtrack(self):
        """Pop the current item off the list and change the itemtype of the
        previous item.
        """
        self.backtrack_count += 1
        self.currentItem = self.items.pop()
        self.types_ints[self.currentItem['type']] += 1
        if self.currentItem['type'] == FILLER:
            self.wordlist.append(self.currentItem['stim'])
        self.currentItem['types_available'].remove(self.currentItem['type'])
        
    def get_stim(self):
        """Set the stimulus of the current item based on its itemtype and
        the preceding stimuli.
        """
        item_type = self.currentItem['type']
        if item_type == FILLER:
            stim = self.wordlist.pop()
        else:
            stim = self.items[-item_type]['stim']
        return(stim)
    
    def get_types(self):
        """Get the itemtypes available for the current item, based on the
        preceding items in the sequence as well as itemtypes that still need to 
        be assigned.
        """
        available_types = []
        # check if fillers available
        if self.types_ints[FILLER] > 0:
            available_types.append(FILLER)
        # check if targets available
        if (self.types_ints[self.n] > 0) & (len(self.items) >= self.n):
            target_available = True
            if self.repeat_limit_reached():
                target_available = (self.items_different(-1, -self.n))
            if target_available:
                available_types.append(self.n)
        # check if various lures available
        for lure_level in self.lures.keys():
            if (self.types_ints[lure_level] > 0) & (len(self.items) >= lure_level):
                lure_available = [True]
                if len(self.items) >= self.n:
                    lure_available.append(self.items_different(-self.n, -lure_level))
                if self.repeat_limit_reached():
                    lure_available.append(self.items_different(-1, -lure_level))
                if all(lure_available):
                    available_types.append(lure_level)
        return(available_types)
    
    def repeat_limit_reached(self):
        """Check if most recent stimulus has occurred the max number of times in a row."""
        if self.max_repeat == 0:
            return(False)
        if len(self.items) < self.max_repeat:
            limit_reached = False
        elif self.max_repeat == 1:
            limit_reached = True
        else:
            limit_reached = not self.items_different(range(-self.max_repeat, 0))
        return(limit_reached)
    
    def items_different(self, index1, index2):
        """Compare two items in indexed positions to see stimuli the same."""
        compare = [self.items[index1]['stim'], self.items[index2]['stim']]
        return(not compare[0] == compare[1])
    
    def set_words(self, wordlist, randomize = True):
        """Convert item stimuli from integers to strings drawn from wordlist.
        
        Args:
            wordlist: A list of strings to assign as stimuli.
            randomize: True by default. If True, shuffle wordlist before
                assigning stimuli.
        
        Returns:
            None. Converts stimuli from integers to words.
        """
        if randomize:
            random.shuffle(wordlist)
        wordlist.reverse()
        selected = []
        while len(selected) < self.fillers:
            try:
                stim = wordlist.pop()
            except IndexError:
                raise WordlistError(len(selected), self.fillers)
            if stim in selected:
                print("Removing duplicate word: %s" %stim)
            else:
                selected.append(stim)
        for item in self.items:
            item['stim'] = selected[item['stim']]
            
    def print_sequence(self):
        """Prints sequence positions, item types_ints and item stims in csv format."""
        row = 1
        print('Position,ItemType,Stimulus')
        for item in self.items:
            print(str(row) + ',' + self.types_strings[(item['type'])]  + ',' + item['stim'])
            row += 1
            
    def write(self, filename):
        """Writes sequence positions, item types_ints and item stims in csv format."""        
        row = 1
        with open(filename, 'w') as out:
            out.write('Position,ItemType,Stimulus\n')
            for item in self.items:
                out.write(str(row) + ',' + self.types_strings[(item['type'])] + ',' + item['stim'] + '\n')
                row += 1

class WordlistError(Exception):
    """Exception raised when wordlist is too short."""
    
    def __init__(self, listlength, fillers):
        """Args:
            listlength: length of wordlist provided
            fillers: length of list needed, equal to number of fillers in sequence
        """
        self.listlength = listlength
        self.fillers = fillers
        self.message = "Wordlist too short. Unique words: %s. Words needed: %s." % (self.listlength, self.fillers)
        
    def __str__(self):
        return repr(self.message)