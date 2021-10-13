from vpmbench.api import run_pipeline
from vpmbench.data import EvaluationData, EvaluationDataEntry
from vpmbench.enums import VariationType, ReferenceGenome
from vpmbench.extractor import CSVExtractor
from vpmbench.metrics import Sensitivity, Specificity
from vpmbench.summaries import ConfusionMatrix, ROCCurve
from vpmbench.utils import plot_confusion_matrices


class CustomMultiClassCSVExtractor(CSVExtractor):

    def _row_to_evaluation_data_entry(self, row: dict) -> EvaluationDataEntry:
        return EvaluationDataEntry(str(row["CHROM"].strip()), int(row["POS"].strip()), row["REF"].strip(),
                                   row["ALT"].strip(),
                                   row["CLASS"].strip(), VariationType.SNP,
                                   ReferenceGenome.HG19)


def test_run_mutliclass_pipeline(plugin_path, multi_cutoff_plugin, multi_class_custom_csv_path):
    summaries = [ConfusionMatrix, ROCCurve]
    metrics = [Specificity, Sensitivity]
    pathogencity_map = {"benign": 0, "likely pathogenic": 1, "pathogenic": 2}
    plugin_selection = lambda plugin: plugin == multi_cutoff_plugin
    results = run_pipeline(multi_class_custom_csv_path,
                           using=plugin_selection,
                           extractor=CustomMultiClassCSVExtractor,
                           reporting=summaries + metrics,
                           plugin_path=plugin_path,
                           pathogenicity_class_map=pathogencity_map)


def test_run_mutliclass_pipeline_all_summaries(plugin_path, multi_cutoff_plugin, multi_class_custom_csv_path,
                                               available_summaries):
    pathogencity_map = {"benign": 0, "likely pathogenic": 1, "pathogenic": 2}
    plugin_selection = lambda plugin: plugin == multi_cutoff_plugin
    results = run_pipeline(multi_class_custom_csv_path,
                           using=plugin_selection,
                           extractor=CustomMultiClassCSVExtractor,
                           reporting=available_summaries,
                           plugin_path=plugin_path,
                           pathogenicity_class_map=pathogencity_map)


def test_run_mutliclass_pipeline_all_metrics(plugin_path, multi_cutoff_plugin, multi_class_custom_csv_path,
                                             available_metrics):
    pathogencity_map = {"benign": 0, "likely pathogenic": 1, "pathogenic": 2}
    plugin_selection = lambda plugin: plugin == multi_cutoff_plugin
    results = run_pipeline(multi_class_custom_csv_path,
                           using=plugin_selection,
                           extractor=CustomMultiClassCSVExtractor,
                           reporting=available_metrics,
                           plugin_path=plugin_path,
                           pathogenicity_class_map=pathogencity_map)


def test_run_mutliclass_plot_confusion_matrix(plugin_path, multi_cutoff_plugin, multi_class_custom_csv_path):
    pathogencity_map = {"benign": 0, "likely pathogenic": 1, "pathogenic": 2}
    plugin_selection = lambda plugin: plugin == multi_cutoff_plugin
    results = run_pipeline(multi_class_custom_csv_path,
                           using=plugin_selection,
                           extractor=CustomMultiClassCSVExtractor,
                           reporting=[ConfusionMatrix],
                           plugin_path=plugin_path,
                           pathogenicity_class_map=pathogencity_map)
    plot_confusion_matrices(results)
