#!/usr/bin/env python3
import subprocess
import docker
import os

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

def run_arangodb() -> str:
    print(f"Running arango db in docker")
    img = client.images.pull("arangodb/arangodb", tag="3.9.2")
    variables = ["ARANGO_NO_AUTH=1"]
    container = client.containers.run(img, environment=variables, ports={"8529/tcp": "8529"}, detach=True)
    print(f"ArangoDB started as docker container, with ID {container.id}")

    return container.id


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


def init_arango():
    print("Initializing spline DB in arangoDB.")
    subprocess.run(RUN_ARANGODB_SPLINE_INIT)
    print("DB initialization finished")


def run_spline_in_docker():
    os.chdir(f"{root_dir}/spline/rest-gateway")
    print(f"Building Spline docker image from dir {os.getcwd()}")
    (img, build_logs) = client.images.build(path=".", tag="spline_for_docker")
    print(f"Running Spline docker image {img.id}")
    container = client.containers.run(img, ports={"8080/tcp": "8080", "8009/tcp": "8009"}, detach=True)
    print(f"Spline started as docker container, with ID {container.id}")

    # backend should be running at http://localhost:8080/spline-rest-server-1.0.0-SNAPSHOT/

if __name__ == '__main__':
    client = docker.from_env()
    root_dir = os.getcwd()

    run_arangodb()
    build_spline()
    init_arango()
    run_spline_in_docker()

    # kill arango
    # TODO

    # spline codebase cleanup
    # TODO


