import Dependencies.*

lazy val scala212 = "2.12.15"
lazy val scala211 = "2.11.12"
lazy val supportedScalaVersions = Seq(scala212, scala211)

ThisBuild / version := "0.1.0-SNAPSHOT"
ThisBuild / organization := "org.example"
ThisBuild / organizationName := "example"

lazy val root = (project in file("."))
  .settings(
    name := "MySplineExtras",
    crossScalaVersions := supportedScalaVersions,
    assembly / assemblyJarName := s"${name.value}_${scalaBinaryVersion.value}-${version.value}.jar",
    assembly / assemblyOption ~= (_.withIncludeScala(false)),
    libraryDependencies ++= Seq(
      splineAgentCore % Provided,
      scalaTest % Test,
      scalatestplus % Test,
    )
  )
