# Contents

- [InceptionV3 Description](#InceptionV3-description)
- [Model Architecture](#model-architecture)
- [Dataset](#dataset)
- [Features](#features)
    - [Mixed Precision](#mixed-precision)
- [Environment Requirements](#environment-requirements)
- [Script Description](#script-description)
    - [Script and Sample Code](#script-and-sample-code)
    - [Training Process](#training-process)
    - [Evaluation Process](#evaluation-process)
        - [Evaluation](#evaluation)
- [Model Description](#model-description)
    - [Performance](#performance)  
        - [Evaluation Performance](#evaluation-performance)
        - [Inference Performance](#inference-performance)
- [Description of Random Situation](#description-of-random-situation)
- [ModelZoo Homepage](#modelzoo-homepage)

# [InceptionV3 Description](#contents)

InceptionV3 by Google is the 3rd version in a series of Deep Learning Convolutional Architectures. Inception v3 mainly focuses on burning less computational power by modifying the previous Inception architectures. This idea was proposed in the paper Rethinking the Inception Architecture for Computer Vision, published in 2015.

[Paper](https://arxiv.org/pdf/1512.00567.pdf) Min Sun, Ali Farhadi, Steve Seitz. Ranking Domain-Specific Highlights by Analyzing Edited Videos[J]. 2014.

# [Model architecture](#contents)

The overall network architecture of InceptionV3 is show below:

[Link](https://arxiv.org/pdf/1512.00567.pdf)

# [Dataset](#contents)

Dataset used can refer to paper.

- Dataset size: 125G, 1250k colorful images in 1000 classes
    - Train: 120G, 1200k images
    - Test: 5G, 50k images
- Data format: RGB images.
    - Note: Data will be processed in src/dataset.py

# [Features](#contents)

## [Mixed Precision(Ascend)](#contents)

The [mixed precision](https://www.mindspore.cn/tutorial/training/en/master/advanced_use/enable_mixed_precision.html) training method accelerates the deep learning neural network training process by using both the single-precision and half-precision data formats, and maintains the network precision achieved by the single-precision training at the same time. Mixed precision training can accelerate the computation process, reduce memory usage, and enable a larger model or batch size to be trained on specific hardware.

For FP16 operators, if the input data type is FP32, the backend of MindSpore will automatically handle it with reduced precision. Users could check the reduced-precision operators by enabling INFO log and then searching ‘reduce precision’.

# [Environment Requirements](#contents)

- Hardware（Ascend）
- Prepare hardware environment with Ascend processor. If you want to try Ascend, please send the [application form](https://obs-9be7.obs.cn-east-2.myhuaweicloud.com/file/other/Ascend%20Model%20Zoo%E4%BD%93%E9%AA%8C%E8%B5%84%E6%BA%90%E7%94%B3%E8%AF%B7%E8%A1%A8.docx) to ascend@huawei.com. Once approved, you can get the resources.
- Framework
    - [MindSpore](https://www.mindspore.cn/install/en)
- For more information, please check the resources below：
    - [MindSpore Tutorials](https://www.mindspore.cn/tutorial/training/en/master/index.html)
    - [MindSpore Python API](https://www.mindspore.cn/doc/api_python/en/master/index.html)

# [Script description](#contents)

## [Script and sample code](#contents)

```shell
.
└─Inception-v3
  ├─README.md
  ├─scripts
    ├─run_standalone_train.sh                 # launch standalone training with ascend platform(1p)
    ├─run_distribute_train.sh                 # launch distributed training with ascend platform(8p)
    └─run_eval.sh                             # launch evaluating with ascend platform
  ├─src
    ├─config.py                       # parameter configuration
    ├─dataset.py                      # data preprocessing
    ├─inception_v3.py                 # network definition
    ├─loss.py                         # Customized CrossEntropy loss function
    ├─lr_generator.py                 # learning rate generator
  ├─eval.py                           # eval net
  ├─export.py                         # convert checkpoint
  └─train.py                          # train net

```

## [Script Parameters](#contents)

```python
Major parameters in train.py and config.py are:
'random_seed'                # fix random seed
'work_nums'                  # number of workers to read the data
'decay_method'               # learning rate scheduler mode
"loss_scale"                 # loss scale
'batch_size'                 # input batchsize
'epoch_size'                 # total epoch numbers
'num_classes'                # dataset class numbers
'smooth_factor'              # label smoothing factor
'aux_factor'                 # loss factor of aux logit
'lr_init'                    # initiate learning rate
'lr_max'                     # max bound of learning rate
'lr_end'                     # min bound of learning rate
'warmup_epochs'              # warmup epoch numbers
'weight_decay'               # weight decay
'momentum'                   # momentum
'opt_eps'                    # epsilon
'keep_checkpoint_max'        # max numbers to keep checkpoints
'ckpt_path'                  # save checkpoint path
'is_save_on_master'          # save checkpoint on rank0, distributed parameters
'dropout_keep_prob'          # the keep rate, between 0 and 1, e.g. keep_prob = 0.9, means dropping out 10% of input units
'has_bias'                   # specifies whether the layer uses a bias vector.
'amp_level'                  # option for argument `level` in `mindspore.amp.build_train_network`, level for mixed
                             # precision training. Supports [O0, O2, O3].

```

## [Training process](#contents)

### Usage

You can start training using python or shell scripts. The usage of shell scripts as follows:

- Ascend:

```shell
# distribute training(8p)
sh scripts/run_distribute_train.sh RANK_TABLE_FILE DATA_PATH
# standalone training
sh scripts/run_standalone_train.sh DEVICE_ID DATA_PATH
```

> Notes: RANK_TABLE_FILE can refer to [Link](https://www.mindspore.cn/tutorial/training/en/master/advanced_use/distributed_training_ascend.html), and the device_ip can be got as [Link](https://gitee.com/mindspore/mindspore/tree/master/model_zoo/utils/hccl_tools). For large models like InceptionV3, it's better to export an external environment variable `export HCCL_CONNECT_TIMEOUT=600` to extend hccl connection checking time from the default 120 seconds to 600 seconds. Otherwise, the connection could be timeout since compiling time increases with the growth of model size.
>
> This is processor cores binding operation regarding the `device_num` and total processor numbers. If you are not expect to do it, remove the operations `taskset` in `scripts/run_distribute_train.sh`

### Launch

```python
# training example
  python:
      Ascend: python train.py --dataset_path DATA_PATH --platform Ascend

  shell:
      Ascend:
      # distribute training example(8p)
      sh scripts/run_distribute_train.sh RANK_TABLE_FILE DATA_PATH
      # standalone training example
      sh scripts/run_standalone_train.sh DEVICE_ID DATA_PATH
```

### Result

Training result will be stored in the example path. Checkpoints will be stored at `. /checkpoint` by default, and training log  will be redirected to `./log.txt` like followings.

```python
epoch: 0 step: 1251, loss is 5.7787247
epoch time: 360760.985 ms, per step time: 288.378 ms
epoch: 1 step: 1251, loss is 4.392868
epoch time: 160917.911 ms, per step time: 128.631 ms
```

## [Eval process](#contents)

### Usage

You can start training using python or shell scripts. The usage of shell scripts as follows:

- Ascend:

```python
    sh scripts/run_eval.sh DEVICE_ID DATA_PATH PATH_CHECKPOINT
```

### Launch

```python
# eval example
  python:
      Ascend: python eval.py --dataset_path DATA_PATH --checkpoint PATH_CHECKPOINT --platform Ascend

  shell:
      Ascend: sh scripts/run_eval.sh DEVICE_ID DATA_PATH PATH_CHECKPOINT
```

> checkpoint can be produced in training process.

### Result

Evaluation result will be stored in the example path, you can find result like the followings in `eval.log`.

```python
metric: {'Loss': 1.778, 'Top1-Acc':0.788, 'Top5-Acc':0.942}
```

# [Model description](#contents)

## [Performance](#contents)

### Evaluation Performance

| Parameters                 | Ascend                                    |
| -------------------------- | ---------------------------------------------- |
| Model Version              | InceptionV3                                    |
| Resource                   | Ascend 910, cpu:2.60GHz 192cores, memory:755G   |
| uploaded Date              | 08/21/2020                                     |
| MindSpore Version          | 0.6.0-beta                                     |
| Dataset                    | 1200k images                                   |
| Batch_size                 | 128                                            |
| Training Parameters        | src/config.py                                  |
| Optimizer                  | RMSProp                                        |
| Loss Function              | SoftmaxCrossEntropy                            |
| Outputs                    | probability                                    |
| Loss                       | 1.98                                           |
| Total time (8p)            | 11h                                            |
| Params (M)                 | 103M                                           |
| Checkpoint for Fine tuning | 313M                                           |
| Model for inference        | 92M (.onnx file)                               |
| Speed                      | 1pc:1050 img/s;8pc:8000 img/s                  |
| Scripts                    | [inceptionv3 script](https://gitee.com/mindspore/mindspore/tree/master/model_zoo/official/cv/inceptionv3) |

### Inference Performance

| Parameters          | Ascend                 |
| ------------------- | --------------------------- |
| Model Version       | InceptionV3                 |
| Resource            | Ascend 910, cpu:2.60GHz 192cores, memory:755G                  |
| Uploaded Date       | 08/22/2020                  |
| MindSpore Version   | 0.6.0-beta                  |
| Dataset             | 50k images                  |
| Batch_size          | 128                         |
| Outputs             | probability                 |
| Accuracy            | ACC1[78.8%] ACC5[94.2%]     |
| Total time          | 2mins                       |

# [Description of Random Situation](#contents)

In dataset.py, we set the seed inside “create_dataset" function. We also use random seed in train.py.

# [ModelZoo Homepage](#contents)

Please check the official [homepage](https://gitee.com/mindspore/mindspore/tree/master/model_zoo).