# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""train resnet."""
import argparse
import ast
import os

import mindspore.common.initializer as weight_init
import mindspore.nn as nn
from mindspore import Tensor, context
from mindspore._c_expression import (kungfu_current_cluster_size,
                                     kungfu_current_rank, kungfu_finalize,
                                     kungfu_init, kungfu_nccl_finalize,
                                     kungfu_nccl_init)
from mindspore.common import set_seed
from mindspore.communication.management import get_group_size, get_rank, init
from mindspore.context import ParallelMode
from mindspore.nn.loss import SoftmaxCrossEntropyWithLogits
from mindspore.nn.optim.momentum import Momentum
from mindspore.train.callback import (CheckpointConfig, LossMonitor,
                                      ModelCheckpoint, TimeMonitor)
from mindspore.train.loss_scale_manager import FixedLossScaleManager
from mindspore.train.model import Model
from mindspore.train.serialization import load_checkpoint, load_param_into_net

from src.CrossEntropySmooth import CrossEntropySmooth
from src.kungfu_mindspore_optimizer import KungFuMomentum
from src.lr_generator import get_lr, warmup_cosine_annealing_lr

parser = argparse.ArgumentParser(description='Image classification')
parser.add_argument('--net',
                    type=str,
                    default=None,
                    help='Resnet Model, either resnet50 or resnet101')
parser.add_argument('--dataset',
                    type=str,
                    default=None,
                    help='Dataset, either cifar10 or imagenet2012')
parser.add_argument('--run_distribute',
                    type=ast.literal_eval,
                    default=False,
                    help='Run distribute')
parser.add_argument('--run_kungfu',
                    type=ast.literal_eval,
                    default=False,
                    help='Run kungfu')
parser.add_argument('--elastic',
                    type=ast.literal_eval,
                    default=False,
                    help='elastic')
parser.add_argument('--device_num', type=int, default=1, help='Device num.')

parser.add_argument('--dataset_path',
                    type=str,
                    default=None,
                    help='Dataset path')
parser.add_argument('--device_target',
                    type=str,
                    default='Ascend',
                    help='Device target')
parser.add_argument('--pre_trained',
                    type=str,
                    default=None,
                    help='Pretrained checkpoint path')
parser.add_argument('--parameter_server',
                    type=ast.literal_eval,
                    default=False,
                    help='Run parameter server train')
args_opt = parser.parse_args()

set_seed(1)

if args_opt.net == "resnet50":
    from src.resnet import resnet50 as resnet
    if args_opt.dataset == "cifar10":
        from src.config import config1 as config
        from src.dataset import create_dataset1 as create_dataset
    else:
        from src.config import config2 as config
        from src.dataset import create_dataset2 as create_dataset
elif args_opt.net == "resnet101":
    from src.config import config3 as config
    from src.dataset import create_dataset3 as create_dataset
    from src.resnet import resnet101 as resnet
else:
    from src.config import config4 as config
    from src.dataset import create_dataset4 as create_dataset
    from src.resnet import se_resnet50 as resnet

