#!/usr/bin/env python3
import argparse
import subprocess
import docker
import os
import platform
import pandas as pd
import matplotlib.pyplot as plt
import git

GIT_SPLINE_URL = "https://github.com/AbsaOSS/spline.git"
SPLINE_DEFAULT_BRANCH = "develop"

SPLINE_CORE_VERSION = "1.0.0-SNAPSHOT"  # needs to be in sync with .env
CUSTOM_IMAGES = [f"testing-spline-db-admin:{SPLINE_CORE_VERSION}", f"testing-spline-rest-server:{SPLINE_CORE_VERSION}"]

SPLINE_BUILD = "{mvn} install -DskipTests"

JMETER_COLNAME_TIMESTAMP = "timeStamp"
JMETER_COLNAME_ELAPSED = "elapsed"
JMETER_COLNAME_LABEL = "label"
# coming from Jmeter, but custom-added (graphType,operationCount,attributeCount,readCount)
JMETER_COLNAME_GRAPH_TYPE = "graphType"
JMETER_COLNAME_OP_COUNT = "operationCount"
JMETER_COLNAME_ATTR_COUNT = "attributeCount"
JMETER_COLNAME_READ_COUNT = "readCount"

# script folders:
RESULTS_FOLDER_NAME = "results"
REFERENCE_FOLDER_NAME = "reference"
PROCESSED_FOLDER_NAME = "processed_results"
GRAPHS_FOLDER_NAME = "graphs"

# Matplotlib:
PLOT_MARKER = "o"
PLOT_MARKER_SIZE = 2
PLOT_DPI = 300


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='run_jmetered_spline',
        description='Spline backend simple testing (jmetered)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter  # prints default values, too, on help (-h)
    )

    parser.add_argument('-n', '--no-rebuild', action='store_true', dest="no_rebuild", default=False,
                        help="if specified, spline will not be rebuilt (use when rerunning on an existing codebase)")
    # parser.add_argument('-v', '--verbose', action="store_true", default=False,
    #                     help="prints extra information while running.")

    parser.add_argument('-b', '--spline-branch', dest="spline_branch", default=SPLINE_DEFAULT_BRANCH,
                        help="Name of spline branch to test")

    return parser.parse_args()


def get_mvn_by_os() -> str:
    if platform.system() == "Windows":
        return "mvn.cmd"
    else:
        return "mvn"


def build_spline(branch):
    spline_dir = f"{root_dir}/spline"

    if not os.path.exists(spline_dir):
        print(f"Cloning Spline into {spline_dir} (branch {branch})")
        git.Repo.clone_from(GIT_SPLINE_URL, spline_dir, branch=branch)
    else:
        print(f"Pulling Spline into {spline_dir} (branch {branch})")
        repo = git.Repo(spline_dir)
        repo.remotes[0].pull()

    os.chdir(f"{root_dir}/spline")
    print(f"Current working directory: {os.getcwd()}")

    mvn = get_mvn_by_os()
    spline_build_command = SPLINE_BUILD.format(mvn=mvn)
    print(f"Building spline via '{spline_build_command}'")
    subprocess.run(spline_build_command, shell=True, check=True)


def run_docker_compose():
    os.chdir(root_dir)
    os.makedirs(f"{root_dir}/{RESULTS_FOLDER_NAME}", exist_ok=True)
    # --exit-code-from = reports exit code from this container
    # AND implies '--abort-on-container-exit' - will 'docker-compose down' after any container has exited
    subprocess.run("docker-compose up --exit-code-from jmeter", shell=True, check=True)
    print("docker-compose up done")


def cleanup_docker():
    client = docker.from_env()

    for image_name in CUSTOM_IMAGES:
        print(f"Cleaning up custom image '{image_name}'")
        try:
            client.images.remove(image_name, force=True)
            print(" - done")
        except docker.errors.ImageNotFound as inf:
            print(f" - custom image custom image '{image_name}' not found!")

    print("docker-compose cleanup finished")


def enrich_results_with_reference():
    result_filenames = os.listdir(f"{root_dir}/{RESULTS_FOLDER_NAME}")
    os.makedirs(f"{root_dir}/{PROCESSED_FOLDER_NAME}", exist_ok=True)
    for result_filename in result_filenames:
        reference_df = pd.read_csv(f"./{REFERENCE_FOLDER_NAME}/{result_filename}")
        reference_df[JMETER_COLNAME_LABEL] = reference_df[JMETER_COLNAME_LABEL].map(lambda x: f"reference {x}")  # in-place
        normalized_reference_df = normalize_dataframe_timestamp(reference_df)

        results_df = pd.read_csv(f"./{RESULTS_FOLDER_NAME}/{result_filename}")
        normalized_results_df = normalize_dataframe_timestamp(results_df)

        joined_df = pd.concat([normalized_reference_df, normalized_results_df])

        joined_df.to_csv(f"./{PROCESSED_FOLDER_NAME}/{result_filename}", index=False)


