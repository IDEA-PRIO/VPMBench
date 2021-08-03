from pathlib import Path
from statistics import mean
from timeit import default_timer

import matplotlib.pylab as plt
import pandas as pd
from vpmbench.api import load_plugins, extract_evaluation_data, is_plugin_compatible_with_data, run_pipeline
from vpmbench.logging import enable_logging
from vpmbench.metrics import Concordance
from vpmbench.report import PerformanceReport

# samples_path = "/media/arusch/One Touch/Data/samples2"
plugin_path = "/home/andreas/work/code/VPM-Bench/VPMBench-private/plugins"
all_plugins = lambda plugin: "CADD" in plugin.name
enable_logging()

metrics = [Concordance]
# Run the vpmbench pipeline
report = run_pipeline(with_data="/home/andreas/work/code/VPM-Bench/VPMBench-private/example/bad.vcf",
                      reporting=metrics,
                      using=all_plugins,
                      plugin_path=plugin_path,
                      cpu_count=-1)

#
# def get_clinvar_releases(file_path):
#     # returns a list with files
#     path = Path(file_path)
#     return list(path.glob("*.vcf"))
#
#
# def get_clinvar_release_date(clinvar_release_sample_path):
#     return int(clinvar_release_sample_path.stem.split("_")[3])
#
#
# def get_clinvar_sample_number(clinvar_release_sample_path):
#     splits = clinvar_release_sample_path.stem.split("_")
#     return int(splits[1])
#
#
# def return_concordance_value(report: PerformanceReport):
#     concordanceItems = report.metrics_and_summaries["Concordance"].items()
#     return {key.name: value for (key, value) in concordanceItems}
#
#
# def export_to_csv(data):
#     df = pd.DataFrame(data)
#     df.to_csv("concordance.csv", index=False)
#     return df
#
#
# def create_dictionary_for_concordance_plugin_data():
#     # { release_date : { plugin_name : [concordance_values]}}
#     time_concordance_plugin_data = {}
#     # Specifying pipeline inputs
#     all_plugins = lambda plugin: True
#     # clinvar_samples = sorted(get_clinvar_releases(samples_path), key=lambda x: get_clinvar_release_date(x))
#     # print(f"There are {len(clinvar_samples)} clinvar samples")
#     # time_measures = []
#     # enable_logging()
#     # for (i, clinvar_sample) in enumerate(clinvar_samples):
#     #     print(f"[{i + 1}/{len(clinvar_samples)}]: Run {clinvar_sample}")
#         start = default_timer()
#         release_data_plugin_data = time_concordance_plugin_data.setdefault(clinvar_sample, {})
#         metrics = [Concordance]
#         # Run the vpmbench pipeline
#         report = run_pipeline(with_data=clinvar_sample,
#                               reporting=metrics,
#                               using=all_plugins,
#                               plugin_path=plugin_path,
#                               cpu_count=-1)
#         # Plot the summaries and report the metrics
#         plugin_concordance_values = return_concordance_value(report)
#         for plugin_name in plugin_concordance_values:
#             plugin_samples = release_data_plugin_data.setdefault(plugin_name, [])
#             plugin_samples.append(plugin_concordance_values[plugin_name])
#         end = default_timer()
#         time_measures.append(end - start)
#         fininishing_time_estimate = round((len(clinvar_samples) - (i + 1)) * mean(time_measures))
#         print(f"Pipeline took {mean(time_measures)}s, Estimated Time to finish: {fininishing_time_estimate}s")
#         print("########################################################")
#         if i % 15 == 0:
#             sample_data_df = build_sample_data_df(time_concordance_plugin_data)
#             mean_concordance_df = build_concordance_statistics_df(sample_data_df)
#             plot_concordance_results(mean_concordance_df)
#     return time_concordance_plugin_data
#
#
# def build_concordance_statistics_df(build_sample_data_df):
#     entries = []
#     dates = build_sample_data_df["Date"].unique()
#     plugin_names = build_sample_data_df["Plugin-Name"].unique()
#     for date in dates:
#         for plugin_name in plugin_names:
#             query = (build_sample_data_df["Date"] == date) & (build_sample_data_df["Plugin-Name"] == plugin_name)
#             plugin_data = build_sample_data_df[query]
#             mean_concordance = plugin_data["Concordance"].mean()
#             std_concordance = plugin_data["Concordance"].std()
#             entry = {"Date": date, "Plugin-Name": plugin_name, "Concordance (AVG)": mean_concordance,
#                      "Concordance (STD)": std_concordance}
#             entries.append(entry)
#     df = pd.DataFrame(entries).sort_values(by="Date")
#     df.to_csv("concordance_statistics.csv", index=False)
#     return df
#
#
# def build_sample_data_df(time_concordance_plugin_data):
#     plugin_data = []
#     # {Data : ReleaseDate,Plugin-Name, Sample-No,Concordance]]}
#     for sample_file_path in time_concordance_plugin_data:
#         for plugin_name in time_concordance_plugin_data[sample_file_path]:
#             concordance_entries = time_concordance_plugin_data[sample_file_path][plugin_name]
#             sample_number = get_clinvar_sample_number(sample_file_path)
#             release_date = get_clinvar_release_date(sample_file_path)
#             for concordance in concordance_entries:
#                 entry = {"Date": release_date, "Sample": sample_number, "Plugin-Name": plugin_name,
#                          "Concordance": concordance}
#                 plugin_data.append(entry)
#     df = pd.DataFrame(plugin_data).sort_values(by=["Date", "Plugin-Name", "Sample"])
#     df.to_csv("sample_concordance.csv", index=False)
#     return df
#
#
# def plot_plugin_concordance(concordance_results, plugin_name, ax):
#     plugin_concordance = concordance_results[concordance_results["Plugin-Name"] == plugin_name]
#     plugin_concordance.plot(kind="line", x="Date", y="Concordance (AVG)", label=plugin_name,
#                             xlabel="Date", ylabel="Concordance (AVG)", ax=ax)  # colums sort
#
#
# def plot_concordance_results(concordance_results):
#     plugin_names = concordance_results["Plugin-Name"].unique()
#     ax = plt.gca()
#     for plugin_name in plugin_names:
#         plot_plugin_concordance(concordance_results, plugin_name, ax)
#     # plt.show()
#     plt.savefig("concordance.png")
#
#
# def check_data_compliance():
#     for everyFile in get_clinvar_releases(samples_path):
#         print(f"Checking: {everyFile}")
#         all_plugins = lambda plugin: True
#         for plugin in load_plugins():
#             data = extract_evaluation_data(everyFile)
#             is_plugin_compatible_with_data(plugin, data)
#
#
# if __name__ == '__main__':
#     time_concordance_plugin_data = create_dictionary_for_concordance_plugin_data()
#     sample_data_df = build_sample_data_df(time_concordance_plugin_data)
#     mean_concordance_df = build_concordance_statistics_df(sample_data_df)
#     plot_concordance_results(mean_concordance_df)
# # result = return_average_of_concordance(time_concordance_plugin_data, year_of_publishing)
#
#
# # plot_python_plugin()
# # plot_concordance_results(export_to_csv(time_concordance_plugin_data))
