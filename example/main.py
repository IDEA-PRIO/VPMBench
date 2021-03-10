from vpmbench.api import run_pipeline
from vpmbench.logging import enable_logging
from vpmbench.metrics import Specificity, Sensitivity
from vpmbench.summaries import ROCCurve, ConfusionMatrix
from vpmbench.utils import plot_roc_curves, report_metrics, plot_confusion_matrices

# Specifying pipeline inputs
all_plugins = lambda plugin: True
evaluation_input_data = "ClinVar_GRCh37_500benign_500pathogenic.vcf"
summaries = [ConfusionMatrix, ROCCurve]
metrics = [Specificity, Sensitivity]

enable_logging()
# Run the vpmbench pipeline
report = run_pipeline(with_data=evaluation_input_data,
                      reporting=summaries + metrics,
                      using=all_plugins,
                      plugin_path="/home/andreas/work/code/idea-prio-testbench/plugins")
#
# Plot the summaries and report the metrics
plot_confusion_matrices(report)
plot_roc_curves(report)
report_metrics(report)
