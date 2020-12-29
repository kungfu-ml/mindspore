/**
 * Copyright 2019-2020 Huawei Technologies Co., Ltd
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

#include "src/ops/switch.h"

#ifndef PRIMITIVE_WRITEABLE
#include "src/ops/ops_register.h"
#endif

namespace mindspore {
namespace lite {
#ifdef PRIMITIVE_WRITEABLE
int Switch::UnPackAttr(const Primitive &prim, const std::vector<AnfNodePtr> &inputs) {
  if (this->primitive_ == nullptr) {
    this->primitive_ = new (std::nothrow) schema::PrimitiveT;
    if (this->primitive_ == nullptr) {
      MS_LOG(ERROR) << "new primitiveT failed";
      return RET_ERROR;
    }
    this->primitive_->value.type = schema::PrimitiveType_Switch;
  }
  if (this->primitive_->value.type != schema::PrimitiveType_Switch) {
    MS_LOG(ERROR) << "Primitive type is error :" << this->primitive_->value.type;
    return RET_ERROR;
  }
  if (this->primitive_->value.value == nullptr) {
    auto attr = new (std::nothrow) schema::SwitchT();
    if (attr == nullptr) {
      MS_LOG(ERROR) << "new primitiveT value failed";
      return RET_ERROR;
    }

    this->primitive_->value.value = attr;
    if (this->primitive_->value.value == nullptr) {
      MS_LOG(ERROR) << "primitive value is nullptr";
      return RET_ERROR;
    }
  }
  return RET_OK;
}
#else
int Switch::UnPackToFlatBuilder(const schema::Primitive *primitive, flatbuffers::FlatBufferBuilder *fbb) {
  MS_ASSERT(nullptr != primitive);
  MS_ASSERT(nullptr != fbb);
  auto attr = primitive->value_as_Switch();
  if (attr == nullptr) {
    MS_LOG(ERROR) << "value_as_Switch return nullptr";
    return RET_ERROR;
  }
  auto val_offset = schema::CreateSwitch(*fbb);
  auto prim_offset = schema::CreatePrimitive(*fbb, schema::PrimitiveType_Switch, val_offset.o);
  fbb->Finish(prim_offset);
  return RET_OK;
}

PrimitiveC *SwitchCreator(const schema::Primitive *primitive) { return PrimitiveC::NewPrimitiveC<Switch>(primitive); }
Registry SwitchRegistry(schema::PrimitiveType_Switch, SwitchCreator);
#endif

int Switch::InferShape(std::vector<Tensor *> inputs_, std::vector<Tensor *> outputs_) {
  MS_ASSERT(2 * (inputs_.size() - 1) == outputs_.size());
  if (!infer_flag()) {
    return RET_INFER_INVALID;
  }
  for (size_t i = 0; i < outputs_.size() / 2; i++) {
    outputs_[i]->set_data_type(inputs_[i + 1]->data_type());
    outputs_[i + outputs_.size() / 2]->set_data_type(inputs_[i + 1]->data_type());
    outputs_[i]->set_shape(inputs_[i + 1]->shape());
    outputs_[i + outputs_.size() / 2]->set_shape(inputs_[i + 1]->shape());
    outputs_[i]->set_format(inputs_[i + 1]->format());
    outputs_[i + outputs_.size() / 2]->set_format(inputs_[i + 1]->format());
  }
  return RET_OK;
}
}  // namespace lite
}  // namespace mindspore
