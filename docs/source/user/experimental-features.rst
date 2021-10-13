Experimental Features
=====================


.. warning::
    All the listed features below are regarded as **experimental**, i.e., are rather integrated prototypcially into VPMBench.
    Thus, their API might be subject to changes or might be moved to another branches.


Multi-Class Classification Support
----------------------------------

VPMBench also supports the evaluation of non-binary classifier, e.g., classifier trying to predict the clinical significance of the variance as defined in `ClinVar <https://www.ncbi.nlm.nih.gov/clinvar/docs/clinsig/>`_.
Therefore, the following steps are required:

Implementing a Multi-Class Plugin
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To implement a multi-class plugin, you have to basically follow the same approach as for the :ref:`standard plugins <plugins>`.
The only difference between the standard plugins and multi-class plugins is the number of specified cutoff points.
For the multi-class plugins, we require that for each class a cuttoff is defined as shown in the following example:

.. code-block:: yaml

    name: My Multi-Class Plugin
    supported-variants: SNP
    reference-genome: GRCh37/hg19
    cutoff:
      - < 0.3
      - < 0.6
      - < 1

    entry-point:
      mode: Python
      file: ./entrypoint.py

When interpreting the scores of the prediction methods these cutoff are applied in order to assign the classes. The first cutoff correspond to class 0, the second one to class 1, etc .

Implementing a custom extractor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Implementing a custom extractor allows you to assign arbitrary class labels for each of the entries.
Currently, we provide customizable extractors for :class:`CSV <vpmbench.extractor.CSVExtractor>` and :class:`VCF <vpmbench.extractor.VCFExtractor>` files.

A custom extractor supporting mutli-classes might look like this:

.. code-block:: python

    class CustomMultiClassCSVExtractor(CSVExtractor):

        def _row_to_evaluation_data_entry(self, row: dict) -> EvaluationDataEntry:
            translation_map = {"A":"bad","B":"really bad","C":"its ok"}
            chrom = str(row["CHROM"].strip())
            pos = int(row["POS"].strip())
            ref = row["REF"].strip()
            alt = row["ALT"].strip()
            clnsig = translation_map[row["CLASS"].strip()]
            return EvaluationDataEntry(chrom, pos, ref, alt, clnsig, VariationType.SNP, ReferenceGenome.HG19)


Invoking the VPMBench
^^^^^^^^^^^^^^^^^^^^^

After the previous steps, VPMBench is ready to be invoked.
Consequently, this implies that you have to filter for your multi-class plugin and that you have to pass your custom extractor.
Addtionally, a `pathogencity_map` has to be passed to the testbench based on which between the labels of your custom can be converted into the numerical classes corresponding to your specified cutoffs.

An example might be look like this:

.. code-block:: python

    from vpmbench.api import run_pipeline
    from vpmbench.summaries import ConfusionMatrix
    from vpmbench.utils import plot_confusion_matrices
    from vpmbench.predicates import is_multiclass_plugin
    from my.package import MyCustomExtractor

    class_map =  {"bad": 0, "really bad": 1, "its ok": 2}
    multi_class_plugins = lambda plugin: is_multiclass_plugin(plugin)
    my_data = "/my/path/to/my/multiclass-data.csv"
    results = run_pipeline(my_data,
                           using=multi_class_plugins,
                           extractor=MyCustomExtractor
                           reporting=[ConfusionMatrix],
                           pathogenicity_class_map=class_map)
    plot_confusion_matrices(results)

Runnable examples can be found under ``tests/test_multiclass.py``.