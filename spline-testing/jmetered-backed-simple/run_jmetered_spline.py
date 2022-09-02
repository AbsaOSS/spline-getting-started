#!/usr/bin/env python3
import subprocess
import docker
import os
import platform

GIT_CLONE_SPLINE = "git clone git@github.com:AbsaOSS/spline.git"
GIT_CHEKOUT_SPLINE_BRANCH = "git checkout {branch}"

SPLINE_CORE_VERSION = "1.0.0-SNAPSHOT"  # needs to be in sync with .env
CUSTOM_IMAGES = [f"testing-spline-db-admin:{SPLINE_CORE_VERSION}", f"testing-spline-rest-server:{SPLINE_CORE_VERSION}"]

SPLINE_BUILD = "{mvn} install -DskipTests"

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


if __name__ == '__main__':
    client = docker.from_env()
    root_dir = os.getcwd()
    spine_branch = "feature/adding-curl-rest-gw-docker"

    build_spline(spine_branch)  # TODO use develop when merged?
    run_docker_compose()

    cleanup_docker()

    print("ALL DONE")

