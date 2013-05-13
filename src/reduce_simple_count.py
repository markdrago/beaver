#!/usr/bin/env python

from __future__ import print_function
import sys

def reduce_all():
    current_word = None
    current_count = 0
    for line in sys.stdin:
        line = line.strip()

        #treat everything to the left like one big data field
        word, count = line.rsplit(' ', 1)
        count = int(count)

        if current_word == word:
            current_count += count
        else:
            if current_word:
                print(current_word + " " + str(current_count))
            current_count = count
            current_word = word
    if current_word and current_count > 0:
        print(current_word + " " + str(current_count))

if __name__ == '__main__':
    reduce_all()

