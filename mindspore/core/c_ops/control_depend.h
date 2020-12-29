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

#ifndef MINDSPORE_CORE_C_OPS_CONTROL_DEPEND_H_
#define MINDSPORE_CORE_C_OPS_CONTROL_DEPEND_H_
#include <vector>
#include <memory>

#include "c_ops/primitive_c.h"
#include "c_ops/op_utils.h"
#include "abstract/abstract_value.h"
#include "utils/check_convert_utils.h"

namespace mindspore {
constexpr auto kNameControlDepend = "ControlDepend";
class ControlDepend : public PrimitiveC {
 public:
  ControlDepend() : PrimitiveC(kNameControlDepend) {}
  ~ControlDepend() = default;
  MS_DECLARE_PARENT(ControlDepend, PrimitiveC);
  void Init(int64_t depend_mode);
  void set_depend_mode(int64_t depend_mode);
  int64_t get_depend_mode();
};
AbstractBasePtr ControlDependInfer(const abstract::AnalysisEnginePtr &, const PrimitivePtr &primitive,
                                   const std::vector<AbstractBasePtr> &input_args);
using PrimControlDepend = std::shared_ptr<ControlDepend>;
}  // namespace mindspore
#endif  // MINDSPORE_CORE_C_OPS_CONTROl_DEPEND_H_
