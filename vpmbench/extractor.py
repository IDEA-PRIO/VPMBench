import csv
from abc import abstractmethod, ABC
from pathlib import Path
from typing import Union

from vcf import Reader

from vpmbench import log
from vpmbench.data import EvaluationDataEntry, EvaluationData
from vpmbench.enums import PathogencityClass, VariationType, ReferenceGenome


class Extractor(ABC):
    """ Extractors are used to extract the :class:`~vpmbench.data.EvaluationData` from evaluation input files.

    """

    @classmethod
    @abstractmethod
    def _extract(cls, file_path: Union[str, Path]) -> EvaluationData:
        """ Internal function to extract the evaluation data from the evaluation input file at `file-path`.

        This function has to be implemented for every extractor.

        Parameters
        ----------
        file_path
            The file path to evaluation input data

        Returns
        -------
        EvaluationData
            The evaluation data
        """
        raise NotImplementedError

    @classmethod
    def extract(cls, file_path: Union[str, Path]) -> EvaluationData:
        """ Extract the :class:`~vpmbench.data.EvaluationData` from the file at `file_path`.

        This function calls :meth:`~vpmbench.extractor.Extractor._extract` and uses
        :meth:`vpmbench.data.EvaluationData.validate` to check if the evaluation data is valid.

        Parameters
        ----------
        file_path
            The file path to evaluation input data


        Returns
        -------
        EvaluationData
            The validated evaluation data

        Raises
        ------
        RuntimeError
            If the file can not be parsed

        SchemaErrors
            If the validation of the extracted data fails

        """
        try:
            table = cls._extract(file_path)
        except Exception:
            raise RuntimeError(
                f"Can't parse data at '{file_path}' with '{cls.__name__}'. \nMaybe the data does not exist, or is not "
                f"compatible with the Extractor.\n If the data exists use absolute path.")
        log.debug("Extracted Data:")
        log.debug(table.variant_data.head(10))
        table.validate()
        return table


class ClinVarVCFExtractor(Extractor):
    """ An implementation of an :class:`~vpmbench.extractor.Extractor` for ClinVarVCF files.
    """

    @classmethod
    def _extract(cls, file_path: Union[str, Path]) -> EvaluationData:
        records = []
        vcf_reader = Reader(open(file_path, "r"),encoding="latin-1", strict_whitespace=True)
        for vcf_record in vcf_reader:
            chrom = str(vcf_record.CHROM)
            pos = vcf_record.POS
            ref = vcf_record.REF
            alt = (vcf_record.ALT[0] if len(vcf_record.ALT) == 1 else vcf_record.ALT).sequence
            vcf_clnsig = vcf_record.INFO["CLNSIG"][0].lower()
            clnsig = PathogencityClass.resolve(vcf_clnsig)
            variation_type = VariationType(vcf_record.var_type)
            rg = ReferenceGenome.resolve(vcf_reader.metadata["reference"])
            records.append(EvaluationDataEntry(chrom, pos, ref, alt, clnsig, variation_type, rg))
        return EvaluationData.from_records(records)

class VariSNPExtractor(Extractor):
    """ An implementation of an :class:`~vpmbench.extractor.Extractor` for VariSNP files.
    """

    @classmethod
    def _build_entry(cls, data_row) -> EvaluationDataEntry:
        hgvs_name = data_row['hgvs_names'].split(";")[0]
        chrom_number = int(hgvs_name.split(":")[0][3:9])
        chrom = None
        if chrom_number <= 22:
            chrom = str(chrom_number)
        elif chrom_number == 23:
            chrom = "X"
        elif chrom_number == 24:
            chrom = "Y"
        pos = int(data_row['asn_to']) + 1
        alt = data_row['minor_allele']
        ref = data_row['reference_allele']
        return EvaluationDataEntry(chrom, pos, ref, alt, PathogencityClass.BENIGN, VariationType.SNP,
                                   ReferenceGenome.HG38)

    @classmethod
    def _extract(cls, file_path: Union[str, Path]) -> EvaluationData:
        records = []
        with open(file_path, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file,delimiter="\t")
            for row in csv_reader:
                records.append(cls._build_entry(row))
        return EvaluationData.from_records(records)
