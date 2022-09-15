#!/usr/bin/env python3
import subprocess
import docker
import os
import platform
import pandas as pd

GIT_CLONE_SPLINE = "git clone git@github.com:AbsaOSS/spline.git"
GIT_CHEKOUT_SPLINE_BRANCH = "git checkout {branch}"

SPLINE_CORE_VERSION = "1.0.0-SNAPSHOT"  # needs to be in sync with .env
CUSTOM_IMAGES = [f"testing-spline-db-admin:{SPLINE_CORE_VERSION}", f"testing-spline-rest-server:{SPLINE_CORE_VERSION}"]

SPLINE_BUILD = "{mvn} install -DskipTests"

JMETER_TIMESTAMP_COLNAME = "timeStamp"
JMETER_LABEL_COLNAME = "label"

# script folders:
RESULTS_FOLDER_NAME = "results"
REFERENCE_FOLDER_NAME = "reference"
PROCESSED_FOLDER_NAME = "processed_results"
GRAPHS_FOLDER_NAME = "graphs"

# populated in main
# client =
# root_dir =
# mvn =


def get_mvn_by_os() -> str:
    if platform.system() == "Windows":
        return "mvn.cmd"
    else:
        return "mvn"


def build_spline(branch: str = "develop"):
    print(f"Getting spline (via: '{GIT_CLONE_SPLINE}')")
    subprocess.run(GIT_CLONE_SPLINE)

    print(f"Current working directory: {os.getcwd()}")
    print("Changing current working directory...")
    os.chdir(f"{root_dir}/spline")
    print(f"Current working directory: {os.getcwd()}")


    checkout_spline_command = GIT_CHEKOUT_SPLINE_BRANCH.format(branch=branch)
    print(f"Checking out spline codebase - branch {branch} (via: '{checkout_spline_command}')")
    subprocess.run(checkout_spline_command)

    mvn = get_mvn_by_os()
    spline_build_command = SPLINE_BUILD.format(mvn=mvn)
    print(f"Building spline via '{spline_build_command}'")
    subprocess.run(spline_build_command)

    print("Spline build complete.")


def run_docker_compose():
    os.chdir(root_dir)
    # --exit-code-from = reports exit code from this container
    # AND implies '--abort-on-container-exit' - will 'docker-compose down' after any container has exited
    subprocess.run("docker-compose up --exit-code-from jmeter")
    print("docker-compose up done")


def cleanup_docker():
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
        reference_df[JMETER_LABEL_COLNAME] = reference_df[JMETER_LABEL_COLNAME].map(lambda x: f"reference {x}")  # in-place
        normalized_reference_df = normalize_dataframe_timestamp(reference_df)

        results_df = pd.read_csv(f"./{RESULTS_FOLDER_NAME}/{result_filename}")
        normalized_results_df = normalize_dataframe_timestamp(results_df)

        joined_df = pd.concat([normalized_reference_df, normalized_results_df])

        joined_df.to_csv(f"./{PROCESSED_FOLDER_NAME}/{result_filename}", index=False)


def normalize_dataframe_timestamp(df: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    min_ts = df[JMETER_TIMESTAMP_COLNAME].min()
    normalized_df = df.copy()  # deep copy for the fn to behave immutably
    normalized_df[JMETER_TIMESTAMP_COLNAME] = normalized_df[JMETER_TIMESTAMP_COLNAME].map(lambda x: x - min_ts)
    return normalized_df


def generate_graphs():
    result_filenames = os.listdir(f"{root_dir}/{PROCESSED_FOLDER_NAME}")
    os.makedirs(f"{root_dir}/{GRAPHS_FOLDER_NAME}", exist_ok=True)
    for result_filename in result_filenames:
        # TODO nicify or read from .env file?
        NAME="jmeter"
        JMETER_VERSION="5.4"
        IMAGE=f"justb4/jmeter:{JMETER_VERSION}"
        PWD=os.getcwd()
        subprocess.run(f'docker run --rm --name {NAME} -v {PWD}:/var/jmeter -w /var/jmeter {IMAGE} -J"user.properties=/var/jmeter/user.properties" -g {PROCESSED_FOLDER_NAME}/{result_filename} -o {GRAPHS_FOLDER_NAME}/{result_filename}')


if __name__ == '__main__':
    client = docker.from_env()
    root_dir = os.getcwd()
    spine_branch = "feature/adding-curl-rest-gw-docker"

    build_spline(spine_branch)  # TODO use develop when merged?
    run_docker_compose()

    enrich_results_with_reference()
    generate_graphs()

    cleanup_docker()

    print("ALL DONE")

