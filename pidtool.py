#!/usr/bin/env python

from __future__ import print_function
import argparse
import numpy as np
from numpy.random import choice
import logging
import json
from TrafoProbNN import back_transform
import ROOT as R

logging.basicConfig(level=logging.INFO)


class Resampler:
    def __init__(self, *args):
        # Choose histogram size according to bin edges
        # Take under/overflow into account for dependent variables only
        edges = []
        self.histogram = None
        if args:
            print('Creating resampler with args')
            for arg in args[:-1]:
                edges.append(np.append(np.append([-np.inf], arg), [np.inf]))
            edges.append(args[-1])
            self.edges = edges

            self.histogram = np.zeros(map(lambda x: len(x) - 1, self.edges))

    def copy(self):
        '''
        Creates a copy of the resampler
        '''
        rv = Resampler()
        rv.edges = list(self.edges)
        rv.histogram = self.histogram.copy()
        return rv

    def learn(self, features, weights=None):
        assert (len(features) == len(self.edges))

        features = np.array(features)

        h, _ = np.histogramdd(features.T, bins=self.edges, weights=weights)
        self.histogram += h

    def sample(self, features):

        assert (len(features) == len(self.edges) - 1)
        args = np.array(features)
        idx = [
            np.searchsorted(edges, vals) - 1
            for edges, vals in zip(self.edges, args)
        ]
        tmp = self.histogram[idx]
        # Fix negative bins (resulting from possible negative weights) to zero
        tmp[tmp < 0] = 0
        norm = np.sum(tmp, axis=1)
        probs = tmp / norm[:, np.newaxis]
        sampled_bin = []
        for i in range(tmp.shape[0]):
            sampled_bin.append(choice(tmp.shape[1], p=probs[i, :]))
        sampled_bin = np.array(sampled_bin)
        sampled_val = np.random.uniform(
            self.edges[-1][sampled_bin],
            self.edges[-1][sampled_bin + 1],
            size=len(sampled_bin))
        # If the histogram is empty, we can't sample
        sampled_val[norm == 0] = -1000

        assert(len(features[0]) == len(sampled_val)), \
            ('Resampled values are too few.\n'
             'Features length: {}\nresampled length:{}'.format(
                len(features[0]), len(sampled_val)))
        return sampled_val


def rooBinning_to_list(rooBinning):
    return [rooBinning.binLow(i) for i in range(rooBinning.numBins())
            ] + [rooBinning.binHigh(rooBinning.numBins() - 1)]


def grab_data(options):
    import ROOT
    from ROOT import TFile
    from os.path import join, exists
    from os import makedirs

    if not exists(options.output):
        makedirs(options.output)

    logging.info('Saving nTuples to ' + options.output)

    with open(options.config) as f:
        locations = json.load(f)
    if options.particles is not None:
        locations = [
            sample for sample in locations
            if sample['particle'] in options.particles
        ]

    for sample in locations:
        output = join(
            options.output,
            '{particle}_Stripping{stripping}_Magnet{magnet}.root'.format(
                **sample))
        ff = TFile(output, 'recreate')
        ff.Close()
        for input_file in sample['paths']:
            logging.info('Opening file {}'.format(input_file))

            f = TFile(input_file)
            ws = f.Get(f.GetListOfKeys().First().GetName())
            ROOT.SetOwnership(ws, False)
            data = ws.allData().front()
            ROOT.RooAbsData.setDefaultStorageType(ROOT.RooAbsData.Tree)
            ff = TFile(output, 'update')
            dset = ROOT.RooDataSet('tree', 'tree',
                                   data.get(), ROOT.RooFit.Import(data))
            logging.info('Saving data to {}'.format(output))
            dset.tree().Write('tree')
            ff.Close()
            ws.Delete()


