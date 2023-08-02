/*
 * Copyright 2022 ABSA Group Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.example

import org.apache.commons.configuration.MapConfiguration
import org.apache.spark.SparkContext
import org.apache.spark.sql.SparkSession
import org.mockito.Mockito.when
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers
import org.scalatestplus.mockito.MockitoSugar
import za.co.absa.spline.HierarchicalObjectFactory
import za.co.absa.spline.agent.AgentConfig.ConfProperty

import scala.collection.JavaConverters._

class MyFilterWithSparkSessionSpec extends AnyFlatSpec with Matchers with MockitoSugar {
  "My custom filter" should "get access to Spark Session" in {
    val filterName = "mySparkAwareFilter"
    val sparkMock = mock[SparkSession]
    val contextMock = mock[SparkContext]

    when(sparkMock.sparkContext) thenReturn contextMock
    when(contextMock.appName) thenReturn "My Awesome Application"

    val config = new MapConfiguration(Map(
      "spline.postProcessingFilter" -> filterName,
      s"spline.postProcessingFilter.$filterName.className" -> classOf[MyFilterWithSparkSession].getName,
      s"spline.postProcessingFilter.$filterName.foo" -> "awesome",
      s"spline.postProcessingFilter.$filterName.bar" -> "42"
    ).asJava)

    val factory =
      new HierarchicalObjectFactory(config, sparkMock)
        .child(ConfProperty.RootPostProcessingFilter)
        .child(filterName)

    val myFilter = factory.instantiate[MyFilterWithSparkSession]()

    myFilter.sparkAppName should equal("My Awesome Application")
  }
}
