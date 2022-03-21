# Spline Spark Agent extension example project

This project serves as an example and a seed project to build your own extensions
for [Spline Spark Agent](https://github.com/AbsaOSS/spline-spark-agent).

## Structure

The project consist of build files and dummy example source code written in Scala.

### `build.sbt`

Here is where you define all metadata about the project:

- version
- project name
- organization name
- supported Scala versions
- etc.

### `/src/main/scala/`

Your Spline agent extension source code goes here. The directory contains examples of how to build a
custom [Post Processing Filter](https://github.com/AbsaOSS/spline-spark-agent#filters)
and a custom [Lineage Dispatcher](https://github.com/AbsaOSS/spline-spark-agent#dispatchers).

Classes `MyFilterWithParams`  and `MyFilterWithSparkSession` shows how to pass configuration parameters and a Spark Session respectively to your
custom filter. **The same technique also works for the lineage dispatcher.**

In order to be instantiated your custom filter or a dispatcher has to define at least one of the following constructors
(listed from the least to the most priority one):
- `this()` &ndash; default no-argument constructor
- `this(c: Configuration)` 
- `this(c: Configuration, spark: SparkSession)` 

You can choose any of those, and you can combine them with other (overloading) constructors at your convenience.

### `/src/test/scala/`

Test suites

## Building

The project requires [SBT](https://www.scala-sbt.org/) tool for building.

### Build final JARs

```shell
sbt clean +assembly
```

or for those using linux

```shell
make
```

The built JAR-files are located in the `target/scala-$VER/` folder, one per given Scala version.

### Clean up

Remove all generated files and build artifacts

```shell
make clean
```

## Usage

1. Add the built JAR-file to the Spark driver classpath using any of available approaches, including but not limited to:
  - Copy the JAR-file to the `$SPARK_HOME/jars/` directory
  - Include it into the `-jars` param of the `spark-submit`, `spark-shell` or `pyspark` command line
  - Unpack the JAR-file and copy its content into your own Spark job fat-JAR, if you have one.

2. Register your component in the config. The majority of custom component types (with exception for _Plugin_ trait) require explicit registering in
   the [Agent configuration](https://github.com/AbsaOSS/spline-spark-agent#configuration).
   See [this section](https://github.com/AbsaOSS/spline-spark-agent#creating-your-own-dispatcher) for example.

---

    Copyright 2022 ABSA Group Limited
    
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
    
        http://www.apache.org/licenses/LICENSE-2.0
    
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
