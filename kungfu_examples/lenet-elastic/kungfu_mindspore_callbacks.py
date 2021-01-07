import mindspore as ms
import mindspore.ops.operations.kungfu_comm_ops as kfops


class Broadcast(ms.nn.Cell):
    def __init__(self):
        super(Broadcast, self).__init__()
        self.broadcast = kfops.KungFuBroadcast()

    def construct(self, x):
        return self.broadcast(x)


class Resize(ms.nn.Cell):
    def __init__(self):
        super(Resize, self).__init__()
        self.resize = kfops.KungFuResize()

    def construct(self, n):
        return self.resize(n)


def sync_net_parameters(network: ms.nn.Cell):
    print('BEGIN sync_net_parameters')
    broadcast = Broadcast()
    network.init_parameters_data()
    for _name, param in network.parameters_and_names():
        x = ms.Tensor(param.data)
        x = broadcast(x)
        param.set_data(x)
    print('END sync_net_parameters')


# TODO: use KungFu AP interface
class KungFuElasticCallback(ms.train.callback.Callback):
    def __init__(self, schedule):
        self.schedule = schedule
        self.need_sync = True

        self.broadcast = Broadcast()
        # TODO: use integer
        self._kungfu_global_step = ms.Tensor(0.0, dtype=ms.float32)

        # self.resize = kfops.KungFuResize()()
        """
    FIXME:
    kungfu_init called in thread 139876087523136
    [ERROR] PYNATIVE(16185,python3.7):2020-12-23-11:40:43.645.165 [mindspore/ccsrc/pipeline/pynative/pynative_execute.cc:660] RunOpInMs] Device target [CPU] is not supported in Pynative mode
    Traceback (most recent call last):
    File "train.py", line 168, in <module>
        main()
    File "train.py", line 161, in main
        train_net(network, model, args, ckpoint_cb, dataset_sink_mode)
    File "train.py", line 113, in train_net
        kungfu_elastic_callback = KungFuElasticCallback(schedule)
    File "/home/lg/code/repos/github.com/lgarithm/mindspore-dev/kungfu_examples/lenet-elastic/kungfu_mindspore_callbacks.py", line 45, in __init__
        self.resize = kfops.KungFuResize()()
    File "/home/lg/.local/lib/python3.7/site-packages/mindspore/ops/primitive.py", line 173, in __call__
        return _run_op(self, self.name, args)
    File "/home/lg/.local/lib/python3.7/site-packages/mindspore/common/api.py", line 69, in wrapper
        results = fn(*arg, **kwargs)
    File "/home/lg/.local/lib/python3.7/site-packages/mindspore/ops/primitive.py", line 512, in _run_op
        output = real_run_op(obj, op_name, args)
    RuntimeError: mindspore/ccsrc/pipeline/pynative/pynative_execute.cc:660 RunOpInMs] ArgumentError Device target [CPU] is not supported in Pynative mode
        """
        self.resize = Resize()

    def _advance_step(self):
        old_step = int(self._kungfu_global_step.asnumpy())
        self._kungfu_global_step = ms.Tensor(old_step + 1.0, dtype=ms.float32)

    def _sync_step(self):
        old_step = int(self._kungfu_global_step.asnumpy())
        self._kungfu_global_step = self.broadcast(self._kungfu_global_step)
        new_step = int(self._kungfu_global_step.asnumpy())
        print('sync step %d -> %d' % (old_step, new_step))

    def begin(self, run_context):
        pass

    def epoch_begin(self, run_context):
        pass

    def epoch_end(self, run_context):
        pass

    def step_begin(self, run_context):
        self._advance_step()

        if self.need_sync:
            self._sync_step()
            cb_params = run_context.original_args()
            sync_net_parameters(cb_params.train_network)
            self.need_sync = False

    def step_end(self, run_context):
        step = int(self._kungfu_global_step.asnumpy())
        if step in self.schedule:
            new_size = self.schedule[step]
            new_size_tensor = ms.Tensor(new_size, dtype=ms.uint32)
            print('calling resize with %d at step %d' % (new_size, step))
            changed, detached = self.resize(new_size_tensor)
            if changed:
                self.need_sync = True
            if detached:
                run_context.request_stop()

    def end(self, run_context):
        print('stopped')
