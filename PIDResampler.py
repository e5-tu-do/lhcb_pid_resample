#!/bin/env python
import numpy
from root_pandas import read_root
from pandas import DataFrame


from numpy import *
from numpy.random import *
from numpy.random import choice


class PIDResampler:

    def __init__(self, particle, pid, binning_P=numpy.linspace(0, 5e3, num=15), binning_ETA=numpy.linspace(0, 7, num=15), selection=None):

        self._particle = particle
        self._pid = pid

        # figure out which histogram to get exactly
        inputFileName = "test_Kaon_Stripping20_MagnetUp.root"

        binning_P = append(append([-inf], binning_P), [inf])
        binning_ETA = append(append([-inf], binning_ETA), [inf])
        binning_PID = append(append([-inf], linspace(-5, 5, 99, dtype=float64)), [inf])

        self.histogram, self.edges = histogramdd([], bins=[binning_P, binning_ETA, binning_PID])
        for chunk in read_root(inputFileName, "default", chunksize=100000, selection=selection, variables = [particle+"_P", particle+"_ETA",particle+"_"+pid] ):
            h , _ = histogramdd(chunk[[particle+"_P", particle+"_ETA",particle+"_"+pid]], bins=[binning_P, binning_ETA, binning_PID])
            histogram +=h


    def _resample(p, eta):

        p_bin = numpy.searchsorted(self.edges[0],p)-1
        eta_bin = numpy.searchsorted(self.edges[1],eta)-1
    
        pid = self._histogram[p_bin,eta_bin,:]
        norm = sum(pid)
        idx = arange(len(pid))

        sampled_bin = numpy.choice(idx, p=pid / norm)
        sampled_pid = uniform(self.edges[sample], self.edges[sample+1])

        return sampled_pid