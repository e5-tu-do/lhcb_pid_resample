
import sys
import os.path
import numpy as np
from resampler import Resampler
import pickle
import json

pid_variables = ['V3ProbNNK']
kin_variables = ['{}_P', '{}_Eta', 'nSPDHits']

binning_P = np.linspace(0, 1e5, 20)
binning_ETA = np.linspace(0, 7, 20)
binning_nSPDHits = np.linspace(0, 800, 20)
binning = [binning_P, binning_ETA, binning_nSPDHits]
binning_ProbNN = np.linspace(0, 1, 100)

dataLocation = sys.argv[1]

with open('raw_file_locations.json') as f:
    locations = json.load(f)

for sample in locations:
    data = dataLocation + '/{particle}_Stripping{stripping}_Magnet{magnet}.root'.format(**sample)
    resampler_location = '{particle}_Stripping{stripping}_Magnet{magnet}.pkl'.format(**sample)
    resamplers = dict()
    deps = map(lambda x: x.format(sample['branch_particle']), kin_variables)
    if os.path.isfile(data):
        for pid in pid_variables:
            target = '{}_{}'.format(sample['branch_particle'], pid)
            resamplers[pid] = Resampler(data, target, deps, binning_ProbNN, binning)

        with open(resampler_location, 'wb') as f:
            pickle.dump(resamplers, f)

