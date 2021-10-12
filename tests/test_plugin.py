import pytest
from pandas import DataFrame

from vpmbench.api import invoke_methods, run_pipeline
from vpmbench.data import AnnotatedVariantData


def test_run_python_plugin(python_plugin, evaluation_data_grch37):
    result = python_plugin.run(evaluation_data_grch37.variant_data)
    assert result is not None
    assert type(result) is DataFrame
    assert set(result.columns) == {"UID", python_plugin.score_column_name}


def test_run_docker_plugin(docker_plugin, evaluation_data_grch37):
    result = docker_plugin.run(evaluation_data_grch37.variant_data)
    assert result is not None
    assert type(result) is DataFrame
    assert set(result.columns) == {"UID", docker_plugin.score_column_name}


def test_run_plugin_on_invalid_data_fails(docker_plugin, evaluation_data_grch38):
    with pytest.raises(Exception):
        docker_plugin.run(evaluation_data_grch38.variant_data)


def test_score_cuttofs(cutoff_greater_plugin, cutoff_less_plugin, cutoff_just_number_plugin, evaluation_data_grch37):
    plugins = [cutoff_greater_plugin, cutoff_less_plugin, cutoff_just_number_plugin]
    results = invoke_methods(plugins, evaluation_data_grch37.variant_data)
    for score in results.scores:
        assert sum(score.interpret()) == 0


def test_multi_cuttof(plugin_path, multi_cutoff_plugin, grch37_vcf_path, available_summaries, available_metrics):
    plugin_selection = lambda plugin: plugin == multi_cutoff_plugin
    run_pipeline(grch37_vcf_path, reporting=available_metrics + available_summaries, using=plugin_selection,
                 plugin_path=plugin_path)
