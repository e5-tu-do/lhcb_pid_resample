import re
import math

from PIDPerfScripts.Exceptions import *

def DataSetVariables(var=None):
    h = {
        'Charge': 'Charge',
        'nTracks': 'nTracks',
        'runNumber': 'runNumber',
        'nPVs' : 'nPVs',
        'DLLK': '{particle}_CombDLLK',
        'DLLp': '{particle}_CombDLLp',
        'DLLe': '{particle}_CombDLLe',
        'DLLmu': '{particle}_CombDLLmu',
        'Tesla_DLLK': '{particle}_Tesla_CombDLLK',
        'Tesla_DLLp': '{particle}_Tesla_CombDLLp',
        'Tesla_DLLe': '{particle}_Tesla_CombDLLe',
        'Tesla_DLLmu': '{particle}_Tesla_CombDLLmu',
#        'ProbNNK': '{particle}_ProbNNK',
#        'ProbNNpi': '{particle}_ProbNNpi',
#        'ProbNNp': '{particle}_ProbNNp',
#        'ProbNNmu': '{particle}_ProbNNmu',
#        'ProbNNe': '{particle}_ProbNNe',
        'V2ProbNNK': '{particle}_V2ProbNNK',
        'V2ProbNNpi': '{particle}_V2ProbNNpi',
        'V2ProbNNp': '{particle}_V2ProbNNp',
        'V2ProbNNmu': '{particle}_V2ProbNNmu',
        'V2ProbNNe': '{particle}_V2ProbNNe',
        'V2ProbNNghost': '{particle}_V2ProbNNghost',
        'V3ProbNNK': '{particle}_V3ProbNNK',
        'V3ProbNNpi': '{particle}_V3ProbNNpi',
        'V3ProbNNp': '{particle}_V3ProbNNp',
        'V3ProbNNmu': '{particle}_V3ProbNNmu',
        'V3ProbNNe': '{particle}_V3ProbNNe',
        'V3ProbNNghost': '{particle}_V3ProbNNghost',
        'trackcharge': '{particle}_trackcharge',
        'P': '{particle}_P',
        'PT': '{particle}_PT',
        'ETA': '{particle}_Eta',
        'PHI': '{particle}_Phi',
        'Tesla_P': '{particle}_Tesla_P',
        'Tesla_PT': '{particle}_Tesla_PT',
        'Tesla_ETA': '{particle}_Tesla_Eta',
        'Tesla_PHI': '{particle}_Tesla_Phi',
        'IsMuon': '{particle}_IsMuon',
        'InMuonAcc': '{particle}_InMuonAcc',
        'IsMuonLoose': '{particle}_IsMuonLoose',
        'IsMuonTight': '{particle}_IsMuonTight',
        'nShared': '{particle}_nShared',
        'RICHThreshold_pi': '{particle}_RICHThreshold_pi',
        'RICHThreshold_p': '{particle}_RICHThreshold_p',
        'RICHThreshold_e': '{particle}_RICHThreshold_e',
        'RICHThreshold_K': '{particle}_RICHThreshold_K',
        'RICHThreshold_e': '{particle}_RICHThreshold_e',
        'RICHAerogelUsed': '{particle}_RICHAerogelUsed',
        'RICH1GasUsed': '{particle}_RICH1GasUsed',
        'RICH2GasUsed': '{particle}_RICH2GasUsed',
        'HasRich': '{particle}_hasRich',
        'HasCalo': '{particle}_hasCalo',
        'HasBremAdded': '{particle}_HasBremAdded',
        'CaloRegion': '{particle}_CaloRegion',
        'nSPDHits': 'nSPDHits',
        'nRich1Hits':'nRich1Hits',
        'nRich2Hits':'nRich2Hits',
        'Unbias_HLT1': '{particle}_Unbias_HLT1',
        'Unbias_HLT12': '{particle}_Unbias_HLT12',
        'ProbeTIS': '{particle}_Probe_TIS',
        'TagTOS': '{particle}_Tag_TOS',

    }
    if var == None:
        return h
    else:
        return h[var]

