import numpy as np
from pandas import DataFrame


def entry_point(arg):
    result = DataFrame(arg["UID"])
    result["SCORE"] = np.random.rand(len(result))
    return result
