#!/usr/bin/env python3
import subprocess
import docker
import os
import time

RUN_ARANGODB_DOCKER = "docker run -p 8529:8529 -e ARANGO_NO_AUTH=1 arangodb/arangodb:3.9.2"

GIT_CLONE_SPLINE = "git clone git@github.com:AbsaOSS/spline.git"
GIT_CHEKOUT_SPLINE_BRANCH = "git checkout {branch}"
RUN_ARANGODB_SPLINE_INIT = "java -jar ./admin/target/admin-1.0.0-SNAPSHOT.jar db-init arangodb://localhost/spline"

# or install??
# todo alternate mvn.cmd for mvn for non-windows
SPLINE_BUILD = "mvn.cmd install -DskipTests"
BUILD_SPLINE_FOR_DOCKER = "docker build -t spline_for_docker"

# populated in main
# client =
# root_dir =


def build_spline(branch: str = "develop"):
    print(f"Getting spline (via: '{GIT_CLONE_SPLINE}')")
    subprocess.run(GIT_CLONE_SPLINE)

    print(f"Current working directory: {os.getcwd()}")
    print("Changing current working directory...")
    os.chdir(f"{root_dir}/spline")
    print(f"Current working directory: {os.getcwd()}")


    complete_command = GIT_CHEKOUT_SPLINE_BRANCH.format(branch=branch)
    print(f"Checking out spline codebase - branch {branch} (via: '{complete_command}')")
    subprocess.run(complete_command)

    print("Building spline:")
    subprocess.run(SPLINE_BUILD)

    print("Spline build complete.")


def run_docker_compose() -> object:
    os.chdir(root_dir)
    # subprocess.run("docker-compose up", )

    handle = subprocess.Popen('docker-compose up'.split())  # continue immediately
    time.sleep(20)  # timeout to start the services
    print("docker compose up done")
    return handle


def cleanup_docker_compose():
    handle = subprocess.Popen('docker-compose down'.split())
    # todo cleanup images?
    # handle.terminate()
    # handle.wait()

    print("docker compose down done")


if __name__ == '__main__':
    client = docker.from_env()
    root_dir = os.getcwd()
    spine_branch = "feature/adding-curl-rest-gw-docker"

    #build_spline(spine_branch)  # TODO use develop when merged?
    run_docker_compose()

    #cleanup_docker_compose()

    print("DONE")

