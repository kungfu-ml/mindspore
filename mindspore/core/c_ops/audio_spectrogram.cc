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

#include "c_ops/audio_spectrogram.h"
#include <string>
#include <algorithm>
#include <memory>
#include <set>
#include <vector>
#include "c_ops/op_utils.h"
#include "utils/check_convert_utils.h"
#include "abstract/primitive_infer_map.h"

namespace mindspore {

void AudioSpectrogram::set_window_size(const int64_t &window_size) {
  this->AddAttr(kWindowSize, MakeValue(window_size));
}
int64_t AudioSpectrogram::get_window_size() const {
  auto value_ptr = GetAttr(kWindowSize);
  return GetValue<int64_t>(value_ptr);
}

void AudioSpectrogram::set_stride(const int64_t &stride) { this->AddAttr(kStride, MakeValue(stride)); }
int64_t AudioSpectrogram::get_stride() const {
  auto value_ptr = GetAttr(kStride);
  return GetValue<int64_t>(value_ptr);
}

void AudioSpectrogram::set_mag_square(const bool &mag_square) { this->AddAttr(kMagSquare, MakeValue(mag_square)); }
bool AudioSpectrogram::get_mag_square() const {
  auto value_ptr = GetAttr(kMagSquare);
  return GetValue<bool>(value_ptr);
}
void AudioSpectrogram::Init(const int64_t &window_size, const int64_t &stride, const bool &mag_square) {
  this->set_window_size(window_size);
  this->set_stride(stride);
  this->set_mag_square(mag_square);
}
REGISTER_PRIMITIVE_C(kNameAudioSpectrogram, AudioSpectrogram);
}  // namespace mindspore
