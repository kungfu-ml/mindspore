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
#ifdef ENABLE_AVX
#ifndef MINDSPORE_LITE_SRC_RUNTIME_KERNEL_ARM_FP32_CONVOLUTION_DEPTHWISE_SLIDEWINDOW_X86_FP32_H_
#define MINDSPORE_LITE_SRC_RUNTIME_KERNEL_ARM_FP32_CONVOLUTION_DEPTHWISE_SLIDEWINDOW_X86_FP32_H_

#include <vector>
#include "src/inner_kernel.h"
#include "src/runtime/kernel/arm/base/convolution_base.h"
#include "nnacl/fp32/conv_depthwise_fp32.h"

namespace mindspore::kernel {
class ConvolutionDepthwiseSWCPUKernelX86 : public ConvolutionBaseCPUKernel {
 public:
  ConvolutionDepthwiseSWCPUKernelX86(OpParameter *parameter, const std::vector<lite::Tensor *> &inputs,
                                     const std::vector<lite::Tensor *> &outputs, const lite::InnerContext *ctx)
      : ConvolutionBaseCPUKernel(parameter, inputs, outputs, ctx) {}
  ~ConvolutionDepthwiseSWCPUKernelX86() override;

  int Init() override;
  int ReSize() override;
  int Run() override;

  int InitWeightBias();
  int Execute(int task_id);
  int Eval() override;

 private:
  void FreePackedInputOutput();
  int InitPackedInputOutput();
  void PackWeight();
  int oc_tile_ = C8NUM;  // in x86 avx
  SlidingWindowParam *sliding_ = nullptr;
  float *packed_weight_ = nullptr;
  float *packed_bias_ = nullptr;
  float *packed_input_ = nullptr;
  float *packed_output_ = nullptr;
  float *origin_weight_ = nullptr;
  bool input_need_align_ = false;
  bool output_need_align_ = false;
  size_t alignment = C32NUM;
};
}  // namespace mindspore::kernel

#endif  // MINDSPORE_LITE_SRC_RUNTIME_KERNEL_ARM_FP32_CONVOLUTION_DEPTHWISE_SLIDEWINDOW_X86_FP32_H_
#endif
