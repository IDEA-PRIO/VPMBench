from abc import abstractmethod, ABC

from pandas import Series
from sklearn.metrics import roc_auc_score, matthews_corrcoef

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


class Accuracy(PerformanceMetric):
    @staticmethod
    def calculate(score: Score, interpreted_classes: Series) -> float:
        """ Calculate the accuracy.

        Uses a :class:`~vpmbench.summaries.ConfusionMatrix` to calculate the accuracy/true positive rate.

        Parameters
        ----------
        score :
            The score from the plugin
        interpreted_classes :
            The interpreted classes

        Returns
        -------
        float
            The calculated accuracy
        """
        confusion_matrix = ConfusionMatrix().calculate(score, interpreted_classes)
        return (confusion_matrix["tp"] + confusion_matrix["tn"]) / (
                confusion_matrix["tp"] + confusion_matrix["tn"] + confusion_matrix["fp"] + confusion_matrix["fn"])

    @staticmethod
    def name():
        return "Accuracy"


class Precision(PerformanceMetric):
    @staticmethod
    def calculate(score: Score, interpreted_classes: Series) -> float:
        """ Calculate the precision.

        Uses a :class:`~vpmbench.summaries.ConfusionMatrix` to calculate the precision/positive predictive value.

        Parameters
        ----------
        score :
            The score from the plugin
        interpreted_classes :
            The interpreted classes

        Returns
        -------
        float
            The calculated precision
        """
        confusion_matrix = ConfusionMatrix().calculate(score, interpreted_classes)
        return confusion_matrix["tp"] / (confusion_matrix["tp"] + confusion_matrix["fp"])

    @staticmethod
    def name():
        return "Precision"


class NegativePredictiveValue(PerformanceMetric):
    @staticmethod
    def calculate(score: Score, interpreted_classes: Series) -> float:
        """ Calculate the negative predictive value.

        Uses a :class:`~vpmbench.summaries.ConfusionMatrix` to calculate the negative predictive value.

        Parameters
        ----------
        score :
            The score from the plugin
        interpreted_classes :
            The interpreted classes

        Returns
        -------
        float
            The calculated negative predictive value
        """
        confusion_matrix = ConfusionMatrix().calculate(score, interpreted_classes)
        return confusion_matrix["tn"] / (confusion_matrix["tn"] + confusion_matrix["fn"])

    @staticmethod
    def name():
        return "Negative Predictive Value"


class Specificity(PerformanceMetric):
    @staticmethod
    def calculate(score: Score, interpreted_classes: Series) -> float:
        """ Calculate the specificity.

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


class Concordance(PerformanceMetric):
    @staticmethod
    def calculate(score: Score, interpreted_classes: Series) -> float:
        """ Calculate the concordance, i.e, the sum of true positives and true negatives.

        Uses a :class:`~vpmbench.summaries.ConfusionMatrix` to calculate the concordance.

        Parameters
        ----------
        score :
            The score from the plugin
        interpreted_classes :
            The interpreted classes

        Returns
        -------
        float
            The calculated concordance
        """
        confusion_matrix = ConfusionMatrix().calculate(score, interpreted_classes)
        return confusion_matrix["tp"] + confusion_matrix["tn"]

    @staticmethod
    def name():
        return "Concordance"


class AreaUnderTheCurveROC(PerformanceMetric):
    """ Calculate the area under the roc curve (AUROC).

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


class MatthewsCorrelationCoefficient(PerformanceMetric):
    @staticmethod
    def calculate(score: Score, interpreted_classes: Series) -> float:
        """ Calculate the matthews correlation coefficient.
.

        Parameters
        ----------
        score :
            The score from the plugin
        interpreted_classes :
            The interpreted classes

        Returns
        -------
        float
            The matthews correlation coefficient
        """
        return matthews_corrcoef(interpreted_classes, score.interpret())

    @staticmethod
    def name():
        return "Matthews correlation coefficient"
