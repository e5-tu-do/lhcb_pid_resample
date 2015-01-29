#!/bin/env python
import numpy
from root_pandas import read_root
from pandas import DataFrame

class PIDResampler:
	def make_histogram(self, particle_name, pid_name, binning_P=numpy.linspace(0, 5e3, num=15), binning_ETA=numpy.linspace(0, 7, num=15)):
		# figure out which histogram to get exactly
		inputFileName = ".Kaon_Stripping20_MagnetUp.root"

		for chunk in read_root(inputFileName, "default", chunksize=100000):



