import multiprocessing as mp
import warnings
from datetime import datetime
from pathlib import Path
from typing import Type, Union, Callable, Any, List, Tuple, Dict, Optional

import yaml
from pandas import DataFrame

from vpmbench import log
from vpmbench.config import DEFAULT_PLUGIN_PATH
from vpmbench.data import EvaluationData, AnnotatedVariantData
from vpmbench.extractor import Extractor, ClinVarVCFExtractor
from vpmbench.metrics import PerformanceMetric
from vpmbench.plugin import Plugin, PluginBuilder
from vpmbench.report import PerformanceReport
from vpmbench.summaries import PerformanceSummary


def is_plugin_compatible_with_data(plugin: Plugin, data: EvaluationData):
    plugin.is_compatible_with_data(data.variant_data)
    return True


def extract_evaluation_data(evaluation_data_path: Union[str, Path],
                            extractor: Union[Extractor, Type[Extractor]] = ClinVarVCFExtractor) -> EvaluationData:
    """ Extract the EvaluationData from the evaluation input data.

    Parses the evaluation the evaluation input data given by the `evaluation_data_path` using the `extractor`.

    Parameters
    ----------
    evaluation_data_path : Union[str, Path]
        The path to the evaluation input data
    extractor : Type[Extractor]
        The extractor that should be used to parse the evaluation input data

    Returns
    -------
    EvaluationData
        The evaluation data extracted from `evaluation_input_data` using the `extractor`

    """
    try:
        extractor = extractor()
    except Exception as e:
        pass
    log.info(f"Extract data from {evaluation_data_path} ")
    log.debug(f"Used extractor: {extractor}!")
    return extractor.extract(evaluation_data_path)


def load_plugin(manifest_path: Union[str, Path]) -> Plugin:
    """ Load a manifest given by the `manifest_path` as a plugin.

    Parameters
    ----------
    manifest_path : Union[str, Path]
        The path to the manifest

    Returns
    -------
    Plugin
        The loaded plugin

    """
    with open(manifest_path, "r") as manifest_file:
        manifest = yaml.safe_load(manifest_file)
        manifest["path"] = Path(manifest_path)
        return PluginBuilder.build_plugin(**manifest)


def load_plugins(plugin_path: Union[str, Path], plugin_selection: Optional[Callable[[Plugin], bool]] = None) -> \
        List[Plugin]:
    """ Load all plugins from the `plugin_directory` and applies the plugin selection to filter them.

    If `plugin_selection` is `None` all plugins in the `plugin_path` are returned.

    Parameters
    ----------
    plugin_path : Union[str, PathLike]
        The path to your plugin directory

    plugin_selection : Optional[Callable[[Plugin], bool]]
        The selection function that should be applied to filter the plugins

    Returns
    -------
    List[Plugin]
        The list of plugins loaded from the `plugin_path`

    """
    log.info(f"Load plugins from {plugin_path}")
    plugin_path = Path(plugin_path).resolve().absolute()
    log.debug(f"Absolute plugin path: {plugin_path}")
    found_plugins = []
    for manifest in plugin_path.glob("*/**/manifest.yaml"):
        try:
            plugin = load_plugin(manifest)
            found_plugins.append(plugin)
        except Exception as e:
            warnings.warn(f"Can't load plugin from {manifest}: {e} ")
    log.debug(f"Found {len(found_plugins)} plugins: {[plugin.name for plugin in found_plugins]}")
    if filter:
        filtered_plugins = list(filter(plugin_selection, found_plugins))
        log.debug(f"Returning {len(filtered_plugins)} filtered plugins: {[plugin.name for plugin in filtered_plugins]}")
        return filtered_plugins
    log.debug(f"Returning {len(found_plugins)} plugins: {found_plugins}")
    return found_plugins


def invoke_method(plugin: Plugin, variant_data: DataFrame) -> Tuple[Plugin, DataFrame]:
    """ Invoke a prioritization method represented as a `plugin` on the `variant_data`.

    Uses :meth:`vpmbench.plugin.Plugin.run` to invoke the prioritization method.

    Parameters
    ----------
    plugin : Plugin
        The plugin for the method that should be invoked

    variant_data : pandas.DataFrame
        The variant data which should be processed by the method

    Returns
    -------
    Tuple[Plugin,pandas.DataFrame]
            The plugin and the resulting data from the method
    """
    return plugin, plugin.run(variant_data)