def create_resamplers(options):
    import os
    import pickle
    from root_pandas import read_root
    from PIDPerfScripts.Binning import GetBinScheme

    # TupleToolANNPID stores all available tunes whereas TupleToolPid stores
    # only the default tune as {}_ProbNNX
    # Information on the default tunes can be found here:
    # https://gitlab.cern.ch/lhcb/Rec/blob/master/Rec/ChargedProtoANNPID/python/ChargedProtoANNPID/Configuration.py
    pid_variables = [
        '{}_CombDLLK',
        '{}_CombDLLmu',
        '{}_CombDLLp',
        '{}_CombDLLe',
        # ProbNN
        '{}_V3ProbNNK',
        '{}_V3ProbNNpi',
        '{}_V3ProbNNmu',
        '{}_V3ProbNNp',
        '{}_V3ProbNNe',
        '{}_V3ProbNNghost',
        # transformed ProbNN with log( var/(1-var) )
        '{}_V3ProbNNK_Trafo',
        '{}_V3ProbNNpi_Trafo',
        '{}_V3ProbNNmu_Trafo',
        '{}_V3ProbNNp_Trafo',
        '{}_V3ProbNNe_Trafo',
        '{}_V3ProbNNghost_Trafo',
        # Same for V2
        '{}_V2ProbNNK',
        '{}_V2ProbNNpi',
        '{}_V2ProbNNmu',
        '{}_V2ProbNNp',
        '{}_V2ProbNNe',
        '{}_V2ProbNNghost',
        '{}_V2ProbNNK_Trafo',
        '{}_V2ProbNNpi_Trafo',
        '{}_V2ProbNNmu_Trafo',
        '{}_V2ProbNNp_Trafo',
        '{}_V2ProbNNe_Trafo',
        '{}_V2ProbNNghost_Trafo'
    ]
    # # Same for V1
    # '{}_V1ProbNNK', '{}_V1ProbNNpi', '{}_V1ProbNNmu', '{}_V1ProbNNp',
    # '{}_V1ProbNNe', '{}_V1ProbNNghost', '{}_V1ProbNNK_Trafo',
    # '{}_V1ProbNNpi_Trafo', '{}_V1ProbNNmu_Trafo', '{}_V1ProbNNp_Trafo',
    # '{}_V1ProbNNe_Trafo', '{}_V1ProbNNghost_Trafo',
    # #Same for V4
    # '{}_V4ProbNNK', '{}_V4ProbNNpi', '{}_V4ProbNNmu', '{}_V4ProbNNp',
    # '{}_V4ProbNNe', '{}_V4ProbNNghost', '{}_V4ProbNNK_Trafo',
    # '{}_V4ProbNNpi_Trafo', '{}_V4ProbNNmu_Trafo', '{}_V4ProbNNp_Trafo',
    # '{}_V4ProbNNe_Trafo', '{}_V4ProbNNghost_Trafo']

    kin_variables = ['{}_P', '{}_Eta', 'nTracks']

    with open(options.config) as f:
        locations = json.load(f)
    if options.particles:
        locations = [
            sample for sample in locations
            if sample['particle'] in options.particles
        ]
    if options.both_magnet_orientations:
        # we use both magnet orientations on the first run
        locations = [
            sample for sample in locations if sample['magnet'] == 'Up'
        ]
    for sample in locations:
        # last argument takes name of user-defined binning
        binning_P = rooBinning_to_list(
            GetBinScheme(sample['branch_particle'], 'P', None))
        # last argument takes name of user-defined binning
        # TODO: let user pass this argument
        binning_ETA = rooBinning_to_list(
            GetBinScheme(sample['branch_particle'], 'ETA', None))
        # last argument takes name of user-defined binning
        # TODO: let user pass this argument
        binning_nTracks = rooBinning_to_list(
            GetBinScheme(sample['branch_particle'], 'nTracks', None))
        if options.both_magnet_orientations:
            if sample['magnet'] == 'Up':
                data = [
                    options.location +
                    '/{particle}_Stripping{stripping}_MagnetUp.root'.format(
                        **sample)
                ]
                data += [
                    options.location +
                    '/{particle}_Stripping{stripping}_MagnetDown.root'.format(
                        **sample)
                ]
                resampler_location = options.saveto + \
                    '/{particle}_Stripping{stripping}_MagnetAny.pkl'.format(
                        **sample
                    )
        else:
            data = [
                options.location +
                '/{particle}_Stripping{stripping}_Magnet{magnet}.root'.format(
                    **sample)
            ]
            resampler_location = options.saveto + \
                '/{particle}_Stripping{stripping}_Magnet{magnet}.pkl'.format(
                    **sample
                )
        if os.path.exists(resampler_location):
            os.remove(resampler_location)
        resamplers = dict()
        deps = map(lambda x: x.format(sample['branch_particle']),
                   kin_variables)
        pids = map(lambda x: x.format(sample['branch_particle']),
                   pid_variables)
        for pid in pids:
            if 'DLL' in pid:
                # binning for DLL
                target_binning = np.linspace(-150, 150, 300)
            elif 'ProbNN' in pid and 'Trafo' in pid:
                # binning for transformed ProbNN
                target_binning = np.linspace(-30, 30, 300)
            elif 'ProbNN' in pid:
                # binning for (raw) ProbNN
                target_binning = np.linspace(0, 1, 100)
            else:
                raise Exception
            resamplers[pid] = Resampler(binning_P, binning_ETA,
                                        binning_nTracks, target_binning)

        for dataSet in data:
            # where is None if option is not set
            for i, chunk in enumerate(
                    read_root(
                        dataSet,
                        options.tree,
                        columns=deps + pids + ['nsig_sw'],
                        chunksize=100000,
                        where=options.cutstring)):
                for pid in pids:
                    resamplers[pid].learn(
                        chunk[deps + [pid]].values.T, weights=chunk['nsig_sw'])
                logging.info('Finished chunk {}'.format(i))
        with open(resampler_location, 'wb') as f:
            pickle.dump(resamplers, f)


