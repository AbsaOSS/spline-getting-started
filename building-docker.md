**Note**: All Spline runnable components are available as Docker images on [Docker Hub](https://hub.docker.com/search?q=absaoss%2Fspline&type=image)

---
## How to build Spline Docker images

The build process is standardized across Spline components.
Every runnable component has a standard _Dockerfile_. 
Although you can use a build tool of your choice if you prefer, we recommend to use Apache Maven.

Our Docker build process leverages [Spotify Dockerfile Maven plugin](https://github.com/spotify/dockerfile-maven)

One project may have multiple _Dockerfiles_ and hence multiple Docker images will be produced in the build process.

### Steps

1. Install [Java](https://adoptopenjdk.net/) (version 11 is recommended except for the _Spark Agent_ which strictly requires Java 1.8)
1. Install [Apache Maven](https://maven.apache.org/) (version 3.6+ is recommended)
1. Pull the Spline component project that you want to build.
    ```shell
    git clone https://github.com/AbsaOSS/{spline_repo_of_choice}.git
    ```
1. From the project root directory, run Maven build command with the `docker` profile enabled, specifying required properties (see below):
    ```shell
    mvn install \
      -D skipTests \                  # Skip unit and integration tests
      -P docker \                     # Activate "docker" profile
      -D dockerfile.repositoryUrl=my  # The name prefix of the final Docker image(s)
    ```
Done.

The above command produces docker images with the name `my/{spline_image_name}` tagged as `{project_version}` and `latest`

You can verify that docker images were created:
```shell
docker image ls | grep spline
```

### Customizing image names and tags

By default, you have to provide `dockerfile.repositoryUrl` that is used to specify the target repo that is also used as a name prefix for images.

Instead of `dockerfile.repositoryUrl` you can also use `dockerfile.repositoryPrefix` and optionally `dockerfile.repositorySuffix`
for more precise control on image naming.
For example, the following arguments will create an image with the name `x/y/z/aaa{spline_image_name}bbb`
```shell
  -D dockerfile.repositoryPrefix=x/y/z/aaa
  -D dockerfile.repositorySuffix=bbb
```
 
Similarly, you can add custom prefixes and/or suffixes to the tag names.
For instance, adding the following arguments to the command line would result in tagging the images as `foo_1.2.3_bar` instead of just `1.2.3`:
```shell
  -D dockerfile.versionTagPrefix=foo_
  -D dockerfile.versionTagSuffix=_bar
```

To override tag names completely you can add the following arguments:
```shell
  -D dockerfile.versionTagName=aaa  # renames '{project_version}' tag to 'aaa'
  -D dockerfile.latestTagName=bbb   # renames 'latest' tag to 'bbb'
```

### Customizing base image names

There are cases when it's preferable to pull the base images from a custom repo, and sometimes using custom image name prefixes.

For example, if a _Dockerfile_ is based on `adoptopenjdk/openjdk11:jdk-11.0.10_9-alpine-slim` 
and you want to pull it as `foo/bar/baz-adoptopenjdk/openjdk11:jdk-11.0.10_9-alpine-slim`
you can do the following:

```shell
  -D dockerfile.baseImagePrefix=foo/bar/baz-
```

See https://github.com/AbsaOSS/spline-root-pom/blob/main/pom.xml for details.

### Pushing to the Docker repo

Use `mvn deploy` instead of `mvn install` is you want the images to be also pushed.  


---

    Copyright 2019 ABSA Group Limited

    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