def NtupleVariables(var=None):
    h = {
        'Charge': 'Charge',
        'nTracks': 'nTracks',
        'runNumber': 'runNumber',
        'nPVs': 'nPVs',
        'Tesla_DLLK': '{particle}_PIDK',
        'Tesla_DLLp': '{particle}_PIDp',
        'Tesla_DLLe': '{particle}_PIDe',
        'Tesla_DLLmu': '{particle}_PIDmu',
        'DLLpK': '{particle}_DLLpK',
        'DLLK': '{particle}_Brunel_PIDK',
        'DLLp': '{particle}_Brunel_PIDp',
        'DLLe': '{particle}_Brunel_PIDe',
        'DLLmu': '{particle}_Brunel_PIDmu',
 #       'ProbNNK': '{particle}_ProbNNK',
 #       'ProbNNpi': '{particle}_ProbNNpi',
 #       'ProbNNp': '{particle}_ProbNNp',
 #       'ProbNNmu': '{particle}_ProbNNmu',
 #       'ProbNNe': '{particle}_ProbNNe',
        'V2ProbNNK': '{particle}_V2ProbNNK',
        'V2ProbNNpi': '{particle}_V2ProbNNpi',
        'V2ProbNNp': '{particle}_V2ProbNNp',
        'V2ProbNNmu': '{particle}_V2ProbNNmu',
        'V2ProbNNe': '{particle}_V2ProbNNe',
        'V2ProbNNghost': '{particle}_V2ProbNNghost',
        'V3ProbNNK': '{particle}_V3ProbNNK',
        'V3ProbNNpi': '{particle}_V3ProbNNpi',
        'V3ProbNNp': '{particle}_V3ProbNNp',
        'V3ProbNNmu': '{particle}_V3ProbNNmu',
        'V3ProbNNe': '{particle}_V3ProbNNe',
        'V3ProbNNghost': '{particle}_V3ProbNNghost',
        'trackcharge': '{particle}_trackcharge',
        'P': '{particle}_Brunel_P',
        'PT': '{particle}_Brunel_PT',
        'ETA': '{particle}_Brunel_TRACK_Eta',
        'PHI': '{particle}_Brunel_Phi',
        'Tesla_P': '{particle}_P',
        'Tesla_PT': '{particle}_PT',
        'Tesla_ETA': '{particle}_TRACK_Eta',
        'Tesla_PHI': '{particle}_Phi',
        'IsMuon': '{particle}_IsMuon',
        'InMuonAcc': '{particle}_InMuonAcc',
        'IsMuonLoose': '{particle}_IsMuonLoose',
        'IsMuonTight': '{particle}_IsMuonTight',
        'nShared': '{particle}_nShared',
        'RICHThreshold_pi': '{particle}_RICHThreshold_pi',
        'RICHThreshold_p': '{particle}_RICHThreshold_p',
        'RICHThreshold_e': '{particle}_RICHThreshold_e',
        'RICHThreshold_K': '{particle}_RICHThreshold_K',
        'RICHThreshold_e': '{particle}_RICHThreshold_e',
        'RICHAerogelUsed': '{particle}_RICHAerogelUsed',
        'RICH1GasUsed': '{particle}_RICH1GasUsed',
        'RICH2GasUsed': '{particle}_RICH2GasUsed',
        'HasRich': '{particle}_hasRich',
        'HasCalo': '{particle}_hasCalo',
        'HasBremAdded': '{particle}_HasBremAdded',
        'CaloRegion': '{particle}_CaloRegion',
        'nSPDHits': 'nSPDHits',
        'Unbias_HLT1': '{particle}_UT1_MuonTisTagged',
        'Unbias_HLT12': '{particle}_UT2_MuonTisTagged',
    }
    if var == None:
        return h
    else:
        return h[var]

def GetVarNames():
    varArr = [varName for varName, varNameInDataset in DataSetVariables().iteritems()]
    varArr.sort()
    return varArr

