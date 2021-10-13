import subprocess
from multiprocessing.pool import ThreadPool
from pathlib import Path

from pandas import DataFrame


def row_to_query(row):
    query_string = f"{row['CHROM']}:{row['POS'] + 1}-{row['POS'] + 1}"
    job = {"UID": row["UID"], "REF": row["REF"], "ALT": row["ALT"], "query": query_string}
    return job


def build_queries(variant_data):
    return variant_data.apply(row_to_query, axis=1)


def extract_score(param):
    split = filter(lambda str: str != '.', param.split(";"))
    values = [float(str) for str in split]
    if values == []:
        return None
    else:
        return min(values)

def run_query(tabix_file, query):
    command = f"tabix \"{tabix_file}\" {query['query']} 2>/dev/null"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    data, err = proc.communicate()
    score = None
    for record in data.decode().split("\n"):
        if not record:
            continue
        record = record.strip().split("\t")
        if record[2] == query['REF'] and record[3] == query['ALT']:
            score = extract_score(record[36])
            break
    result = {'UID': query['UID'], 'SCORE': score} if score is not None else {}
    return result


def entry_point(variant_data: DataFrame):
    entry_point_directory = Path(__file__).parent
    tabix_file = (entry_point_directory / "../dbNSFP4.1a.txt.gz").resolve()
    if not tabix_file.exists():
        raise RuntimeError(f"Can't find {tabix_file.name} for Sift (dbnsfp).")
    queries = build_queries(variant_data)
    with ThreadPool(processes=10) as pool:
        jobs = [pool.apply_async(run_query, (tabix_file, query,)) for query in queries]
        pool.close()
        pool.join()
        results = [job.get() for job in jobs]
    df = DataFrame(results)
    return df