def invoke_methods(plugins: List[Plugin], variant_data: DataFrame, cpu_count: int = -1) -> AnnotatedVariantData:
    """ Invoke multiple prioritization methods given as a list of `plugins` on the `variant_data` in parallel.

    Calls :func:`vpmbench.api.invoke_method` for each in plugin in `plugins` on the `variant_data`.
    The compatibility of the `plugins` with the `variant_data` are checked via :meth:`Plugin.is_compatible_with_data <vpmbench.plugin.Plugin.is_compatible_with_data>`.
    If `cpu_count` is -1 then (number of cpus-1) are used to run the plugins in parallel; set to one 1 disable parallel execution.
    The resulting annotated variant data is constructed by collecting the outputs of the plugin use them as input for :meth:`AnnotatedVariantData.from_results <vpmbench.data.AnnotatedVariantData.from_results>`.

    Parameters
    ----------
    variant_data : pandas.DataFrame
        The variant data which should be processed by the plugins

    plugins : List[Plugin]
        A list of plugins that should be invoked

    cpu_count : int
        The numbers of cpus that should be used to invoke the plugins in parallel

    Returns
    -------
    AnnotatedVariantData
        The variant data annotated with the scores from the prioritization methods

    """
    map(lambda plugin: plugin.is_compatible_with_data(variant_data), plugins)
    if cpu_count == -1:
        cpu_count = mp.cpu_count() - 1
    log.info(f"Invoke methods")
    log.debug(f"#CPUs: {cpu_count}")
    pool = mp.Pool(cpu_count)
    jobs = [pool.apply_async(invoke_method, args=(plugin, variant_data)) for plugin in plugins]
    plugin_results = []
    for job in jobs:
        plugin_results.append(job.get())
    pool.close()
    return AnnotatedVariantData.from_results(variant_data, plugin_results)


# TODO: Refactor to have a real performance result object
def calculate_metric_or_summary(annotated_variant_data: AnnotatedVariantData, evaluation_data: EvaluationData,
                                report: Union[Type[PerformanceMetric], Type[PerformanceSummary]]) -> Dict[Plugin, Any]:
    """ Calculates a metrics or a summary for all plugins in the annotated variant data.

    Parameters
    ----------
    annotated_variant_data : AnnotatedVariantData
        The annotated variant data

    evaluation_data : EvaluationData
        The evaluation data

    report: Union[Type[PerformanceMetric], Type[PerformanceSummary]]
        The performance summary or metric that should be calculated

    Returns
    -------
    Dict[Plugin, Any]
        A dictionary where the keys are the plugins and the result from the calculations are the values

    """
    log.debug(f"Calculate {report.name()}")
    rv = {}
    for score in annotated_variant_data.scores:
        rv[score.plugin] = report.calculate(score, evaluation_data.interpreted_classes)
    return rv


def calculate_metrics_and_summaries(annotated_variant_data: AnnotatedVariantData, evaluation_data: EvaluationData,
                                    reporting: List[Union[Type[PerformanceMetric], Type[PerformanceSummary]]]) -> Dict[
    str, dict]:
    """ Calculates the metrics and summaries for the plugin used to annotate the variants.

    Uses :func:`~vpmbench.api.calculate_metric_or_summary` to calculate all summaries and metrics from `reporting`.

    Parameters
    ----------
    annotated_variant_data :
        The annotated variant data
    evaluation_data :
        The evaluation data
    reporting :
        The metrics and summaries that should be calculated

    Returns
    -------
    Dict
        Keys: the name of the metric/summary; Values: The results from :func:`~vpmbench.api.calculate_metric_or_summary`

    """
    log.info("Calculate reports")
    rv = {}
    for report in reporting:
        rv[report.name()] = calculate_metric_or_summary(annotated_variant_data, evaluation_data, report)
    return rv


def run_pipeline(with_data: Union[str, Path],
                 reporting: List[Union[Type[PerformanceMetric], Type[PerformanceSummary]]],
                 using: Callable[[Plugin], Any] = None,
                 extractor: Type[Extractor] = ClinVarVCFExtractor,
                 plugin_path: Union[str, Path] = DEFAULT_PLUGIN_PATH, cpu_count: int = -1) -> PerformanceReport:
    log.info("Run pipeline")
    start_time = datetime.now()
    log.debug(f'Starting time: {start_time.strftime("%d/%m/%Y %H:%M:%S")}')
    evaluation_data: EvaluationData = extract_evaluation_data(with_data, extractor)
    plugins: List[Plugin] = load_plugins(plugin_path, using)
    if len(plugins) == 0:
        raise RuntimeError(f"Can' find plugins in {plugin_path}")
    annotated_variants: AnnotatedVariantData = invoke_methods(plugins, evaluation_data.variant_data, cpu_count)
    reports = calculate_metrics_and_summaries(annotated_variants, evaluation_data, reporting)
    log.info("Stop pipeline")
    end_time = datetime.now()
    log.debug(f'Finishing time: {end_time.strftime("%d/%m/%Y %H:%M:%S")}')
    log.debug(f'Pipeline took {(end_time - start_time).seconds}')

    report = PerformanceReport(evaluation_data, annotated_variants, reports)
    return report