def GetRICHPIDRealPartTypes():
    return ("K", "Pi", "P", "e")

def GetRICHPIDPartTypes():
    return GetRICHPIDRealPartTypes()+GetProtonPIDPartTypes()

def GetMuonPIDRealPartTypes():
    return ("Mu",)

def GetProtonPIDPartTypes():
    return ("P_LcfB", "P_IncLc", "P_TotLc")

def GetProtonPIDRealPartTypes():
    return ("P",)

def GetMuonPIDPartTypes():
    return GetMuonPIDRealPartTypes()+tuple(['{0}_MuonUnBiased'.format(
        p) for p in GetRICHPIDRealPartTypes()])

def GetRealPartTypes():
    return GetRICHPIDRealPartTypes()+GetMuonPIDRealPartTypes()

def GetPartTypes():
    return GetRICHPIDPartTypes()+GetMuonPIDPartTypes()


def GetRealPartType(PartName):
    CheckPartType(PartName)
    if PartName == 'K' or PartName == 'K_MuonUnBiased':
        return 'K'
    elif PartName == 'Pi' or PartName == 'Pi_MuonUnBiased':
        return 'Pi'
    elif PartName == 'P' or PartName == 'P_MuonUnBiased' or PartName == 'P_LcfB' or PartName == 'P_IncLc' or PartName == 'P_TotLc':
        return 'P'
    elif PartName == 'e' or PartName == 'e_MuonUnBiased':
        return 'e'
    else:
        return 'Mu'

# N.B. The following method will need to be changed once the
# Lambda_c proton samples are included
def GetMotherName(PartName):
    #PartType = GetRealPartType(PartName)
    if PartName == 'K' or PartName == 'Pi':
        return 'DSt'
    elif PartName == 'P':
        return 'Lam0'
    elif PartName == 'e':
        return 'Jpsi'
    if PartName == 'K_MuonUnBiased' or PartName == 'Pi_MuonUnBiased':
        return 'DSt_MuonUnBiased'
    elif PartName == 'P_MuonUnBiased':
        return 'Lam0_MuonUnBiased'
    elif PartName == 'e_MuonUnBiased':
        return 'Jpsi'
    elif PartName == 'P_LcfB':
        return 'LcfB'
    elif PartName == 'P_TotLc':
        return 'TotLc'
    elif PartName == 'P_IncLc':
        return 'IncLc'
    else:
        return 'Jpsi'

# N.B. The following method will need to be changed once the
# Lambda_c proton samples are included - its going to come from the mother but not for electrons and muons as the are both from jpsis
def GetWorkspaceName(PartName):
    PartType = GetRealPartType(PartName)
    MType = GetMotherName(PartName)
    if MType == 'DSt' or MType == 'Dst_MuonUnBiased':
        return 'RSDStCalib'
    elif MType == 'Lam0' or MType == 'Lam0_MuonUnBiased':
        return 'Lam0Calib'
    elif PartType == 'e':
        return 'JpsieeCalib'
    elif MType == 'LcfB':
        return 'IncLcCalib'
    elif MType == 'TotLc':
        return 'IncLcCalib'
    elif MType == 'IncLc':
        return 'IncLcCalib'
    else:
        return 'JpsiCalib'

def IsMuonUnBiased(PartName):
    CheckPartType(PartName)
    if PartName in GetMuonPIDPartTypes():
        return True
    else:
        return False

def GetRecoVer(StripVer):
    CheckStripVer(StripVer)
    if StripVer=='13b':
        return 10
    elif StripVer=='15':
        return 11
    elif StripVer=='17':
        return 12
    elif StripVer=='22':
        return '15a'
    elif StripVer=='23Val':
        return '15a'
    elif StripVer=='23':
        return '15a'
    elif StripVer=='5TeV':
        return '15a'
    else:
        return 14

