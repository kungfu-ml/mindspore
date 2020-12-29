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

#ifndef MINDSPORE_CORE_C_OPS_BROADCAST_H_
#define MINDSPORE_CORE_C_OPS_BROADCAST_H_
#include <string>

#include "c_ops/primitive_c.h"
#include "abstract/abstract_value.h"
#include "utils/check_convert_utils.h"

namespace mindspore {
constexpr auto kNameBroadcast = "Broadcast";
class Broadcast : public PrimitiveC {
 public:
  Broadcast() : PrimitiveC(kNameBroadcast) {}
  ~Broadcast() = default;
  MS_DECLARE_PARENT(Broadcast, PrimitiveC);
  void Init(int64_t root_rank, const std::string &group = "hccl_world_group");
  void set_root_rank(int64_t root_rank);
  void set_group(const std::string &group);
  int64_t get_root_rank();
  std::string get_group() const;
};
}  // namespace mindspore

#endif  // MINDSPORE_CORE_C_OPS_BROADCAST_H_
