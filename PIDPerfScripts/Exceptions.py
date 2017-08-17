# THIS FILE IS COPIED FROM THE PIDCalib package from the LHCbSoftware stack

import exceptions

class GetEnvError(exceptions.Exception):
    pass

class TFileError(exceptions.Exception):
    pass

class RooWorkspaceError(exceptions.Exception):
    pass

class RooDataSetError(exceptions.Exception):
    pass
