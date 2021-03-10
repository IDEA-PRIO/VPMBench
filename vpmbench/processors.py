import pandas
from pandas import DataFrame


class Registry:
    def __init__(self) -> None:
        super().__init__()
        self.funcs = {}

    def register(self, format_name: str):
        def decorator(f):
            self.funcs[format_name] = f
            return f

        return decorator

    def get(self, format_name: str):
        return self.funcs[format_name]


input_registry = Registry()
output_registry = Registry()


def format_input(variant_information_table: DataFrame, target_format: str, target_file: str, **kwargs):
    """ Formats the variant information table into the target format and write the results to target file.

    Parameters
    ----------
    variant_information_table :
        The input table
    target_format :
        The format in which data should be written
    target_file :
        The file in which the data should be written
    kwargs :
        Additional arguments that are passed to the converter function


    """
    f = input_registry.get(target_format)
    f(variant_information_table, target_file, **kwargs)


def format_output(variant_information_table: DataFrame, output_format: str, output_file: str, **kwargs) -> DataFrame:
    """ Formats the content of the output file into a dataframe.

    Parameters
    ----------
    variant_information_table :
        The variant information table used to calculate the results in the output file
    output_format :
        The format of the output file
    output_file :
        The file from which the output should be read
    kwargs :
        Additional arguments

    Returns
    -------
    DataFrame
        The formatted content of the output file

    """
    f = output_registry.get(output_format)
    return f(variant_information_table, output_file, **kwargs)


@input_registry.register("CSV")
def to_csv(variant_information_table: DataFrame, file, separator=",", header=True, columns=None, **kwargs):
    if columns is None:
        columns = ["CHROM", "POS", "REF", "ALT"]
    table = variant_information_table[columns]
    table.to_csv(file, index=False, sep=separator, header=header)


@input_registry.register("VCF")
def to_vcf(table: DataFrame, file: str, **kwargs):
    vcf_data_collection = DataFrame()
    vcf_data_collection["CHROM"] = table["CHROM"]
    vcf_data_collection["REF"] = table["REF"]
    vcf_data_collection["ALT"] = table["ALT"]
    vcf_data_collection["POS"] = table["POS"]
    vcf_data_collection["ID"] = "."
    vcf_data_collection['QUAL'] = 40
    vcf_data_collection['FILTER'] = ""
    vcf_data_collection['INFO'] = ""
    vcf_table = vcf_data_collection[['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO']]
    header = "##fileformat=VCFv4.1 \n #CHROM POS ID REF ALT QUAL FILTER INFO"
    with open(file, "w") as vcf_file:
        vcf_file.write(header)
    vcf_table.to_csv(file, sep="\t", mode='a', index=False)


@output_registry.register("CSV")
def from_csv(variant_information_table: DataFrame, file: str, merge_on=None, **kwargs):
    if merge_on is None:
        merge_on = ["CHROM", "POS", "REF", "ALT"]
    score_table = pandas.read_csv(file)
    if merge_on:
        score_table["CHROM"] = score_table["CHROM"].astype(str)
        score_table = variant_information_table.merge(score_table, on=merge_on)
    return score_table[["UID", "SCORE"]]