def normalize_dataframe_timestamp(df: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    min_ts = df[JMETER_COLNAME_TIMESTAMP].min()
    normalized_df = df.copy()  # deep copy for the fn to behave immutably
    normalized_df[JMETER_COLNAME_TIMESTAMP] = normalized_df[JMETER_COLNAME_TIMESTAMP].map(lambda x: x - min_ts)
    return normalized_df


def divide_df_ref_and_non_ref(df: pd.core.frame.DataFrame) -> list[pd.core.frame.DataFrame]:
    ref_df = df[df['label'].str.startswith("reference")]
    nonref_df = df[~df['label'].str.startswith("reference")]

    return [ref_df, nonref_df]


def divide_plan_and_event(df: pd.core.frame.DataFrame) -> list[pd.core.frame.DataFrame]:
    plan_df = df[df['label'].str.endswith("plan")]
    non_plan_df = df[~df['label'].str.endswith("plan")]

    return [plan_df, non_plan_df]


def find_variable_column_name(df: pd.core.frame.DataFrame) -> str:
    unique_ops, unique_attrs, unique_reads = df[[JMETER_COLNAME_OP_COUNT, JMETER_COLNAME_ATTR_COUNT, JMETER_COLNAME_READ_COUNT]].nunique().values.tolist()
    # debug print(f"uniques: {unique_ops}, {unique_attrs}, {unique_reads}")

    if unique_ops > 1:
        print(f"  Using variable column '{JMETER_COLNAME_OP_COUNT}' (nuniques = {unique_ops})")
        return JMETER_COLNAME_OP_COUNT
    elif unique_attrs > 1:
        print(f"  Using variable column '{JMETER_COLNAME_ATTR_COUNT}' (nuniques = {unique_attrs})")
        return JMETER_COLNAME_ATTR_COUNT
    elif unique_reads > 1:
        print(f"  Using variable column '{JMETER_COLNAME_READ_COUNT}' (nuniques = {unique_reads})")
        return JMETER_COLNAME_READ_COUNT
    else:
        print(f"  Fall-backing variable column to '{JMETER_COLNAME_TIMESTAMP}'")
        return JMETER_COLNAME_TIMESTAMP


def generate_graph_from_processed_result(result_filename: str):

    # rereading the results file, because we want the graph drawing process to be independent from the processing part
    all_data = pd.read_csv(f"./{PROCESSED_FOLDER_NAME}/{result_filename}")
    ref_df, res_df = divide_df_ref_and_non_ref(all_data)

    ref_plan_df, ref_event_df = divide_plan_and_event(ref_df)
    res_plan_df, res_event_df = divide_plan_and_event(res_df)

    var_colname = find_variable_column_name(all_data)  # operationCount,attributeCount,readCount or (worst-case) timeStamp

    plt.clf() # clear previous state if any
    plt.yscale("log")  # because initial values tend to be outliers

    ref_plan_elapsed = ref_plan_df[JMETER_COLNAME_ELAPSED].tolist()
    ref_plan_var = ref_plan_df[var_colname].tolist()
    plt.plot(ref_plan_var, ref_plan_elapsed, marker=PLOT_MARKER, markersize=PLOT_MARKER_SIZE, label="Reference lineage plan posting")

    res_plan_elapsed = res_plan_df[JMETER_COLNAME_ELAPSED].tolist()
    res_plan_var = res_plan_df[var_colname].tolist()
    plt.plot(res_plan_var, res_plan_elapsed, marker=PLOT_MARKER, markersize=PLOT_MARKER_SIZE, label="Current lineage plan posting")

    ref_event_elapsed = ref_event_df[JMETER_COLNAME_ELAPSED].tolist()
    ref_event_var = ref_event_df[var_colname].tolist()
    plt.plot(ref_event_var, ref_event_elapsed, marker=PLOT_MARKER, markersize=PLOT_MARKER_SIZE, label="Reference lineage event posting")

    res_event_elapsed = res_event_df[JMETER_COLNAME_ELAPSED].tolist()
    res_event_var = res_event_df[var_colname].tolist()
    plt.plot(res_event_var, res_event_elapsed, marker=PLOT_MARKER, markersize=PLOT_MARKER_SIZE, label="Current lineage event posting")

    plt.xlabel(f"Variable '{var_colname}'")
    plt.ylabel('Elapsed time [ms]')
    plt.title(f"Elapsed time dependence on variable '{var_colname}'")
    plt.legend()

    # debug:
    # print(f"ref_plan_var={ref_plan_var}")
    # print(f"res_plan_var={res_plan_var}")
    # print(f"ref_event_var={ref_event_var}")
    # print(f"res_event_var={res_event_var}")
    
    plt.savefig(f"{root_dir}/{GRAPHS_FOLDER_NAME}/{result_filename}.png", dpi=PLOT_DPI)


def generate_graphs():
    result_filenames = os.listdir(f"{root_dir}/{PROCESSED_FOLDER_NAME}")
    os.makedirs(f"{root_dir}/{GRAPHS_FOLDER_NAME}", exist_ok=True)

    # rereading the results file, because we want the graph drawing process to be independent from the processing part
    for result_filename in result_filenames:
        print(f"Generating graph for file {PROCESSED_FOLDER_NAME}/{result_filename}")
        generate_graph_from_processed_result(result_filename)


def run(parsed_args: argparse.Namespace):
    spline_branch = parsed_args.spline_branch
    no_rebuild = parsed_args.no_rebuild

    if not no_rebuild:
        build_spline(spline_branch)

    run_docker_compose()

    enrich_results_with_reference()
    generate_graphs()

    cleanup_docker()

    print("All testing done.")


if __name__ == '__main__':
    args = parse_args()

    # globals script vars
    root_dir = os.getcwd()

    run(args)
