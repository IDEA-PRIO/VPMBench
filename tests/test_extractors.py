import pytest

from vpmbench.extractor import ClinVarVCFExtractor, VariSNPExtractor


def test_VCFExtractor_grch37(grch37_vcf_path):
    evaluation_data_table = ClinVarVCFExtractor.extract(grch37_vcf_path)
    assert evaluation_data_table is not None


def test_VCFExtractor_grch38(grch38_vcf_path):
    evaluation_data_table = ClinVarVCFExtractor.extract(grch38_vcf_path)
    assert evaluation_data_table is not None


def test_Extractor_invalid_data():
    with pytest.raises(Exception) as e:
        ClinVarVCFExtractor.extract("this/path/does/not/exists")
    assert "ClinVarVCFExtractor" in e.value.args[0]

def test_VariSNPExtractor(varisnp_path):
    evaluation_data_table = VariSNPExtractor.extract(varisnp_path)
    assert evaluation_data_table is not None