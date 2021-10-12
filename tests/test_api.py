import pytest

from vpmbench.api import extract_evaluation_data, load_plugin, load_plugins, invoke_method, invoke_methods, run_pipeline
from vpmbench.metrics import Sensitivity, Specificity
from vpmbench.summaries import ConfusionMatrix, ROCCurve


def test_extract_evaluation_data(grch37_vcf_path):
    evaluation_data = extract_evaluation_data(grch37_vcf_path)
    assert evaluation_data is not None


def test_load_python_manifest(python_plugin_path):
    plugin = load_plugin(python_plugin_path)
    assert "Python-Plugin" == plugin.name
    assert plugin.entry_point is not None


def test_load_docker_manifest(docker_plugin_path):
    plugin = load_plugin(docker_plugin_path)
    assert "Docker-Plugin" == plugin.name
    assert plugin.entry_point is not None


def test_load_plugins(plugin_path):
    plugins = load_plugins(plugin_path)
    names = [plugin.name for plugin in plugins]
    assert set(names) == {'Depth-Plugin',
                          'Docker-Plugin',
                          'Extended-Manifests-Plugin',
                          'Python-Plugin',
                          'Python-Plugin Cuttof Greater',
                          'Python-Plugin Cuttof Less',
                          'Python-Plugin Cuttof Number',
                          'Python-Plugin Multi Cuttof',
                          'Zero-Python-Plugin'}


def test_invoke_docker_method(docker_plugin, evaluation_data_grch37):
    plugin, data = invoke_method(docker_plugin, evaluation_data_grch37.variant_data)
    assert docker_plugin == plugin
    assert set(data.columns) == {"UID", "Docker-Plugin_SCORE"}
    assert len(evaluation_data_grch37.variant_data) == len(data)


def test_invoke_python_method(python_plugin, evaluation_data_grch37):
    plugin, data = invoke_method(python_plugin, evaluation_data_grch37.variant_data)
    assert python_plugin == plugin
    assert set(data.columns) == {"UID", "Python-Plugin_SCORE"}
    assert len(evaluation_data_grch37.variant_data) == len(data)


def test_invoke_methods(docker_plugin, python_plugin, evaluation_data_grch37):
    annotated_variants = invoke_methods([docker_plugin, python_plugin], evaluation_data_grch37.variant_data)
    assert annotated_variants is not None
    assert len(annotated_variants.scores) == 2
    assert set(annotated_variants.plugins) == {docker_plugin, python_plugin}


def test_run_pipeline(grch37_vcf_path, plugin_path):
    all_plugins = lambda plugin: True
    summaries = [ConfusionMatrix, ROCCurve]
    metrics = [Specificity, Sensitivity]
    report = run_pipeline(with_data=grch37_vcf_path,
                          reporting=summaries + metrics,
                          using=all_plugins,
                          plugin_path=plugin_path)
    assert report is not None
    assert len(report.metrics_and_summaries) == len(summaries + metrics)


def test_run_pipeline_fails(grch37_vcf_path, plugin_path):
    no_plugins = lambda plugin: False
    summaries = [ConfusionMatrix, ROCCurve]
    metrics = [Specificity, Sensitivity]
    with pytest.raises(RuntimeError):
        report = run_pipeline(with_data=grch37_vcf_path,
                              reporting=summaries + metrics,
                              using=no_plugins,
                              plugin_path=plugin_path)


def test_run_pipeline_without_filter(grch37_vcf_path, plugin_path):
    summaries = [ConfusionMatrix, ROCCurve]
    metrics = [Specificity, Sensitivity]
    report = run_pipeline(with_data=grch37_vcf_path,
                          reporting=summaries + metrics,
                          plugin_path=plugin_path)
    assert report is not None


def test_invoke_methods_invalid_data(docker_plugin, python_plugin, evaluation_data_grch38):
    with pytest.raises(Exception):
        invoke_methods(evaluation_data_grch38.annotated_variant_data, [docker_plugin, python_plugin])


def test_invoke_method_invalid_data(docker_plugin, evaluation_data_grch38):
    with pytest.raises(Exception):
        invoke_methods(evaluation_data_grch38.annotated_variant_data, docker_plugin)
