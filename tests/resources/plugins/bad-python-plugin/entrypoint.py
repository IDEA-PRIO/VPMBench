import numpy as np
from pandas import DataFrame


def entry_point(arg):
    result = DataFrame(arg["UID"])
    result["SCORE"] = np.random.choice([None, np.nan, 0.5], len(result))
    return result
