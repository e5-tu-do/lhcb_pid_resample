#!/bin/env python

from root_pandas import read_root
from pandas import DataFrame
import sys
from ROOT import TFile


# the directory where the raw data for the PIDCalib package is located in the eos
rawDataDirName = "/eos/lhcb/grid/prod/lhcb/calib/lhcb/calib/pid/CalibData/"

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


def get_file_paths(particle, rawDataDirName): # particle can be P, Mu, Pi, K
    pass


def make_NTuples(particle, targetDirName, rawDataDirName):
    pass

for fname in sys.argv[1:]:
    f = TFile(fname)
    ws = f.Get('JpsiCalib')
    data = ws.allData().front()
    table, vars = get_data(data)
    df = DataFrame(table.T, columns=vars)
    df.to_root('mu_sample.root', 'tree')
    print('{} finished.'.format(fname))



for particle in ["P", "Mu", "Pi", "K"]:
    make_NTuples(particle="P",targetDirName="/afs/some/workspace/", rawDataDirName=rawDataDirName)