#!/usr/bin/env python

import random
import pprint

class Deck(object):

    def __init__(self):
        self.deck = []
        self.discard = []

    def draw(self):
        try:
            card = self.deck.pop()
        except IndexError:
            self.shuffle()
            card = self.deck.pop()
        self.discard.append(card)
        return card

    def shuffle(self):
        print "Shuffling"
        while len(self.discard) > 0:
            self.deck.append(self.discard.pop(random.randrange(len(self.discard))))

def main():
    d = Deck()
    d.discard.extend([
        { 'action': 'random', 'direction': 'NE', },
        { 'action': 'random', 'direction': 'NO', },
        { 'action': 'random', 'direction': 'E', },
        { 'action': 'random', 'direction': 'O', },
        { 'action': 'random', 'direction': 'SE', },
        { 'action': 'random', 'direction': 'SO', },
        { 'action': 'direction', 'direction': 'NE', },
        { 'action': 'direction', 'direction': 'NO', },
        { 'action': 'direction', 'direction': 'E', },
        { 'action': 'direction', 'direction': 'O', },
        { 'action': 'direction', 'direction': 'SE', },
        { 'action': 'direction', 'direction': 'SO', },
        { 'action': 'pheromon', 'direction': 'NE', },
        { 'action': 'pheromon', 'direction': 'NO', },
        { 'action': 'pheromon', 'direction': 'E', },
        { 'action': 'pheromon', 'direction': 'O', },
        { 'action': 'pheromon', 'direction': 'SE', },
        { 'action': 'pheromon', 'direction': 'SO', },
        ])
    while True:
        raw_input()
        c1 = d.draw()
        c2 = d.draw()
        print "%s -> %s" % (c1['action'], c2['direction'])

if __name__ == "__main__":
    main()
