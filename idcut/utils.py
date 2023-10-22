from json import JSONEncoder
import numpy

class NumpyDatatypesEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        if isinstance(obj, numpy.int64):
            return int(obj)
        return JSONEncoder.default(self, obj)