# lhcb_pid_resample

Resample ("reweight") simulated values using clean data samples.
The aim of this project is to simplify and accelerate the tedious task of resampling PIDs and other variables.

## Caveats

This package resamples PID variables one by one. Therefore it doesn't reflect the correlations between them, except for those that already originate from correlations to the kinematic variables that we resample from.

## Requirements:

* [`root_pandas`](https://github.com/ibab/root_pandas)

## Installation:

Clone from git:

    git clone git@github.com:e5-tu-do/lhcb_pid_resample.git

At the moment the software also requires the following folder from the LHCb PIDCalib package:

    http://svn.cern.ch/guest/lhcb/Urania/trunk/PIDCalib/PIDPerfScripts/python/

You can either check it out directly or get it via getpack, for example when setting up PIDCalib as described here: https://twiki.cern.ch/twiki/bin/view/LHCb/PIDCalibPackage
In both cases you need to add the folder to your PYTHONPATH. *Warning: there might be an issue, where you have to create an empty `__init__.py` file in `PIDPerfScripts/python/` to configure this correctly!*

## Usage:

### 1. Prepare simulated data ("Monte Carlo").

The following variables need to be present in the simulated data for any `<particle>` who's PID should be resampled:
* `<particle>_P` (in MeV)
* `<particle>_ETA`
* `nTracks`

The name of the `<particle>` can be chosen by the user (e.g. `muplus`).
These variables are used as dependent variables in the resampling process.
It is not yet supported to define a custom set of dependent variables in the options file.

However, in some cases it is better to avoid the track multiplicity as an input variable, which at the moment still requires some small modifications in the code.

### 2. Download raw data from EOS.

This needs to be run from a location where EOS access is supported.

Data must be downloaded for any particle type who's PID should be resampled. Since this is a tedious process,
we recommend you store the downloaded files locally and keep them for around for future analyses. You only need to
repeat the download when the raw data is updated.

The raw data is maintained by maintainers of the [LHCb PIDCalib packages](https://twiki.cern.ch/twiki/bin/view/LHCb/PIDCalibPackage).

To start the download, call

    python pidtool.py grab_data <output>

where `<output>` is the directory in which the downloaded data should be stored.
If you want to limit your download to certain particle types, you can specify them using the option
`--particles`.
For example `python pidtool.py grab_data ./ --particles Mu` will download muon data to the current directory.
For more information and a list of possible particles type `python pidtool.py grab_data --help`

*There is a known issue where the download causes a segfault after completing. If this happens to you, please make sure you have downloaded all the data by checking the `raw_data.json` file.*

### 3. Create resamplers

A resampler is a worker object that performs the resampling for a specific particle and PID type. Resamplers can be created only for particles types whose data has been downloaded.

To create resamplers for all particle types and PID types, do

    python pidtool.py create_resamplers <input>

Where  `<input>` is the directory where `grab_data` downloaded the `.root` - files. Like before, you can limit yourself to a selection of particle types using the `--particles` option. It is also possible to apply a cutstring to the downloaded data using `--cutstring <cutstring>`. This can for example be used to restrict the raw data to certain runs. Lastly, there is `--merge-magnet-orientations`, which let's you create resamplers that combine the raw data for magUp and magDown. 

### 4. Run the resampling
The command

    python pidtool.py resample_branch <configfile> <source_file> <output_file>

will run the resampling. `<source_file`> is the root file containing the simulated data and `<output_file>` can be chosen freely. An example config-file called `config.json` is part of the repository. In the configurations file, the options are:
* `tasks` : A list of resampling-tasks. Create a task for every particle for which you want to resample PIDs.
  * `resampler_path` : Path to resampler pickle-file to be used for resampling. The resampler name will contain the `particle` - name, the stripping version and the magnet orientation.
  * `pids` : List of all pid branches to be created for this particle.
    * `kind` : Type of PID. Possible values are `X_CombDLLK`, `X_CombDLLmu`, `X_CombDLLp`, `X_CombDLLe`, `X_V3ProbNNK`, `X_V3ProbNNpi`, `X_V3ProbNNmu`, `X_V3ProbNNp`, where X can be `P`,`K`,`pi`,`Mu` or `e`.
    * `name` : Name of the resulting branch, to be chosen freely.
