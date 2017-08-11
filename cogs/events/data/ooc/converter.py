#!/usr/bin/env python3.6

import sys
import os
import csv
import re

quotes = []
with open('./ooc.log', 'r') as fobj:
    for line in fobj.readlines():
        possible_quote = ' '.join(line.split(' ')[4:])
        for group in re.findall('"(.*)"', possible_quote):
            quotes.append(group)
with open('./ooc.txt', 'w') as fobj:
    for quote in quotes:
        fobj.write(quote)
        fobj.write("\n")
