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

#ifndef MINDSPORE_CORE_C_OPS_L2NORMALIZE_H_
#define MINDSPORE_CORE_C_OPS_L2NORMALIZE_H_
#include <vector>
#include <memory>

#include "c_ops/primitive_c.h"
#include "c_ops/op_utils.h"
#include "abstract/abstract_value.h"
#include "utils/check_convert_utils.h"

namespace mindspore {
constexpr auto kNameL2Normalize = "L2Normalize";
class L2Normalize : public PrimitiveC {
 public:
  L2Normalize() : PrimitiveC(kNameL2Normalize) {}
  ~L2Normalize() = default;
  MS_DECLARE_PARENT(L2Normalize, PrimitiveC);
  void Init(int64_t axis = 0, float epsilon = 1e-4);
  void set_axis(int64_t axis);
  void set_epsilon(float epsilon);
  int64_t get_axis();
  float get_epsilon();
};
AbstractBasePtr L2NormalizeInfer(const abstract::AnalysisEnginePtr &, const PrimitivePtr &primitive,
                                 const std::vector<AbstractBasePtr> &input_args);
using PrimL2Normalize = std::shared_ptr<L2Normalize>;
}  // namespace mindspore
#endif  // MINDSPORE_CORE_C_OPS_L2NORMALIZE_H_
