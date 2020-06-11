/**
 * Copyright 2020 Huawei Technologies Co., Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#ifndef MINDSPORE_DATASET_ITERATOR_TRACING_H
#define MINDSPORE_DATASET_ITERATOR_TRACING_H

#include <string>
#include <vector>
#include "dataset/engine/perf/profiling.h"

namespace mindspore {
namespace dataset {
class DatasetIteratorTracing : public Tracing {
 public:
  // Constructor
  DatasetIteratorTracing() = default;

  // Destructor
  ~DatasetIteratorTracing() = default;

  // Record tracing data
  // @return Status - The error code return
  Status Record(const int32_t type, const int32_t extra_info, const int32_t batch_num, const int32_t value);

  std::string Name() const override { return kDatasetIteratorTracingName; };

  // Save tracing data to file
  // @return Status - The error code return
  Status SaveToFile() override;

  Status Init(const std::string &dir_path, const std::string &device_id);

 private:
  std::vector<std::string> value_;
};
}  // namespace dataset
}  // namespace mindspore

#endif  // MINDSPORE_DATASET_ITERATOR_TRACING_H