def resample_branch(options):
    from copy import deepcopy
    for source_file in options.source_files:
        opt = deepcopy(options)
        opt.source_file = source_file
        _resample_branch(opt)


def _resample_branch(options):
    import pickle
    from root_numpy import tree2array, array2tree, list_branches
    from root_pandas import read_root
    from pandas import DataFrame
    import multiprocessing as mp
    logging.info('Starting resampling for {}'.format(options.source_file))

    logging.info('Loading config...')
    with open(options.configfile) as f:
        config = json.load(f)

    branches_in_file = list_branches(
        options.source_file, treename=options.tree)

    logging.info('Checking tasks...')
    pid_names = []
    for task in config['tasks']:
        for pid in task['pids']:
            pid_names.append(pid['name'])
            if options.transform and 'Trafo' in pid['name']:
                pid_names.append(pid['name'].replace('Trafo', 'Untrafo'))

    if all([pid_name in branches_in_file for pid_name in pid_names]):
        raise Exception(
            'Branches exist - resampling seems to be done already.')

    logging.info('Loading resamplers...')

    trueid_branches = []
    prefix_dict = {}
    # load resamplers into config dictionary
    resamplers = {}

    use_trueid = 'trueid' in config['tasks'][0]
    for task in config['tasks'][1:]:
        if use_trueid and not 'trueid' in task \
                or not use_trueid and 'trueid' in task:
            logging.error('Specify true ids on all tasks or on no task.')
            exit()

    for task in config['tasks']:
        if 'trueid_branch' in task:
            trueid_branches.append(task['trueid_branch'])
        with open(task['resampler_path'], 'rb') as f:
            try:
                resampler = pickle.load(f)
            except UnicodeDecodeError:  # pickled with python2
                resampler = pickle.load(f, encoding='latin1')

            for trueid in task.get('trueid', [None]):
                resamplers[trueid] = resamplers.get(trueid, {})
                if trueid is None:
                    prefix_dict[trueid] = None
                else:
                    prefix_dict[trueid] = task['pids'][0]['kind'].split('_')[0]

                for pid in task['pids']:
                    if not pid['kind'] in resampler:
                        logging.error(
                            'No resampler found for {kind} in {picklefile}'.
                            format(
                                kind=pid['kind'],
                                picklefile=task['resampler_path']))
                        exit()

                    resamplers[trueid][pid['kind']] = resampler[pid['kind']]

    needed_branches = [f for task in config['tasks'] for f in task['features']]

    # check if eta is in the tuple, if not store in a list to calculate later
    pseudorapidities_to_calculate = list()
    for idx, b in enumerate(needed_branches):
        if b not in branches_in_file:
            logging.info(
                'I did not find {} among the branches in the file'.format(b))
            if b.endswith('_eta'):
                logging.info('But dont worry, I know how to calculate it')
                head = b[:-4]
                pseudorapidities_to_calculate.append(head)
                needed_branches[idx] = head + '_P'
                needed_branches.append(head + '_PZ')
            else:
                logging.error('I dont know how to calculate {}'.format(b))
                exit()
    needed_branches = list(set(needed_branches))

    logging.info('Starting resampling...')

    resampled_data = DataFrame()

    chunksize = options.chunksize
    for i, chunk in enumerate(
            read_root(
                options.source_file,
                options.tree,
                columns=needed_branches + trueid_branches,
                chunksize=chunksize)):

        for ps in pseudorapidities_to_calculate:
            logging.info('Calculating pseudorapidity for {}'.format(ps))
            p = chunk[ps + '_P']
            pz = chunk[ps + '_PZ']
            chunk[ps + '_eta'] = 0.5 * np.log((p + pz) / (p - pz))

        resampled_data_chunk = DataFrame()
        var_name = []
        args = []

        for task in config['tasks']:
            deps = chunk[task['features']]

            if 'trueid_branch' in task:
                trueid = chunk[task['trueid_branch']]
            else:
                trueid = None

            for pid in task['pids']:
                if pid['name'] in branches_in_file:
                    logging.info('Skipping {}, branch already exists'.format(
                        pid['name']))
                    continue

                var_name.append(pid['name'])
                args.append((resamplers, deps.values.T, trueid, pid['kind'],
                             prefix_dict))

        p = mp.Pool(processes=options.num_cpu)
        resampled = p.map(resample_process, args)
        p.terminate()

        # transform branches back
        for idx, var in enumerate(var_name):
            resampled_data_chunk[var] = resampled[idx]
            if 'Trafo' in var and options.transform:
                logging.info('Back trafo for {}'.format(var))
                resampled_data_chunk[var.replace('Trafo', 'Untrafo')] = \
                    back_transform(resampled[idx])

        logging.info('Processed {} entries'.format((i + 1) * chunksize))
        resampled_data = resampled_data.append(
            resampled_data_chunk, ignore_index=True)

    logging.info('Writing output...')
    f = R.TFile(options.source_file, 'UPDATE')
    t = f.Get(options.tree)
    if '/' in options.tree:
        t_path = options.tree.split('/')[:-1]
        t_dir = f.Get('/'.join(t_path))
        t_dir.cd()
    print(resampled_data.tail())
    array2tree(
        resampled_data.to_records(index=False), tree=t, name=options.tree)
    t.Write()
    f.Close()


