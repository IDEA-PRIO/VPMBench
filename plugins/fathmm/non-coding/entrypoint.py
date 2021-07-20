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


def run_query(tabix_file, query):
    command = f"tabix {tabix_file} {query['query']}"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    data, err = proc.communicate()
    score = -1
    for record in data.decode().split("\n"):
        if not record:
            continue
        record = record.strip().split("\t")
        if record[4] == query['ALT']:
            score = float(record[5])
            break
    result = {'UID': query['UID'], 'SCORE': score}
    return result


def entry_point(variant_data: DataFrame):
    entry_point_directory = Path(__file__).parent
    tabix_file = (entry_point_directory / "../fathmm-MKL_Current.tab.gz").resolve()
    if not tabix_file.exists():
        raise RuntimeError(f"Can't find {tabix_file.name} for fathmm-MKL.")
    queries = build_queries(variant_data)
    with ThreadPool(processes=10) as pool:
        jobs = [pool.apply_async(run_query, (tabix_file, query,)) for query in queries]
        pool.close()
        pool.join()
        results = [job.get() for job in jobs]
    df = DataFrame(results)
    return df
