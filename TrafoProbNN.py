#!/usr/bin/python
import ROOT
import array
import itertools
import numpy as np
import math
from argparse import ArgumentParser
import os.path


def get_any_tree(tfilepath):
    '''
    If given a root file with only one tree, this function will return the name the tree.
    '''
    from root_numpy import list_trees
    trees = list_trees(tfilepath)
    if len(trees) == 1:
        tree_name = trees[0]
    else:
        raise ValueError('More than one tree found in {}'.format(tfilepath))

    return tree_name


def back_transform(var):
    '''
    Performs the back transformation of ProbNN variables, using numpy magic
    for huge speedup when passing arrays to this function.
    This function does not return anything, but changes the passed array in
    place.
    For the per-event back transformation when looping over a TTree use
    UntrafoProbNN
    '''
    error_mask = var < -500

    return -2 * error_mask.astype(int) + (~error_mask).astype(int) * (
        np.exp(var) / (1 + np.exp(var)))


def trafoProbNN(variable_name, event):
    '''
    calculates the transformation of a given variable
    '''
    variable = event.__getattr__(variable_name)

    #Check for problematic ProbNN values
    if variable <= 0.0 or variable >= 1.0:  #-1000 or -2 is the default value when ProbNN could not be read when creating the tuples
        problem_branches[variable_name] = problem_branches.get(
            variable_name, 0) + 1
        return -1000.  #also return -1000

    return np.log(variable / (1 - variable))


def UntrafoProbNN(variable_name, event):
    '''
    calculates the inverse transformation of a given variable
    '''
    variable = event.__getattr__(variable_name)

    #Check for problematic transformed ProbNN values
    if variable < -500:
        return -2.
    else:
        return np.exp(variable) / (1 + np.exp(variable))


