import sbt.*

object Dependencies {
  lazy val splineAgentCore = "za.co.absa.spline.agent.spark" %% "agent-core" % "2.0.0"
  lazy val scalaTest = "org.scalatest" %% "scalatest" % "3.2.15"
  lazy val scalatestplus = "org.scalatestplus" %% "mockito-1-10" % "3.1.0.0"
}
