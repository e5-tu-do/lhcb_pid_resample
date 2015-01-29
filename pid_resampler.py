#!/usr/bin/env python

import numpy as np
from numpy.random import choice
from root_pandas import read_root
import logging
logging.root.setLevel(logging.INFO)

class PIDResampler:

    def __init__(self, particle, pid, binning_P=np.linspace(0, 1e5, num=15), binning_ETA=np.linspace(0, 7, num=15), selection=None):

        self.particle = particle
        self.pid = pid

        # TODO figure out which histogram to get exactly
        inputFileName = "Kaon_Stripping20_MagnetUp.root"

        if 'ProbNN' in pid:
            binning_PID = np.linspace(0, 1, 99, dtype=np.float64)
        else:
            binning_PID = np.linspace(-5, 5, 99, dtype=np.float64)

        columns = [particle+"_P", particle+"_Eta",particle+"_"+pid]
        binning = [binning_P, binning_ETA, binning_PID]

        self.histogram = np.zeros(map(lambda x: len(x) - 1, binning))
        self.edges = binning

        for i, chunk in enumerate(read_root(inputFileName, "default",
                                            chunksize=100000,
                                            selection=selection,
                                            variables=columns)):

            h , _ = np.histogramdd(chunk.as_matrix(), bins=binning)
            self.histogram +=h
            logging.info('Finished chunk {}'.format(i))

    def __call__(self, p, eta):
        p_bin = np.searchsorted(self.edges[0], p) - 1
        eta_bin = np.searchsorted(self.edges[1], eta) - 1
    
        pid = self.histogram[p_bin, eta_bin, :]
        norm = np.sum(pid)
        idx = np.arange(len(pid))

        sampled_bin = choice(idx, p=pid / norm)
        sampled_pid = np.random.uniform(self.edges[2][sampled_bin], self.edges[2][sampled_bin+1])

        return sampled_pid

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    resampler = PIDResampler('K', 'V3ProbNNK')
    pids = []
    for i in range(100000):
        pids.append(resampler(10000, 3))
    plt.hist(pids, bins=100)
    plt.savefig('out.pdf')

