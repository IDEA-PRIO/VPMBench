import csv
from abc import abstractmethod, ABC
from pathlib import Path
from typing import Union

from vcf import Reader
from vcf.model import _Record

from vpmbench import log
from vpmbench.data import EvaluationDataEntry, EvaluationData
from vpmbench.enums import VariationType, ReferenceGenome


class Extractor(ABC):
    """ Extractors are used to extract the :class:`~vpmbench.data.EvaluationData` from evaluation input files.

    """

    @abstractmethod
    def _extract(self, file_path: str) -> EvaluationData:
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

    def extract(self, file_path: Union[str, Path]) -> EvaluationData:
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
        extraction_path = file_path
        try:
            extraction_path = str(extraction_path.resolve())
        except Exception:
            pass
        try:
            table = self._extract(extraction_path)
        except Exception as ex:
            raise RuntimeError(
                f"Can't parse data at '{file_path}' with '{self.__class__.__name__}'. \nMaybe the data does not exist, or is not "
                f"compatible with the Extractor.\n If the data exists use absolute path.") from ex
        log.debug("Extracted Data:")
        log.debug(table.variant_data.head(10))
        return table


class CSVExtractor(Extractor):
    """ An implementation of a generic extractor for CSV files.

        The implementations uses the Python :class:`~csv.DictReader` to parse a CSV file.
        To extract the :class:`~vpmbench.data.EvaluationData`, the :meth:`~vpmbench.extractor.CSVExtractor._row_to_evaluation_data_entry` is called.
        If a row to entry function is passed as an argument, this function will be used instead of the internal method.


        Parameters
        ----------
        row_to_entry_func
            A function that called for every row in the CSV file to extract a :class:`~vpmbench.data.EvaluationDataEntry`
        kwards
            Arguments that are passed to the CSV parser
    """

    def __init__(self, row_to_entry_func=None, **kwargs):
        super().__init__()
        self.row_to_entry_func = self._row_to_evaluation_data_entry if row_to_entry_func is None else row_to_entry_func
        self.csv_reader_args = kwargs

    def _row_to_evaluation_data_entry(self, data_row: dict) -> EvaluationDataEntry:
        """ Parses a row of a CSV file to an evaluation data entry.

        Parameters
        ----------
        data_row : dict
            A dictionary representing a row of the CSV file

        Returns
        -------
        EvaluationDataEntry
            The evaluation data entry for the row
        """
        raise NotImplementedError()

    def _extract(self, file_path: str) -> EvaluationData:
        records = []
        with open(file_path, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file, **self.csv_reader_args)
            for row in csv_reader:
                records.append(self.row_to_entry_func(row))
        return EvaluationData.from_records(records)


class VariSNPExtractor(CSVExtractor):
    """ An implementation of an for VariSNP files based on :class:`~vpmbench.extractor.CSVExtractor`.
    """

    def __init__(self) -> None:
        super().__init__()
        self.csv_reader_args = {'delimiter': '\t'}

    def _row_to_evaluation_data_entry(self, data_row) -> EvaluationDataEntry:
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
        return EvaluationDataEntry(chrom, pos, ref, alt, "benign", VariationType.SNP,
                                   ReferenceGenome.HG38)


class VCFExtractor(Extractor):
    """ An implementation of a generic extractor for VCF files.

        The implementations uses pyvcf :class:`~vcf.Reader` to parse a VCF file.
        The implementation already extracts POS, CHOM, REF, ALT for each variant.
        To extract the CLASS the internal :meth:`~vpmbench.extractor.VCFExtractor._extract_pathogencity_class_from_record` is called for each VCF entry.
        If a record to pathogenicity class func is passed as an argument, this function will be used instead of the internal method.


        Parameters
        ----------
        record_to_pathogencity_class_func
            A function that returns the pathogenicty class for each entry in the VCF file.
    """

    def __init__(self, record_to_pathogencity_class_func=None) -> None:
        super().__init__()
        self.record_to_pathogencity_class_func = self._extract_pathogencity_class_from_record if record_to_pathogencity_class_func is None else record_to_pathogencity_class_func

    def _extract_pathogencity_class_from_record(self, vcf_record: _Record) -> str:
        """ Extracts the pathogencity class of a vcf record.

        Parameters
        ----------
        vcf_record : vcf.model._Record
            A record of the VCF file

        Returns
        -------
        str
            The pathogenicty class of the variant
        """
        raise NotImplementedError

    def _extract(self, file_path: str) -> EvaluationData:
        records = []
        vcf_reader = Reader(filename=file_path, encoding="latin-1", strict_whitespace=True)
        for vcf_record in vcf_reader:
            chrom = str(vcf_record.CHROM)
            pos = vcf_record.POS
            ref = vcf_record.REF
            alt = (vcf_record.ALT[0] if len(vcf_record.ALT) == 1 else vcf_record.ALT).sequence
            clnsig = self.record_to_pathogencity_class_func(vcf_record)
            variation_type = VariationType(vcf_record.var_type)
            rg = ReferenceGenome.resolve(vcf_reader.metadata["reference"])
            records.append(EvaluationDataEntry(chrom, pos, ref, alt, clnsig, variation_type, rg))
        return EvaluationData.from_records(records)


class ClinVarVCFExtractor(VCFExtractor):
    """ An extractor ClinVAR VCF files based on :class:`~vpmbench.extractor.VCFExtractor`.
    """

    def _extract_pathogencity_class_from_record(self, vcf_record) -> str:
        vcf_clnsig = vcf_record.INFO["CLNSIG"][0].lower()
        if "benign" in vcf_clnsig or "2" in vcf_clnsig:
            return "benign"
        elif "pathogenic" in vcf_clnsig or "5" in vcf_clnsig:
            return "pathogenic"
        else:
            raise RuntimeError(f"Can't extract pathogenicity for: {vcf_clnsig}")
