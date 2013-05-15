#!/usr/bin/python
# -*- coding: utf-8 -*-

from pylab import *


with open('plot-data.txt') as f:

    separator = ';'
    lines = [l.strip() for l in f.readlines()]
    X = [x.split(separator)[0].strip() for x in lines]
    Y = [y.split(separator)[1].strip() for y in lines]
    plot([i for i,x in enumerate(X)], Y)
    draw()
    title('Trend')
    xlabel('Dates')
    ylabel('Scores')
    savefig('output.png', dpi=300)
