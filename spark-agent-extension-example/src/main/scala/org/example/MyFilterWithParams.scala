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

import org.apache.commons.configuration.Configuration
import org.apache.spark.internal.Logging
import org.example.MyFilterWithParams.ConfProps
import za.co.absa.commons.config.ConfigurationImplicits._
import za.co.absa.spline.harvester.postprocessing.AbstractPostProcessingFilter


object MyFilterWithParams {
  object ConfProps {
    val Foo = "foo"
    val Bar = "bar"
  }
}

class MyFilterWithParams(val foo: String, val bar: Int)
  extends AbstractPostProcessingFilter("My Filter With Parameters")
    with Logging {

  def this(c: Configuration) = this(
    c.getRequiredString(ConfProps.Foo),
    c.getRequiredInt(ConfProps.Bar)
  )

  log.info(s"My custom filter created: foo=$foo, bar=$bar")
}