if __name__ == '__main__':

    #Read options
    #Create optionparser
    parser = ArgumentParser(
        usage=
        "Tool to transform ProbNN-variables according to log(X_ProbNNY/(1-X_ProbNNY))"
    )

    parser.add_argument(
        "-i",
        "--input",
        dest="Input",
        action="store",
        required=True,
        help="Input ROOT-file")
    parser.add_argument(
        "-t",
        "--tree",
        dest="Tree",
        action="store",
        required=False,
        help=
        "Input TTree (optional if there is only one tree in the input-file)")
    parser.add_argument(
        "-o",
        "--output",
        dest="Output",
        action="store",
        required=True,
        help="Output ROOT-file")
    #parser.add_argument( "--progress", dest="progress", action="store_true", default=False, required=False, help="Show detailed progressbar")
    parser.add_argument(
        "Variables",
        metavar='V',
        type=str,
        nargs='*',
        help="Explicit variable name or variable names to be transformed")
    parser.add_argument(
        "-m",
        "--match",
        dest="Patterns",
        action="append",
        required=False,
        help="Transform all variables matching this pattern")
    parser.add_argument(
        "-r",
        "--reverse",
        dest="Reverse",
        action="store_true",
        help="Perform inverse transformation exp(X_ProbNNY)/(1+exp(X_ProbNNY))"
    )

    #Parse arguments from command line
    options = parser.parse_args()

    #Open tree and clone it
    inputfile = ROOT.TFile(options.Input, "READ")
    if not inputfile.IsOpen():
        raise SystemExit("Could not open inputfile!")

    if options.Tree == None:
        inputtreename = get_any_tree(options.Input)
    else:
        inputtreename = options.Tree

    from root_numpy import list_trees
    trees = list_trees(options.Input)

    # If data was downloaded with grab_data method, you end up with many trees in your file
    if len(trees) > 1:
        inputtree=ROOT.TChain("tree")
        for i in range(1,len(trees)+1):
            filename = options.Input + "/tree;{}".format(i)
            status = inputtree.Add(filename,-1)
            if status == 0:
                break
    else:
        inputtree = inputfile.Get(inputtreename)


    print 'Entries', inputtree.GetEntries()

    outputfile = options.Output

    #Clone tree
    outputfile = ROOT.TFile(options.Output, "RECREATE")
    outputtree = inputtree.CloneTree(0)

    #Get explicit variable names
    variable_names = options.Variables

    #Create new branches for explicit variable names
    variable_trafo_branches = []
    for variable_name in variable_names:
        variable_trafo_branches.append(array.array("d", [0.0]))
        if options.Reverse:
            #If var-name has "Trafo" in it, change it to "Untrafo", otherwise append Untrafo
            if "Trafo" in variable_name:
                outputbranchname = variable_name.replace("Trafo", "Untrafo")
            else:
                outputbranchname = variable_name + "_Untrafo"
            outputtree.Branch(outputbranchname, variable_trafo_branches[-1],
                              outputbranchname + "/D")
        else:
            outputtree.Branch(variable_name + "_Trafo",
                              variable_trafo_branches[-1],
                              variable_name + "_Trafo/D")

    #Get variable names matching the patterns (if applicable)
    if options.Patterns:
        for pattern in options.Patterns:
            for branch in inputtree.GetListOfBranches():
                if pattern in branch.GetName():
                    variable_name = branch.GetName()
                    variable_names.append(variable_name)
                    variable_trafo_branches.append(array.array("d", [0.0]))
                    if options.Reverse:
                        #If var-name has "Trafo" in it, change it to "Untrafo", otherwise append Untrafo
                        if "Trafo" in variable_name:
                            outputbranchname = variable_name.replace(
                                "Trafo", "Untrafo")
                        else:
                            outputbranchname = variable_name + "_Untrafo"
                        outputtree.Branch(outputbranchname,
                                          variable_trafo_branches[-1],
                                          outputbranchname + "/D")
                    else:
                        outputtree.Branch(variable_name + "_Trafo",
                                          variable_trafo_branches[-1],
                                          variable_name + "_Trafo/D")

    if len(variable_names) is 0:
        raise SystemExit("No variables for transformation given/found for {}".
                         format(options.Input))

    # Create dictionary that will contain the branch names, where invalid ProbNN values were encountered (i.e. outside of 0 to 1)
    # and attached to the branch names the number of events there an error occured
    problem_branches = {}

    #Progressbar
    entries = inputtree.GetEntries()
    print("Processing {0} entries in {2} /{1}".format(entries, inputtreename,
                                                      options.Input))
    print("\nThe following variables will be transformed:")
    print(", ".join(variable_names))
    print("\n")

    #widgets = [os.path.basename(options.Output), progressbar.Percentage(), ' ', progressbar.Bar(), ' ', progressbar.ETA()]
    #pbar = progressbar.ProgressBar(widgets=widgets, maxval=entries).start()

    #pbar.update(0)
    #Iterate through tree
    for (i, event) in itertools.izip(xrange(entries), inputtree):
        inputtree.GetEntry(i)

        #iterate through variables
        for (variable_name, variable_trafo_branch) in itertools.izip(
                variable_names, variable_trafo_branches):
            if options.Reverse:
                variable_trafo_branch[0] = UntrafoProbNN(variable_name, event)
            else:
                variable_trafo_branch[0] = trafoProbNN(variable_name, event)

        #Fill tree
        outputtree.Fill()

        #Progressbar
    #    if options.progress:    #detailed progress
    #        pbar.update(i+1)
    #    else:
    #        if (i+1) % (entries/10) == 0:
    #            pbar.update(i+1)

    if problem_branches:
        print(
            "\n\nWARNING: There were events with ProbNN-values outside the allowed region of [0,1] for {}:".
            format(options.Input))
        print("{:<20} {:>15} {:>10}".format('Branch', 'Probl. Events',
                                            'Percent'))
        for branch, events in problem_branches.iteritems():
            print("{:<20} {:>15} {:>10}%".format(
                branch, events, float(events) / entries * 100.))
        print(
            "\t=> Setting these to -1000 (Default value for ProbNN-variables if none was found when creating the ntuple)"
        )

    print("\nFinished processing {0} entries in {2} /{1}\n\t=> Writing to {3}".
          format(entries, inputtreename, options.Input, options.Output))
    outputtree.Write()
    outputfile.Close()
