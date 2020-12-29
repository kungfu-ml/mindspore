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

#include "c_ops/fake_quant_with_min_max_vars.h"
#include "c_ops/op_utils.h"
#include "utils/check_convert_utils.h"
#include "abstract/primitive_infer_map.h"

namespace mindspore {
void FakeQuantWithMinMaxVars::Init(const bool &narrow_range, int64_t num_bits) {
  this->set_narrow_range(narrow_range);
  this->set_num_bits(num_bits);
}

void FakeQuantWithMinMaxVars::set_narrow_range(const bool &narrow_range) {
  this->AddAttr(kNarrowRange, MakeValue(narrow_range));
}

bool FakeQuantWithMinMaxVars::get_narrow_range() const {
  auto value_ptr = this->GetAttr(kNarrowRange);
  return GetValue<bool>(value_ptr);
}

void FakeQuantWithMinMaxVars::set_num_bits(int64_t num_bits) { this->AddAttr(kNumBits, MakeValue(num_bits)); }

int64_t FakeQuantWithMinMaxVars::get_num_bits() const {
  auto value_ptr = this->GetAttr(kNumBits);
  return GetValue<int64_t>(value_ptr);
}
REGISTER_PRIMITIVE_C(kNameFakeQuantWithMinMaxVars, FakeQuantWithMinMaxVars);
}  // namespace mindspore
