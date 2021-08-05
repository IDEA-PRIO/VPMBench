import numpy as np
from pandas import DataFrame


def entry_point(arg):
    result = DataFrame(arg["UID"])
    result["SCORE"] = 0.5
    return result
