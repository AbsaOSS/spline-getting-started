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

import org.apache.spark.sql.SparkSession
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers
import za.co.absa.commons.HierarchicalObjectFactory
import za.co.absa.spline.harvester.conf.DefaultSplineConfigurer.ConfProperty
import za.co.absa.spline.harvester.conf.StandardSplineConfigurationStack

class MyFilterWithSparkSessionSpec extends AnyFlatSpec with Matchers {
  "My custom filter" should "get access to Spark Session" in {
    val filterName = "mySparkAwareFilter"
    val spark = SparkSession.builder
      .master("local")
      .appName("My Awesome Application")
      .config("spark.spline.postProcessingFilter", filterName)
      .config(s"spark.spline.postProcessingFilter.$filterName.className", classOf[MyFilterWithSparkSession].getName)
      .getOrCreate()

    val factory =
      new HierarchicalObjectFactory(StandardSplineConfigurationStack(spark), spark)
        .child(ConfProperty.RootPostProcessingFilter)
        .child(filterName)

    val myFilter = factory.instantiate[MyFilterWithSparkSession]()
    myFilter.sparkAppName should equal("My Awesome Application")
  }
}
