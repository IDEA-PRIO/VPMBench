from pandas import DataFrame


def entry_point(arg):
    result = DataFrame(arg["UID"])
    result["SCORE"] = 0
    return result
