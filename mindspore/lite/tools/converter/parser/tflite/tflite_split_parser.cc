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

#include "tools/converter/parser/tflite/tflite_split_parser.h"
#include <vector>
#include <memory>
#include <map>

namespace mindspore {
namespace lite {
PrimitiveC *TfliteSplitParser::ParseLitePrimitive(const std::unique_ptr<tflite::OperatorT> &tflite_op,
                                                  const std::unique_ptr<tflite::ModelT> &tflite_model) {
  auto primitive = std::make_unique<schema::PrimitiveT>();
  auto &tflite_subgraph = tflite_model->subgraphs.front();
  if (primitive == nullptr) {
    MS_LOG(ERROR) << "primitive is null";
    return nullptr;
  }

  std::unique_ptr<schema::SplitT> attr = std::make_unique<schema::SplitT>();
  if (attr == nullptr) {
    MS_LOG(ERROR) << "new op failed";
    return nullptr;
  }

  const auto &tflite_attr = tflite_op->builtin_options.AsSplitOptions();
  if (tflite_attr == nullptr) {
    MS_LOG(ERROR) << "get op split attr failed";
    return nullptr;
  }
  auto num_splits = tflite_attr->num_splits;

  const auto &shape_tensor = tflite_subgraph->tensors[tflite_op->inputs[1]];
  if (shape_tensor == nullptr) {
    MS_LOG(ERROR) << "shape_tensor is null";
    return nullptr;
  }
  const auto tensor_shape = shape_tensor->shape;
  const auto &axis_tensor = tflite_subgraph->tensors[tflite_op->inputs[0]];
  if (axis_tensor == nullptr) {
    MS_LOG(ERROR) << "axis_tensor is null";
    return nullptr;
  }
  auto axis = *(reinterpret_cast<int32_t *>(tflite_model->buffers[axis_tensor->buffer]->data.data()));
  if (axis < 0) {
    axis += tensor_shape.size();
  }
  if (axis >= static_cast<int>(tensor_shape.size())) {
    MS_LOG(ERROR) << "axis value is too large";
    return nullptr;
  }
  attr->splitDim = axis;
  if (tensor_shape[axis] % num_splits != 0 && tensor_shape[axis] / num_splits != 0) {
    MS_LOG(ERROR) << "num_splits can't divide tensor's length at axis " << axis;
    return nullptr;
  }
  attr->numberSplit = num_splits;
  if (tensor_shape[axis] / num_splits != 0) {
    for (int i = 0; i < num_splits; i++) {
      attr->sizeSplits.push_back(tensor_shape[axis] / num_splits);
    }
  }

  primitive->value.type = schema::PrimitiveType_Split;
  primitive->value.value = attr.release();
  return PrimitiveC::Create(primitive.release());
}

TfliteNodeRegister g_tfliteSplitParser(tflite::BuiltinOperator_SPLIT, new TfliteSplitParser());
}  // namespace lite
}  // namespace mindspore
