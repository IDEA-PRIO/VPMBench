import re
from dataclasses import dataclass
from typing import List, Tuple

from pandas import DataFrame
from pandera import DataFrameSchema, Column, Int, Check, String

from vpmbench.enums import PathogencityClass, VariationType, ReferenceGenome
from vpmbench.plugin import Score


@dataclass
class EvaluationDataEntry:
    """ Represent an entry in the :class:`vpmbench.data.EvaluationData` table.

    Parameters
    ----------
    CHROM
        The chromosome in which the variant is found
    POS
        The 1-based position of the variant within the chromosome
    REF
        The reference bases
    ALT
        The alternative bases
    CLASS
        The expected classification of the variant
    TYPE
        The variation type of the variant
    RG
        The reference genome is used to call the variant
    """
    CHROM: str
    POS: int
    REF: str
    ALT: str
    CLASS: PathogencityClass
    TYPE: VariationType
    RG: ReferenceGenome


@dataclass
class EvaluationData:
    """ Represent the evaluation data.

    The evaluation data contains all the information about the variants required to use the data to evaluate the performance
    of the prioritization methods.

    The data of the following information for the variants:

        * UID: A numerical identifier allowing to reference the variant
        * CHROM: The chromosome in which the variant is found
        * POS: The 1-based position of the variant within the chromosome
        * REF: The reference bases.
        * ALT: The alternative bases.
        * RG: The reference genome is used to call the variant
        * TYPE: The variation type of the variant
        * CLASS: The expected classification of the variant

    Parameters
    ----------
    table: pandas.DataFrame
        The dataframe containing the required information about the variants.
    """
    table: DataFrame

    @staticmethod
    def from_records(records: List[EvaluationDataEntry]) -> 'EvaluationData':
        """ Create a evaluation data table data from list of records.

        This method also automatically assigns each record an UID.

        Parameters
        ----------
        records : List[EvaluationDataEntry]
            The records that should be included in the table.

        Returns
        -------
        EvaluationData
            The resulting evaluation data

        """
        table = DataFrame(records)
        table["UID"] = range(0, len(table))
        return EvaluationData(table)

    def validate(self):
        """ Check if the evaluation data is valid.

        The following constraints are checked:

            * CHROM has to be in ``{"1",...,"22","X","Y"}``
            * POS has to be ``> 1``
            * REF has to match with ``re.compile("^[ACGT]+$")``
            * ALT has to match with ``re.compile("^[ACGT]+$")``
            * RG has to be of type :class:`vpmbench.enums.ReferenceGenome`
            * CLASS has to be of type :class:`vpmbench.enums.PathogencityClass`
            * TYPE has to be of type :class:`vpmbench.enums.VariationType`
            * UID has to be ``> 0``

        Raises
        ------
        :class:`~pandera.errors.SchemaErrors`
            If the validation of the data fails
        """
        chroms = set([str(x) for x in range(1, 23)] + ["X", "Y", "MT"])
        ref_validator = re.compile("^[ACGT]+$")
        alt_validator = re.compile("^[ACGTN]+$")
        schema = DataFrameSchema({
            "CHROM": Column(String, Check(lambda chrom: chrom in chroms, element_wise=True), required=True),
            "POS": Column(Int, Check(lambda pos: pos >= 1), required=True),
            "REF": Column(String, Check(lambda ref: ref_validator.match(ref) is not None, element_wise=True),
                          required=True),
            "ALT": Column(String, Check(lambda alt: alt_validator.match(alt) is not None, element_wise=True),
                          required=True),
            "CLASS": Column(checks=Check(lambda cl: isinstance(cl, PathogencityClass), element_wise=True),
                            required=True),
            "UID": Column(Int, Check(lambda x: x >= 0), required=True),
            "TYPE": Column(checks=Check(lambda cl: isinstance(cl, VariationType), element_wise=True),
                           required=True),
            "RG": Column(checks=Check(lambda cl: isinstance(cl, ReferenceGenome), element_wise=True),
                         required=True)})
        schema.validate(self.table, lazy=True)

    @property
    def variant_data(self) -> DataFrame:
        """ Get the pure variant data from the evaluation data.

        The variant data consists of the data in columns: UID,CHROM,POS,REF,ALT,RG,TYPE

        Returns
        -------
        DataFrame
            The variant data from the evaluation data.
        """
        return self.table[["UID", "CHROM", "POS", "REF", "ALT", "RG", "TYPE"]].copy()

    @property
    def interpreted_classes(self):
        """ Interpret the CLASS data.

        The CLASS data is interpreted by applying :meth:`vpmbench.enums.PathogencityClass.interpret`.

        Returns
        -------
        :class:`pandas.Series`
            A series of interpreted classes
        """
        return self.table["CLASS"].apply(PathogencityClass.interpret)


@dataclass
class AnnotatedVariantData:
    """ Represent the variant data annotated with the scores from the prioritization methods.

    Contains the same information as the :meth:`vpmbench.data.EvaluationData.variant_data` and the scores from the methods.

    Arguments
    ---------
    annotated_variant_data
        The variant data with the annotated scores
    plugins
        The plugins used to calculate the scores
    """
    annotated_variant_data: DataFrame
    plugins: List['Plugin']

    @staticmethod
    def from_results(original_variant_data: DataFrame,
                     plugin_results: List[Tuple['Plugin', DataFrame]]) -> 'AnnotatedVariantData':
        """ Create annotated variant data from the original variant data and plugin results.

        The annotated variant data is created by merging the plugin scores on the UID column.

        Parameters
        ----------
        original_variant_data
            The original variant data used to calculate the scores
        plugin_results
            The results from :func:`invoking <vpmbench.api.invoke_method>` the prioritization methods

        Returns
        -------
        AnnotatedVariantData
            The variant data annotated with the scores
        """

        plugins = []
        for (plugin, plugin_scores) in plugin_results:
            plugins.append(plugin)
            original_variant_data = original_variant_data.merge(plugin_scores, on="UID")
        return AnnotatedVariantData(original_variant_data, plugins)

    @property
    def scores(self) -> List[Score]:
        """ Return the list of scores from the annotated variant data

        Returns
        -------
        List[Score]
            The list of scores.
        """
        scores = []
        for plugin in self.plugins:
            column_name = plugin.score_column_name
            series = self.annotated_variant_data[column_name]
            scores.append(Score(plugin, series))
        return scores
