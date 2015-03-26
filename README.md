# lhcb_pid_resample

Resample ("reweight") simulated values using clean data samples.
The aim of this project is to allow simplify and accelerate the tedious task of resampling PIDs and other variables.

## Installation:

TODO

## Usage:

### 1. Prepare simulated data ("Monte Carlo").

The following variables need to be present in the simulted data for any `<particle>` who's PID should be resampled:
* `<particle>_P` (in MeV)
* `<particle>_ETA`
* `nTracks`

The name of the `<particle>` can be chosen by the user.
These variables are used as dependet variables in the resampling process.
It is not yet supported to define a custom set of dependet variables in the options file.

However, in some cases it is better to avoid the track multiplicity as an input variable, which at the moment still requires some small modifications in the code.

### 2. Download raw data from EOS.

Data must be downloaded for any particle type who's PID should be resampled. Since this is a tedious process, 
we recommend you store the downloaded files locally and keep them for around for future analyses. You only need to 
repeat the download when the raw data is updated.

The raw data is maintained by maintainers of the [LHCb PIDCalib packages](https://twiki.cern.ch/twiki/bin/view/LHCb/PIDCalibPackage).

To start the download, call

    python pidtool.py grab_data <output>
    
where `<output>` is the directory in which the downloaded data should be stored.
If you want to limit your download to certain particle types, you can specify them using the option
`--particles`.
For example `python pidtool.py grab_data ./ --particles Mu` will download muon- data to the current directory. 
For more information and a list of possible particles type `python pidtool.py grab_data --help`
