
import numpy as np
from numpy.random import choice
from root_pandas import read_root

class Resampler:
    """
    A class for resampling a target feature y depending on the values
    of certain dependent features x. Reads data from a specified ROOT
    file and builds an N + 1 dimensional histogram (where N is the
    number of dependent features). It can then efficiently sample new
    values of y, given a sample of x.

    Parameters
    ---------
    fname : str
        File name of the ROOT file that contains the data to resample from
    target : str
        Name of the target feature in the ROOT file
    dependent : list of str
        List of dependent features in the ROOT file
    target_bins
        Bin edges of the target feature
    dep_bins
        List of bin edges of the dependent features
    chunksize : int, optional
        Number of entries to process at once. Default: 200000

    Extra **kwargs are passed to read_root
    """

    def __init__(self, fname, target, dependent, target_bins, dep_bins, chunksize=None, **kwargs):

        if chunksize is None:
            chunksize = 200000

        self.__call__ = np.vectorize(self.__call__)

        self.columns = dependent + [target]
        self.edges = dep_bins + [target_bins]

        # Choose histogram size according to binning
        self.histogram = np.zeros(map(lambda x: len(x) - 1, self.edges))

        print(self.histogram.shape)

        for i, chunk in enumerate(read_root(fname, "default",
                                            chunksize=chunksize,
                                            variables=self.columns,
                                            **kwargs)):

            # Bin data in N + 1 dimensions
            h , _ = np.histogramdd(chunk.as_matrix(), bins=self.edges)
            self.histogram += h

    def __call__(self, *args):
        idx = []
        # Choose dependent feature bins
        for edges, val in zip(self.edges, args):
            idx.append(np.searchsorted(edges, val) - 1)
        # Take everything from target feature
        idx.append(Ellipsis)
    
        tmp = self.histogram[idx]
        norm = np.sum(tmp)
        ix = np.arange(len(tmp))

        sampled_bin = choice(ix, p=tmp / norm)
        sampled_val = np.random.uniform(self.edges[-1][sampled_bin], self.edges[-1][sampled_bin + 1])

        return sampled_val

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    fname = './Kaon_Stripping20_MagnetUp.root'

    binning_P = np.linspace(0, 1e5, 20)
    binning_ETA = np.linspace(0, 7, 20)
    binning_nSPDHits = np.linspace(0, 800, 20)
    binning = [binning_P, binning_ETA, binning_nSPDHits]
    binning_ProbNNK = np.linspace(0, 1, 100)

    resampler = Resampler(fname, 'K_V3ProbNNK', ['K_P', 'K_Eta', 'nSPDHits'], binning_ProbNNK, binning)

    p = 10000 * np.ones(100000)
    eta = 3 * np.ones(100000)
    nSPDHits = 200 * np.ones(100000)
    
    pids = resampler(p, eta, nSPDHits)
    plt.hist(pids, bins=100)
    plt.savefig('out.pdf')

