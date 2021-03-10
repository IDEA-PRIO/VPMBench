from abc import abstractmethod, ABC

from pandas import Series
from sklearn.metrics import roc_auc_score

from vpmbench.data import Score
from vpmbench.summaries import ConfusionMatrix


class PerformanceMetric(ABC):
    """ Represent a metrics."""

    @staticmethod
    @abstractmethod
    def calculate(score: Score, interpreted_classes: Series) -> float:
        return 0.0

    @staticmethod
    @abstractmethod
    def name():
        return None


class Sensitivity(PerformanceMetric):
    @staticmethod
    def calculate(score: Score, interpreted_classes: Series) -> float:
        """ Calculate the sensitivity.

        Uses a :class:`~vpmbench.summaries.ConfusionMatrix` to calculate the sensitivity/true positive rate.

        Parameters
        ----------
        score :
            The score from the plugin
        interpreted_classes :
            The interpreted classes

        Returns
        -------
        float
            The calculated sensitivity
        """
        confusion_matrix = ConfusionMatrix().calculate(score, interpreted_classes)
        return confusion_matrix["tp"] / (confusion_matrix["tp"] + confusion_matrix["fn"])

    @staticmethod
    def name():
        return "Sensitivity"


class Specificity(PerformanceMetric):
    @staticmethod
    def calculate(score: Score, interpreted_classes: Series) -> float:
        """ Calculate the sensitivity.

        Uses a :class:`~vpmbench.summaries.ConfusionMatrix` to calculate the specificity/false positive rate.

        Parameters
        ----------
        score :
            The score from the plugin
        interpreted_classes :
            The interpreted classes

        Returns
        -------
        float
            The calculated specificity
        """
        confusion_matrix = ConfusionMatrix().calculate(score, interpreted_classes)
        return confusion_matrix["tn"] / (confusion_matrix["tn"] + confusion_matrix["fp"])

    @staticmethod
    def name():
        return "Specificity"


class AreaUnderTheCurveROC(PerformanceMetric):
    """ Calculate the area under the roc curve (AUC).

    Parameters
    ----------
    score :
        The score from the plugin
    interpreted_classes :
        The interpreted classes

    Returns
    -------
    float
        The calculated AUC

    """

    @staticmethod
    def calculate(score: Score, interpreted_classes: Series) -> float:
        return roc_auc_score(interpreted_classes, score.data)

    @staticmethod
    def name():
        return "Area under the Curve ROC"
