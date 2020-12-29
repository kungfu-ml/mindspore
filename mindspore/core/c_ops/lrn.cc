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

#include "c_ops/lrn.h"
#include <string>
#include <algorithm>
#include <memory>
#include <set>
#include <vector>
#include "c_ops/op_utils.h"
#include "utils/check_convert_utils.h"
#include "abstract/primitive_infer_map.h"

namespace mindspore {
void Lrn::set_depth_radius(const int64_t &depth_radius) {
  CheckAndConvertUtils::CheckInteger(kDepthRadius, depth_radius, kGreaterEqual, 0, this->name());
  this->AddAttr(kDepthRadius, MakeValue(depth_radius));
}

int64_t Lrn::get_depth_radius() const {
  auto value_ptr = GetAttr(kDepthRadius);
  return GetValue<int64_t>(value_ptr);
}

void Lrn::set_bias(const float &bias) { this->AddAttr(kBias, MakeValue(bias)); }

float Lrn::get_bias() const {
  auto value_ptr = GetAttr(kBias);
  return GetValue<float>(value_ptr);
}

void Lrn::set_alpha(const float &alpha) { this->AddAttr(kAlpha, MakeValue(alpha)); }

float Lrn::get_alpha() const {
  auto value_ptr = GetAttr(kAlpha);
  return GetValue<float>(value_ptr);
}

void Lrn::set_beta(const float &beta) { this->AddAttr(kBeta, MakeValue(beta)); }

float Lrn::get_beta() const {
  auto value_ptr = GetAttr(kBeta);
  return GetValue<float>(value_ptr);
}
void Lrn::set_norm_region(const std::string &norm_region) {
  CheckAndConvertUtils::CheckString(kNormRegion, norm_region, {"ACROSS_CHANNELS"}, this->name());
  this->AddAttr(kNormRegion, MakeValue(norm_region));
}

std::string Lrn::get_norm_region() const {
  auto value_ptr = GetAttr(kNormRegion);
  return GetValue<std::string>(value_ptr);
}
void Lrn::Init(const int64_t &depth_radius, const float &bias, const float &alpha, const float &beta,
               const std::string &norm_region) {
  this->set_depth_radius(depth_radius);
  this->set_bias(bias);
  this->set_alpha(alpha);
  this->set_beta(beta);
  this->set_norm_region(norm_region);
}
REGISTER_PRIMITIVE_C(kNameLrn, Lrn);
}  // namespace mindspore
