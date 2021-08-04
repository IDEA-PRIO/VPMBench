from vpmbench.api import run_pipeline


def test_run_pipeline(grch37_vcf_path, plugin_path, available_metrics):
    all_plugins = lambda plugin: True
    report = run_pipeline(with_data=grch37_vcf_path,
                          reporting=available_metrics,
                          using=all_plugins,
                          plugin_path=plugin_path)
    assert report is not None


def test_run_pipeline(grch37_vcf_path, plugin_path, available_summaries):
    all_plugins = lambda plugin: True
    report = run_pipeline(with_data=grch37_vcf_path,
                          reporting=available_summaries,
                          using=all_plugins,
                          plugin_path=plugin_path)
    assert report is not None


def test_unique_metrics_names(available_metrics):
    names = [metric.name for metric in available_metrics]
    assert len(set(names)) == len(available_metrics)


def test_unique_summary_names(available_summaries):
    names = [summary.name for summary in available_summaries]
    assert len(set(names)) == len(available_summaries)
