VPMBench - A test bench for variant prioritization methods
==========================================================

|docs|


VPMBench automates the evaluation of variant prioritization methods by using a pipeline in which the methods are integrated as plugins.
Thus, you can include new methods as plugins without changing the pipeline code.
Stop reinventing the wheel by developing a bunch of R/Python/Bash scripts to evaluate your prioritization method and use VPMBench to focus your time on compiling suitable evaluation input data and interpreting the results.

Look how easy it is to use:

.. code-block:: python

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
                          using=all_plugins)

    # Plot the summaries and report the metrics
    plot_confusion_matrices(report)
    plot_roc_curves(report)

Features
--------

- Supported input formats: Clinvar-VCF, VariSNP
- Integration of new prioritization methods as Plugins via Docker or Python
- Prebuild plugins for fathmm-MKL and CADD
- Automatic calculation of performance summaries (confusion matrices, ROC curves) and metrics (Sensitivity, Specificity)
- Easy to extend to support additional input formats, performance summaries, and metrics

Installation
------------

Clone the repository and install the VPMBench Python library via:

.. code-block:: console

    $ pip install .

Install VPMBench with plugins via the installation script:

.. code-block:: console

    $ ./install.sh

Contribute
----------

- Source Code: https://github.com/IDEA-PRIO/VPMBench
- Issue Tracker: https://github.com/IDEA-PRIO/VPMBench/issues
- Documentation: https://vpmbench.readthedocs.io/en/latest/

Support
-------

If you are having issues, please let me know.
You can write me a mail: andreas.ruscheinski@uni-rostock.de

License
-------

MIT License

Copyright (c) 2021, Andreas Ruscheinski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.



.. |docs| image:: https://readthedocs.org/projects/vpmbench/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://vpmbench.readthedocs.io/en/latest/?badge=latest


