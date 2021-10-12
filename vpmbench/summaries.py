from abc import ABC, abstractmethod
from warnings import warn

from pandera.typing import Series
from sklearn.metrics import confusion_matrix, roc_curve, precision_recall_curve

from vpmbench.data import Score
from vpmbench.enums import default_pathogencity_class_map


class PerformanceSummary(ABC):
    """ Represent a performance summary    """

    @staticmethod
    @abstractmethod
    def calculate(score: Score, interpreted_classes: Series,
                  pathogenicity_class_map=default_pathogencity_class_map) -> dict:
        return {}

    @staticmethod
    @abstractmethod
    def name():
        return None


class ConfusionMatrix(PerformanceSummary):
    @staticmethod
    def name():
        return "Confusion Matrix"

    @staticmethod
    def calculate(score: Score, interpreted_classes: Series,
                  pathogenicity_class_map=default_pathogencity_class_map) -> dict:
        """ Calculates the confusion matrix.

        Parameters
        ----------
        score :
            The score from the plugin
        interpreted_classes :
            The interpreted classes

        Returns
        -------
        dict
            A dictionary with the following keys: ``tn`` - the number of true negatives, ``fp`` - the number of false positives,
            ``fn`` - the number of false negatives, ``tp`` - the number of the true positives
        """
        interpreted_values = score.interpret()
        labels = sorted(list(set(pathogenicity_class_map.values())), reverse=True)
        cm = confusion_matrix(interpreted_classes, interpreted_values, labels=labels)
        rv = {}
        try:
            tn, fp, fn, tp = cm.ravel()
            rv = {'tn': tn, 'fp': fp, 'fn': fn, 'tp': tp}
        except Exception:
            pass
        rv["data"] = cm
        rv["pathogenicity_class_map"] = pathogenicity_class_map
        rv["labels"] = labels
        return rv


class ROCCurve(PerformanceSummary):
    @staticmethod
    def calculate(score: Score, interpreted_classes: Series,
                  pathogenicity_class_map=default_pathogencity_class_map) -> dict:
        """ Calculates the ROC curves.

        Parameters
        ----------
        score :
            The score from the prioritization method
        interpreted_classes :
            The interpreted classes

        Returns
        -------
        dict
            A dictionary with the following keys: ``fpr``- false positive rates, ``tpr`` - true positives rates,
            ``thresholds`` - the thresholds

        """
        if len(pathogenicity_class_map) > 2:
            warn("Can't calculate ROC curves for multiclass.")
            return {}
        fpr, tpr, thresholds = roc_curve(interpreted_classes, score.data)
        return {'fpr': fpr, "tpr": tpr, "thresholds": thresholds}

    @staticmethod
    def name():
        return "ROC Curve"


class PrecisionRecallCurve(PerformanceSummary):
    @staticmethod
    def calculate(score: Score, interpreted_classes: Series,
                  pathogenicity_class_map=default_pathogencity_class_map) -> dict:
        """ Calculates the precision recall curve.

        Parameters
        ----------
        score :
            The score from the prioritization method
        interpreted_classes :
            The interpreted classes

        Returns
        -------
        dict
            A dictionary with the following keys: ``precsion``- precision values, ``recall`` - recall values,
            ``thresholds`` - the thresholds

        """
        if len(pathogenicity_class_map) > 2:
            warn("Can't calculate ROC curves for multiclass.")
            return {}
        precision, recall, thresholds = precision_recall_curve(interpreted_classes, score.data)
        return {'precision': precision, "recall": recall, "thresholds": thresholds}

    @staticmethod
    def name():
        return "Precision-Recall Curve"