if __name__ == '__main__':
    target = args_opt.device_target
    dataset_sink_mode = not args_opt.parameter_server

    ckpt_save_dir = config.save_checkpoint_path

    # init context
    context.set_context(mode=context.GRAPH_MODE,
                        device_target=target,
                        save_graphs=False)
    if args_opt.parameter_server:
        context.set_ps_context(enable_ps=True)
    if args_opt.run_distribute:
        if target == "Ascend":
            device_id = int(os.getenv('DEVICE_ID'))
            context.set_context(device_id=device_id,
                                enable_auto_mixed_precision=True)
            context.set_auto_parallel_context(
                device_num=args_opt.device_num,
                parallel_mode=ParallelMode.DATA_PARALLEL,
                gradients_mean=True)
            if args_opt.net == "resnet50" or args_opt.net == "se-resnet50":
                context.set_auto_parallel_context(
                    all_reduce_fusion_config=[85, 160])
            else:
                context.set_auto_parallel_context(
                    all_reduce_fusion_config=[180, 313])
            init()
        # GPU target
        else:
            init()
            context.set_auto_parallel_context(
                device_num=get_group_size(),
                parallel_mode=ParallelMode.DATA_PARALLEL,
                gradients_mean=True)
            if args_opt.net == "resnet50":
                context.set_auto_parallel_context(
                    all_reduce_fusion_config=[85, 160])
        ckpt_save_dir = config.save_checkpoint_path + "ckpt_" + str(
            get_rank()) + "/"

    if args_opt.run_kungfu:
        kungfu_init()
        kungfu_nccl_init()
        rank = kungfu_current_rank()
        size = kungfu_current_cluster_size()
        print('kungfu rank=%d, size=%d' % (rank, size))
        if args_opt.elastic:
            version = os.getenv('KUNGFU_INIT_CLUSTER_VERSION')
            ckpt_save_dir = config.save_checkpoint_path + "ckpt_" + str(
                rank) + '@' + version + "/"
        else:
            ckpt_save_dir = config.save_checkpoint_path + "ckpt_" + str(
                rank) + "/"

    # create dataset
    dataset = create_dataset(dataset_path=args_opt.dataset_path,
                             do_train=True,
                             repeat_num=1,
                             batch_size=config.batch_size,
                             target=target)
    step_size = dataset.get_dataset_size()

    # define net
    net = resnet(class_num=config.class_num)
    if args_opt.parameter_server:
        net.set_param_ps()

    # init weight
    if args_opt.pre_trained:
        param_dict = load_checkpoint(args_opt.pre_trained)
        load_param_into_net(net, param_dict)
    else:
        for _, cell in net.cells_and_names():
            if isinstance(cell, nn.Conv2d):
                cell.weight.set_data(
                    weight_init.initializer(weight_init.XavierUniform(),
                                            cell.weight.shape,
                                            cell.weight.dtype))
            if isinstance(cell, nn.Dense):
                cell.weight.set_data(
                    weight_init.initializer(weight_init.TruncatedNormal(),
                                            cell.weight.shape,
                                            cell.weight.dtype))

    # init lr
    if args_opt.net == "resnet50" or args_opt.net == "se-resnet50":
        lr = get_lr(lr_init=config.lr_init,
                    lr_end=config.lr_end,
                    lr_max=config.lr_max,
                    warmup_epochs=config.warmup_epochs,
                    total_epochs=config.epoch_size,
                    steps_per_epoch=step_size,
                    lr_decay_mode=config.lr_decay_mode)
    else:
        lr = warmup_cosine_annealing_lr(config.lr, step_size,
                                        config.warmup_epochs,
                                        config.epoch_size,
                                        config.pretrain_epoch_size * step_size)
    lr = Tensor(lr)

    # define opt
    decayed_params = []
    no_decayed_params = []
    for param in net.trainable_params():
        if 'beta' not in param.name and 'gamma' not in param.name and 'bias' not in param.name:
            decayed_params.append(param)
        else:
            no_decayed_params.append(param)

    group_params = [{
        'params': decayed_params,
        'weight_decay': config.weight_decay
    }, {
        'params': no_decayed_params
    }, {
        'order_params': net.trainable_params()
    }]
    if args_opt.run_kungfu:
        opt = KungFuMomentum(group_params,
                             lr,
                             config.momentum,
                             loss_scale=config.loss_scale)
    else:
        opt = Momentum(group_params,
                       lr,
                       config.momentum,
                       loss_scale=config.loss_scale)

    # define loss, model
    if target == "Ascend":
        if args_opt.dataset == "imagenet2012":
            if not config.use_label_smooth:
                config.label_smooth_factor = 0.0
            loss = CrossEntropySmooth(sparse=True,
                                      reduction="mean",
                                      smooth_factor=config.label_smooth_factor,
                                      num_classes=config.class_num)
        else:
            loss = SoftmaxCrossEntropyWithLogits(sparse=True, reduction='mean')
        loss_scale = FixedLossScaleManager(config.loss_scale,
                                           drop_overflow_update=False)
        model = Model(net,
                      loss_fn=loss,
                      optimizer=opt,
                      loss_scale_manager=loss_scale,
                      metrics={'acc'},
                      amp_level="O2",
                      keep_batchnorm_fp32=False)
    else:
        # GPU target
        if args_opt.dataset == "imagenet2012":
            if not config.use_label_smooth:
                config.label_smooth_factor = 0.0
            loss = CrossEntropySmooth(sparse=True,
                                      reduction="mean",
                                      smooth_factor=config.label_smooth_factor,
                                      num_classes=config.class_num)
        else:
            loss = SoftmaxCrossEntropyWithLogits(sparse=True, reduction="mean")

        if (args_opt.net == "resnet101" or args_opt.net
                == "resnet50") and not args_opt.parameter_server:
            opt = Momentum(
                filter(lambda x: x.requires_grad, net.get_parameters()), lr,
                config.momentum, config.weight_decay, config.loss_scale)
            loss_scale = FixedLossScaleManager(config.loss_scale,
                                               drop_overflow_update=False)
            # Mixed precision
            model = Model(net,
                          loss_fn=loss,
                          optimizer=opt,
                          loss_scale_manager=loss_scale,
                          metrics={'acc'},
                          amp_level="O2",
                          keep_batchnorm_fp32=False)
        else:
            ## fp32 training
            opt = Momentum(
                filter(lambda x: x.requires_grad, net.get_parameters()), lr,
                config.momentum, config.weight_decay)
            model = Model(net, loss_fn=loss, optimizer=opt, metrics={'acc'})

    # define callbacks
    time_cb = TimeMonitor(data_size=step_size)
    loss_cb = LossMonitor()
    cb = [time_cb, loss_cb]
    if config.save_checkpoint:
        config_ck = CheckpointConfig(
            save_checkpoint_steps=config.save_checkpoint_epochs * step_size,
            keep_checkpoint_max=config.keep_checkpoint_max)
        ckpt_cb = ModelCheckpoint(prefix="resnet",
                                  directory=ckpt_save_dir,
                                  config=config_ck)
        cb += [ckpt_cb]

    if args_opt.elastic:
        from elastic_schedule import schedule
        from src.kungfu_mindspore_callbacks import KungFuElasticCallback
        kungfu_elastic_callback = KungFuElasticCallback(schedule)
        cb += [kungfu_elastic_callback]
        dataset_sink_mode = False
        print('enabled elastic')

        # from src.debug_stop_hook import DebugStopHook
        # cb += [DebugStopHook()]

    # train model
    if args_opt.net == "se-resnet50":
        config.epoch_size = config.train_epoch_size
    print('training...')
    print('dataset.get_dataset_size(): %d' % (dataset.get_dataset_size()))
    print('%d callbacks' % (len(cb)))
    print('epoch_size: %d, pretrain_epoch_size: %d' %
          (config.epoch_size, config.pretrain_epoch_size))
    for c in cb:
        print('%s' % (c))
    train_epoch = config.epoch_size - config.pretrain_epoch_size
    print('dataset_sink_mode: %s' % (dataset_sink_mode))
    model.train(train_epoch,
                dataset,
                callbacks=cb,
                sink_size=dataset.get_dataset_size(),
                dataset_sink_mode=dataset_sink_mode)
    print('train finished.')
    if args_opt.run_kungfu:
        kungfu_nccl_finalize()
        kungfu_finalize()
