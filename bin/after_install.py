import sys

from vpmbench.api import run_pipeline
from vpmbench.logging import enable_logging
from vpmbench.metrics import Specificity, Sensitivity
from vpmbench.utils import report_metrics

# Specifying pipeline inputs
all_plugins = lambda plugin: True
evaluation_input_data = sys.argv[1]
metrics = [Specificity, Sensitivity]
enable_logging()

# Run the vpmbench pipeline
report = run_pipeline(with_data=evaluation_input_data,
                      reporting=metrics,
                      using=all_plugins,
                      plugin_path=sys.argv[2])

# Plot the summaries and report the metrics
report_metrics(report)
