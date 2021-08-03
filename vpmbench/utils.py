"""

"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from vpmbench.metrics import PerformanceMetric, AreaUnderTheCurveROC
from vpmbench.report import PerformanceReport
from vpmbench.summaries import ConfusionMatrix, ROCCurve


def plot_roc_curves(report: PerformanceReport):
    """ Plot the ROC curves using a performance report

    Shows the roc curve the :class:`vpmbench.summaries.ROCCurve` was calculated.

    Parameters
    ----------
    report :
        The performance report

    """
    if ROCCurve.name() not in report.metrics_and_summaries:
        return
    roc_curves = report.metrics_and_summaries[ROCCurve.name()]
    mpl.rcParams['figure.dpi'] = 600

    plt.figure()
    plt.plot([0, 1], [0, 1], color='navy', linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    auroc = report.metrics_and_summaries.get(AreaUnderTheCurveROC.name(), {})
    for plugin, result in roc_curves.items():
        label = f"{plugin.name}"
        if plugin in auroc:
            label += f" (AUROC: {auroc[plugin]})"
        plt.plot(result["fpr"], result["tpr"], label=label)
    plt.xlabel('False positive rate')
    plt.ylabel('True positive rate')
    plt.title('ROC curve')
    plt.legend(loc='best')
    plt.show()


def plot_confusion_matrices(report: PerformanceReport,
                            normalize=False,
                            cmap="Blues"):
    """ Plot the confusion matrices of the prioritization method from a performance report

    Shows the roc curve the :class:`vpmbench.summaries.ConfusionMatrix` was calculated.

    Parameters
    ----------
    report :
        The performance report
    normalize:
        If true the values in the confusion matrix are normalized
    cmap:
        The colormap that should be used to plot the confusion matrices
    """
    if ConfusionMatrix.name() not in report.metrics_and_summaries:
        return
    confusion_matrices: dict = report.metrics_and_summaries[ConfusionMatrix.name()]
    for plugin, confusion_matrix in confusion_matrices.items():
        cm = np.array([[confusion_matrix["tn"], confusion_matrix["fp"]],
                       [confusion_matrix["fn"], confusion_matrix["tp"]]])
        classes = ["Pathogenic", "Benign"]
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

        fig, ax = plt.subplots()

        vmax = 1 if normalize else cm.sum(axis=1)[0]
        im = ax.imshow(cm, interpolation='nearest', cmap=cmap, vmin=0, vmax=vmax)
        ax.figure.colorbar(im, ax=ax)
        n_classes = cm.shape[0]
        title = f"Confusion-Matrix: {plugin.name}"
        ax.set(xticks=np.arange(n_classes),
               yticks=np.arange(n_classes),
               # ... and label them with the respective list entries
               xticklabels=classes,
               yticklabels=classes,
               title=title,
               ylabel='True label',
               xlabel='Predicted label')
        ax.set_ylim((n_classes - 0.5, -0.5))
        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")

        # Loop over data dimensions and create text annotations.
        fmt = '.2f' if normalize else 'd'
        thresh = (cm.max() + cm.min()) / 2.0
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, format(cm[i, j], fmt),
                        ha="center", va="center",
                        color="white" if cm[i, j] > thresh else "black")
        fig.tight_layout()
        plt.show()


def report_metrics(report: PerformanceReport):
    """ Print the calculated metrics to the terminal

    Parameters
    ----------
    report :
        The performance report

    """
    metric_names = [cls.name() for cls in PerformanceMetric.__subclasses__()]
    for metric_name in metric_names:
        if metric_name not in report.metrics_and_summaries:
            continue
        print(f"{metric_name}")
        for plugin, value in report.metrics_and_summaries[metric_name].items():
            print(f"- {plugin.name}: {value}")
