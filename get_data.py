#!/bin/env python

from root_pandas import read_root
from pandas import DataFrame
import json
import sys
from ROOT import TFile
import subprocess
import re
import logging
logging.basicConfig(level=logging.INFO)

def wrap_iter(it):
    elem = it.Next()
    while elem:
        yield elem
        elem = it.Next()

def get_data(data):
    from numpy import zeros
    curr = data.get(0)
    ret = zeros((curr.getSize(), data.numEntries()))
    vars = []
    for v in wrap_iter(curr.iterator()):
        vars.append(v)
    idx = 0
    while curr:
        for i, v in enumerate(vars):
            var = curr.find(v)
            try:
                ret[i, idx] = var.getVal()
            except AttributeError:
                ret[i, idx] = var.getIndex()
        idx += 1
        curr = data.get(idx)
    return ret, map(lambda x: x.GetName(), vars)

with open('raw_file_locations.json') as f:
    locations = json.load(f)

for sample in locations:
    output = '{particle}_Stripping{stripping}_Magnet{magnet}.root'.format(**sample)
    for input in sample['paths']:
        logging.info('Opening file {}'.format(input))
        f = TFile.Open(input)
        ws = f.Get(f.GetListOfKeys().First().GetName())
        data = ws.allData().front()
        logging.info('Converting data')
        table, vars = get_data(data)
        df = DataFrame(table.T, columns=vars)
        logging.info('Saving data to {}'.format(output))
        df.to_root(output)

