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

import org.apache.spark.internal.Logging
import za.co.absa.spline.harvester.HarvestingContext
import za.co.absa.spline.harvester.postprocessing.AbstractPostProcessingFilter
import za.co.absa.spline.producer.model._

class MyFilter
  extends AbstractPostProcessingFilter("My Filter")
    with Logging {

  log.info("My custom filter created")

  // Only override and implement methods that you need...

  override def processExecutionEvent(event: ExecutionEvent, ctx: HarvestingContext): ExecutionEvent = event

  override def processExecutionPlan(plan: ExecutionPlan, ctx: HarvestingContext): ExecutionPlan = plan

  override def processReadOperation(op: ReadOperation, ctx: HarvestingContext): ReadOperation = op

  override def processWriteOperation(op: WriteOperation, ctx: HarvestingContext): WriteOperation = op

  override def processDataOperation(op: DataOperation, ctx: HarvestingContext): DataOperation = op
}
