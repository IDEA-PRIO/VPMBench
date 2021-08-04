import pytest

from vpmbench.data import EvaluationDataEntry
from vpmbench.enums import PathogencityClass, ReferenceGenome, VariationType
from vpmbench.extractor import ClinVarVCFExtractor, VariSNPExtractor, CSVExtractor


def test_VCFExtractor_grch37(grch37_vcf_path):
    extractor = ClinVarVCFExtractor()
    evaluation_data_table = extractor.extract(grch37_vcf_path)
    assert evaluation_data_table is not None


def test_VCFExtractor_grch38(grch38_vcf_path):
    extractor = ClinVarVCFExtractor()
    evaluation_data_table = extractor.extract(grch38_vcf_path)
    assert evaluation_data_table is not None


def test_Extractor_invalid_data():
    with pytest.raises(Exception) as e:
        ClinVarVCFExtractor().extract("this/path/does/not/exists")
    assert "ClinVarVCFExtractor" in e.value.args[0]


def test_VariSNPExtractor(varisnp_path):
    evaluation_data_table = VariSNPExtractor().extract(varisnp_path)
    assert evaluation_data_table is not None


def test_VCFExtractor_String_And_Path(grch37_vcf_path):
    assert ClinVarVCFExtractor().extract(grch37_vcf_path) is not None
    grch37_vcf_path_str = str(grch37_vcf_path)
    assert ClinVarVCFExtractor().extract(grch37_vcf_path_str) is not None


def test_CustomCSVExtractor(custom_varisnp_path):
    def custom_row_to_entry(row):
        hgvs_name = row['hgvs_names'].split(";")[0]
        chrom_number = int(hgvs_name.split(":")[0][3:9])
        chrom = None
        if chrom_number <= 22:
            chrom = str(chrom_number)
        elif chrom_number == 23:
            chrom = "X"
        elif chrom_number == 24:
            chrom = "Y"
        pos = int(row['asn_to']) + 1
        alt = row['minor_allele']
        ref = row['reference_allele']
        return EvaluationDataEntry(chrom, pos, ref, alt, PathogencityClass.BENIGN, VariationType.SNP,
                                   ReferenceGenome.HG38)

    extractor = CSVExtractor(row_to_entry_func=custom_row_to_entry, delimiter=",")
    assert extractor.extract(custom_varisnp_path)
