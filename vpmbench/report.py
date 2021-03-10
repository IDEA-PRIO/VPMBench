from typing import List

from pandas import DataFrame

from vpmbench.data import EvaluationData, AnnotatedVariantData, Score
from vpmbench.enums import PathogencityClass


class PerformanceReport:
    """ Represent a collection of the results of running the pipeline.
    """

    def __init__(self, evaluation_data: EvaluationData, annotated_variants: AnnotatedVariantData, reports) -> None:
        self.data: DataFrame = annotated_variants.annotated_variant_data.merge(
            evaluation_data.table[["UID", "CLASS"]],
            on="UID")
        self.metrics_and_summaries = reports
        self.plugins = annotated_variants.plugins

    @property
    def interpreted_classes(self):
        """ Interpret the CLASS data.

        The CLASS data is interpreted by applying :meth:`vpmbench.enums.PathogencityClass.interpret`.

        Returns
        -------
        :class:`pandas.Series`
            A series of interpreted classes
        """
        return self.data["CLASS"].apply(PathogencityClass.interpret)

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
            series = self.data[column_name]
            scores.append(Score(plugin, series))
        return scores
