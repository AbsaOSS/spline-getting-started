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


# def init_arango():
#     print("Initializing spline DB in arangoDB.")
#     os.chdir(f"{root_dir}/spline")
#     subprocess.run(RUN_ARANGODB_SPLINE_INIT)
#     print("DB initialization finished")


# def run_spline_in_docker():
    # os.chdir(f"{root_dir}/spline/rest-gateway")
    # print(f"Building Spline docker image from dir {os.getcwd()}")
    # buildargs = ["PROJECT_BUILD_FINAL_NAME=spline-rest-server-1.0.0-SNAPSHOT"]
    # (img, build_logs) = client.images.build(path=".", buildargs=buildargs, tag="spline_for_docker")  # this hangs, but I don't know why
    # print(f"Running Spline docker image {img.id}")
    #
    #
    # variables = ["SPLINE_DATABASE_CONNECTION_URL=arangodb://172.17.0.1/spline"]
    # container = client.containers.run(img, environment=variables, ports={"8080/tcp": "8080", "8009/tcp": "8009"}, detach=True)
    # print(f"Spline started as docker container, with ID {container.id}")

    # backend should be running at http://localhost:8080/spline-rest-server-1.0.0-SNAPSHOT/


def run_docker_compose():
    os.chdir(root_dir)
    # subprocess.run("docker-compose up", )

    etcd = subprocess.Popen('docker-compose up'.split())  # continue immediately
    # next_cmd_returncode = subprocess.call('next_cmd')  # wait for it
    # ... run more python here ...
    print(etcd)

    time.sleep(200)  # TODO replace with run of measurement
    etcd.terminate()
    etcd.wait()


    print("docker compose up done")
    # or just "docker-compose down"

if __name__ == '__main__':
    client = docker.from_env()
    root_dir = os.getcwd()

    #run_arangodb() # remove

    spine_branch = "feature/adding-curl-rest-gw-docker"
    build_spline(spine_branch)  # TODO use develop when merged?

    #init_arango() # remove
    #run_spline_in_docker() # remove
    run_docker_compose()

    # kill arango
    # TODO

    # spline codebase cleanup
    # TODO


