import pytest
from pandas import DataFrame

from vpmbench.api import invoke_methods
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
