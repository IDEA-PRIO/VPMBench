from vpmbench.api import run_pipeline
from vpmbench.logging import enable_logging
from vpmbench.metrics import Specificity, Sensitivity, AreaUnderTheCurveROC
from vpmbench.summaries import ROCCurve, ConfusionMatrix
from vpmbench.utils import plot_roc_curves, report_metrics, plot_confusion_matrices

# Specifying pipeline inputs
cadd_and_fathmm = lambda plugin: "CADD" in plugin.name or "fathmm-MKL" in plugin.name
evaluation_input_data = "ClinVar_GRCh37_500benign_500pathogenic.vcf"
summaries = [ConfusionMatrix, ROCCurve]
metrics = [Specificity, Sensitivity,AreaUnderTheCurveROC]

enable_logging()
# Run the vpmbench pipeline
report = run_pipeline(with_data=evaluation_input_data,
                      reporting=summaries + metrics,
                      using=cadd_and_fathmm,
                      plugin_path="/media/andreas/OneTouch/VPMBench-Plugins")
#
# Plot the summaries and report the metrics
plot_confusion_matrices(report)
plot_roc_curves(report)
report_metrics(report)
