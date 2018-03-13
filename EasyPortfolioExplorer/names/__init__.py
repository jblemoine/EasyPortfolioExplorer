import os
from functools import lru_cache
from random import randint

FILES = os.path.dirname(os.path.realpath(__file__))+'/names.txt'

@lru_cache(maxsize=128)
def get_file(filename):

    with open(filename) as file:
        strg = file.read().split('\n')
    return strg


def get_full_name():
    lst = get_file(FILES)
    return lst[randint(0, len(lst)-1)]