def GetFileSuffix(PartName): # think this fuction is defunct. makes no sense anyway.
    CheckPartType(PartName)
    if PartName in ("K", "Pi", "P"):
        return "h"
    if PartName in ("Mu",  "P_MuonUnBiased"):
        return "mu_and_p_muonUnBiased"
    else:
        return "h_muonUnBiased"

def GetKnownFunctions():
    ret = dir(math)
    ret += ["abs","fabs"]
    return ret

def CheckCutVarsInTree(cuts,tree):
    if cuts in [None, ""]:
        return True
    math_chars = re.compile("\\s*([-=|&\\(\\)\\+\\*/<>\\[\\]!\\s]+)\\s*")
    split_cuts = re.split(math_chars,cuts)
    #print "CheckCutVarsInTree():", split_cuts
    for var in split_cuts:
        found = False
        if re.match(math_chars,var):
            #print var,"is mathematical"
            continue
        elif var in GetKnownFunctions():
            #print var,"is a function"
            continue
        else:
            try:
                float(var)
                #print var,"is a number"
                continue
            except ValueError:
                pass
            #print var,"is not mathematical or a function"
            tree_vars = tree.GetListOfLeaves()
            for i in xrange(len(tree_vars)):
                if tree_vars[i].GetName() == var:
                    #print var,"==",tree_vars[i].GetName()
                    found = True
                    break
        if not found:
            raise ValueError("Variable '%s' in cut string '%s' not found in TTree %s!"%(var,cuts,tree.GetName()))
            return False
    #print "Everything is bon!"
    return True


def CheckCuts(cuts,triggers=[]):
    simple_cuts = cuts
    for i in "()[]&!|><=:+-*/":
        simple_cuts = simple_cuts.replace(i," ")

    simple_cuts = [x for x in simple_cuts.split(" ") if x!=""]
    valid_varibles = [x for x,y in DataSetVariables().iteritems()]

    for t in triggers:
        for suffix in ["","_Dec","_TIS","_TOS"]:
            valid_varibles.append(t+suffix)

    valid_varibles.sort()

    for var in simple_cuts:
        try:
            float(var)
        except ValueError:
            if var not in valid_varibles:
                print "'%s' is not a valid variable"%var
                print "Known variables are:"
                print valid_varibles
                print triggers
                return False
    return True

def FlatternPlots(Plots):
    ret = []
    if isinstance(Plots,list):
       for plot in Plots:
          ret.extend(FlatternPlots(plot))
    else:
        return [Plots]
    return ret

def CheckRealPartType(PartName):
    ValidPartNames=GetRealPartTypes()
    if PartName not in ValidPartNames:
        msg=("Invalid particle type '{0}'. "
             "Allowed types are {1}").format(
            PartName, str(ValidPartNames))
        raise TypeError(msg)

def CheckPartType(PartName):
    ValidPartNames=GetPartTypes()
    if PartName not in ValidPartNames:
        msg=("Invalid particle type '{0}'. "
             "Allowed types are {1}").format(
            PartName, str(ValidPartNames))
        raise TypeError(msg)

def CheckMagPol(MagPol):
    ValidMagPols=("MagUp", "MagDown")
    if MagPol not in ValidMagPols:
        msg=("Invalid magnet polarity '{0}'. "
        "Allowed polarities are {1}").format(MagPol, str(ValidMagPols))
        raise TypeError(msg)

def CheckStripVer(StripVer):
    ValidStripVers=("13b", "15", "17", "20", "20r1", "20_MCTuneV2",
         "20r1_MCTuneV2","20_MCTunev3", "21r1","21","22", "23Val","23","5TeV")
    if StripVer not in ValidStripVers:
        msg=("Invalid stripping version '{0}'. "
             "Allowed versions are {1}").format(StripVer, str(ValidStripVers))
        raise TypeError(msg)

def CheckVarName(VarName):
    ValidVarNames=GetVarNames()
    if VarName not in ValidVarNames:
        msg=("Invalid binning variable '{0}'. "
             "Allowed variables are {1}").format(VarName, str(ValidVarNames))
        raise TypeError(msg)




