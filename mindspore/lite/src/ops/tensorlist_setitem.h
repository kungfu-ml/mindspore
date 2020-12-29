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
#include <vector>
#include "src/ops/primitive_c.h"
#include "src/tensorlist.h"
#include "ir/dtype/type_id.h"

#ifndef LITE_MINDSPORE_LITE_C_OPS_TENSORLISTSETITEM_H_
#define LITE_MINDSPORE_LITE_C_OPS_TENSORLISTSETITEM_H_
namespace mindspore {
namespace lite {
class TensorListSetItem : public PrimitiveC {
 public:
  TensorListSetItem() = default;
  ~TensorListSetItem() = default;
#ifdef PRIMITIVE_WRITEABLE
  MS_DECLARE_PARENT(TensorListSetItem, PrimitiveC);
  void SetElementDType(int type);
  explicit TensorListSetItem(schema::PrimitiveT *primitive) : PrimitiveC(primitive) {}
  int UnPackAttr(const Primitive &prim, const std::vector<AnfNodePtr> &inputs) override;
#else
  int UnPackToFlatBuilder(const schema::Primitive *primitive, flatbuffers::FlatBufferBuilder *fbb) override;
#endif
  TypeId GetElementDType() const;
  int InferShape(std::vector<lite::Tensor *> inputs_, std::vector<lite::Tensor *> outputs_) override;
};
}  // namespace lite
}  // namespace mindspore

#endif  // LITE_MINDSPORE_LITE_C_OPS_TENSORLISTSETITEM_H_
