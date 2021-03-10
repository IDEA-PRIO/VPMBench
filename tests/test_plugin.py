import pytest
from pandas import DataFrame


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