def resample_process(res_deps):
    resamplers, deps, trueid, pid, prefix_dict = res_deps
    res = np.zeros(deps.shape[1])
    mask = np.ones(deps.shape[1], dtype=bool)

    for t in prefix_dict:
        if t is None:
            res = resamplers[t][pid].sample(deps)
            mask = False
            continue

        idx = np.array(trueid == t, dtype=bool)
        mask[idx] = False
        pid_tail = '_'.join(pid.split('_')[1:])
        pid_name = '_'.join([prefix_dict[t], pid_tail])
        res[idx] = resamplers[t][pid_name].sample(deps[:, idx])
    res[mask] = -9999

    return res


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

grab = subparsers.add_parser(
    'grab_data',
    help='Downloads PID calib data from EOS and saves it as NTuples')
grab.set_defaults(func=grab_data)
grab.add_argument(
    '-c',
    '--config',
    default='raw_data.json',
    help='Config-file with raw_data in it.'
    ' Default: raw_data.json')
grab.add_argument(
    'output', help='Directory where grabbed data is being stored.')
grab.add_argument(
    '--particles',
    nargs='*',
    help='Optional subset of particles for which calibration data will be '
    'downloaded.')

create = subparsers.add_parser(
    'create_resamplers', help='Generates resampling histograms from NTuples')
create.set_defaults(func=create_resamplers)
create.add_argument('location', help='Directory where input files are stored.')
create.add_argument(
    'saveto', help='Directory where to save the resamplers as .pkl - files.')
create.add_argument(
    '--particles',
    nargs='*',
    help='Optional subset of particles for which resamplers will be created.')
create.add_argument(
    '--cutstring',
    help='Optional cutstring. For example you can cut on the runNumber.')
create.add_argument(
    '--merge-magnet-orientations',
    dest='both_magnet_orientations',
    action='store_true',
    default=False,
    help='Create a resampler that combines the raw data for magup and magdown.'
)
create.add_argument(
    '-c',
    '--config',
    default='raw_data.json',
    help='Config-file with raw_data in it. Default: raw_data.json')
create.add_argument(
    '--tree',
    help='Optional tree name to use. Has to be used if you have multiple trees'
    ' in file or have several subsets of the same tree.')

resample = subparsers.add_parser(
    'resample_branch',
    help='Uses histograms to add resampled PID branches to a dataset')
resample.set_defaults(func=resample_branch)
resample.add_argument('configfile')
resample.add_argument('source_files', nargs='+')
# resample.add_argument('output_file')
resample.add_argument(
    '--num_cpu',
    '-n',
    help='Number of cpus used for resampling',
    default=1,
    type=int)
resample.add_argument(
    '--chunksize',
    help='Size of the chunks that are read from the root file',
    default=300000,
    type=int)
resample.add_argument(
    '--tree',
    help='Optional tree name to use. Should be used if you have '
    'multiple trees in file.')
resample.add_argument(
    '--outputtree',
    help='Optional tree name to use. Should be used if you have multiple trees'
    ' in file or if you have a slash in your tree name.')
resample.add_argument(
    '--transform',
    action='store_true',
    help='Perform in place back transformation for ProbNN variables')

if __name__ == '__main__':
    options = parser.parse_args()

    options.func(options)
