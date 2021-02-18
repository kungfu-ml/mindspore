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

"""FasterRcnn dataset"""
from __future__ import division
import os
import numpy as np
from numpy import random
import mmcv
import mindspore.dataset as de
import mindspore.dataset.vision.c_transforms as C
import mindspore.dataset.transforms.c_transforms as CC
import mindspore.common.dtype as mstype
from mindspore.mindrecord import FileWriter
from src.config import config

class PhotoMetricDistortion:
    """Photo Metric Distortion"""

    def __init__(self,
                 brightness_delta=32,
                 contrast_range=(0.5, 1.5),
                 saturation_range=(0.5, 1.5),
                 hue_delta=18):
        self.brightness_delta = brightness_delta
        self.contrast_lower, self.contrast_upper = contrast_range
        self.saturation_lower, self.saturation_upper = saturation_range
        self.hue_delta = hue_delta

    def __call__(self, img, boxes, labels):
        img = img.astype('float32')
        if random.randint(2):
            delta = random.uniform(-self.brightness_delta, self.brightness_delta)
            img += delta
        mode = random.randint(2)
        if mode == 1:
            if random.randint(2):
                alpha = random.uniform(self.contrast_lower,
                                       self.contrast_upper)
                img *= alpha
        # convert color from BGR to HSV
        img = mmcv.bgr2hsv(img)
        # random saturation
        if random.randint(2):
            img[..., 1] *= random.uniform(self.saturation_lower,
                                          self.saturation_upper)
        # random hue
        if random.randint(2):
            img[..., 0] += random.uniform(-self.hue_delta, self.hue_delta)
            img[..., 0][img[..., 0] > 360] -= 360
            img[..., 0][img[..., 0] < 0] += 360
        # convert color from HSV to BGR
        img = mmcv.hsv2bgr(img)
        # random contrast
        if mode == 0:
            if random.randint(2):
                alpha = random.uniform(self.contrast_lower,
                                       self.contrast_upper)
                img *= alpha
        # randomly swap channels
        if random.randint(2):
            img = img[..., random.permutation(3)]
        return img, boxes, labels

class Expand:
    """expand image"""

    def __init__(self, mean=(0, 0, 0), to_rgb=True, ratio_range=(1, 4)):
        if to_rgb:
            self.mean = mean[::-1]
        else:
            self.mean = mean
        self.min_ratio, self.max_ratio = ratio_range

    def __call__(self, img, boxes, labels):
        if random.randint(2):
            return img, boxes, labels
        h, w, c = img.shape
        ratio = random.uniform(self.min_ratio, self.max_ratio)
        expand_img = np.full((int(h * ratio), int(w * ratio), c),
                             self.mean).astype(img.dtype)
        left = int(random.uniform(0, w * ratio - w))
        top = int(random.uniform(0, h * ratio - h))
        expand_img[top:top + h, left:left + w] = img
        img = expand_img
        boxes += np.tile((left, top), 2)
        return img, boxes, labels

def rescale_column(img, img_shape, gt_bboxes, gt_label, gt_num):
    """rescale operation for image"""
    img_data, scale_factor = mmcv.imrescale(img, (config.img_width, config.img_height), return_scale=True)
    if img_data.shape[0] > config.img_height:
        img_data, scale_factor2 = mmcv.imrescale(img_data, (config.img_height, config.img_width), return_scale=True)
        scale_factor = scale_factor * scale_factor2
    img_shape = np.append(img_shape, scale_factor)
    img_shape = np.asarray(img_shape, dtype=np.float32)
    gt_bboxes = gt_bboxes * scale_factor
    gt_bboxes = split_gtbox_label(gt_bboxes)
    if gt_bboxes.shape[0] != 0:
        gt_bboxes[:, 0::2] = np.clip(gt_bboxes[:, 0::2], 0, img_shape[1] - 1)
        gt_bboxes[:, 1::2] = np.clip(gt_bboxes[:, 1::2], 0, img_shape[0] - 1)

    return (img_data, img_shape, gt_bboxes, gt_label, gt_num)


def resize_column(img, img_shape, gt_bboxes, gt_label, gt_num):
    """resize operation for image"""
    img_data = img
    img_data, w_scale, h_scale = mmcv.imresize(
        img_data, (config.img_width, config.img_height), return_scale=True)
    scale_factor = np.array(
        [w_scale, h_scale, w_scale, h_scale], dtype=np.float32)
    img_shape = (config.img_height, config.img_width, 1.0)
    img_shape = np.asarray(img_shape, dtype=np.float32)
    gt_bboxes = gt_bboxes * scale_factor
    gt_bboxes = split_gtbox_label(gt_bboxes)
    gt_bboxes[:, 0::2] = np.clip(gt_bboxes[:, 0::2], 0, img_shape[1] - 1)
    gt_bboxes[:, 1::2] = np.clip(gt_bboxes[:, 1::2], 0, img_shape[0] - 1)

    return (img_data, img_shape, gt_bboxes, gt_label, gt_num)


def resize_column_test(img, img_shape, gt_bboxes, gt_label, gt_num):
    """resize operation for image of eval"""
    img_data = img
    img_data, w_scale, h_scale = mmcv.imresize(
        img_data, (config.img_width, config.img_height), return_scale=True)
    scale_factor = np.array(
        [w_scale, h_scale, w_scale, h_scale], dtype=np.float32)
    img_shape = (config.img_height, config.img_width)
    img_shape = np.append(img_shape, (h_scale, w_scale))
    img_shape = np.asarray(img_shape, dtype=np.float32)
    gt_bboxes = gt_bboxes * scale_factor
    shape = gt_bboxes.shape
    label_column = np.ones((shape[0], 1), dtype=int)
    gt_bboxes = np.concatenate((gt_bboxes, label_column), axis=1)
    gt_bboxes[:, 0::2] = np.clip(gt_bboxes[:, 0::2], 0, img_shape[1] - 1)
    gt_bboxes[:, 1::2] = np.clip(gt_bboxes[:, 1::2], 0, img_shape[0] - 1)

    return (img_data, img_shape, gt_bboxes, gt_label, gt_num)

def flipped_generation(img, img_shape, gt_bboxes, gt_label, gt_num):
    """flipped generation"""
    img_data = img
    flipped = gt_bboxes.copy()
    _, w, _ = img_data.shape
    flipped[..., 0::4] = w - gt_bboxes[..., 2::4] - 1
    flipped[..., 2::4] = w - gt_bboxes[..., 0::4] - 1
    return (img_data, img_shape, flipped, gt_label, gt_num)

def image_bgr_rgb(img, img_shape, gt_bboxes, gt_label, gt_num):
    img_data = img[:, :, ::-1]
    return (img_data, img_shape, gt_bboxes, gt_label, gt_num)

def photo_crop_column(img, img_shape, gt_bboxes, gt_label, gt_num):
    """photo crop operation for image"""
    random_photo = PhotoMetricDistortion()
    img_data, gt_bboxes, gt_label = random_photo(img, gt_bboxes, gt_label)

    return (img_data, img_shape, gt_bboxes, gt_label, gt_num)

def expand_column(img, img_shape, gt_bboxes, gt_label, gt_num):
    """expand operation for image"""
    expand = Expand()
    img, gt_bboxes, gt_label = expand(img, gt_bboxes, gt_label)

    return (img, img_shape, gt_bboxes, gt_label, gt_num)

def split_gtbox_label(gt_bbox_total):
    """split ground truth box label"""
    gtbox_list = []
    box_num, _ = gt_bbox_total.shape
    for i in range(box_num):
        gt_bbox = gt_bbox_total[i]
        if gt_bbox[0] % 16 != 0:
            gt_bbox[0] = (gt_bbox[0] // 16) * 16
        if gt_bbox[2] % 16 != 0:
            gt_bbox[2] = (gt_bbox[2] // 16 + 1) * 16
        x0_array = np.arange(gt_bbox[0], gt_bbox[2], 16)
        for x0 in x0_array:
            gtbox_list.append([x0, gt_bbox[1], x0+15, gt_bbox[3], 1])
    return np.array(gtbox_list)

def pad_label(img, img_shape, gt_bboxes, gt_label, gt_valid):
    """pad ground truth label"""
    pad_max_number = 256
    gt_label = gt_bboxes[:, 4]
    gt_valid = gt_bboxes[:, 4]
    if gt_bboxes.shape[0] < 256:
        gt_box = np.pad(gt_bboxes, ((0, pad_max_number - gt_bboxes.shape[0]), (0, 0)), \
            mode="constant", constant_values=0)
        gt_label = np.pad(gt_label, ((0, pad_max_number - gt_bboxes.shape[0])), mode="constant", constant_values=-1)
        gt_valid = np.pad(gt_valid, ((0, pad_max_number - gt_bboxes.shape[0])), mode="constant", constant_values=0)
    else:
        print("WARNING label num is high than 256")
        gt_box = gt_bboxes[0:pad_max_number]
        gt_label = gt_label[0:pad_max_number]
        gt_valid = gt_valid[0:pad_max_number]
    return (img, img_shape, gt_box[:, :4], gt_label, gt_valid)

def preprocess_fn(image, box, is_training):
    """Preprocess function for dataset."""
    def _infer_data(image_bgr, image_shape, gt_box_new, gt_label_new, gt_valid):
        image_shape = image_shape[:2]
        input_data = image_bgr, image_shape, gt_box_new, gt_label_new, gt_valid
        if config.keep_ratio:
            input_data = rescale_column(*input_data)
        else:
            input_data = resize_column_test(*input_data)
        input_data = pad_label(*input_data)
        input_data = image_bgr_rgb(*input_data)
        output_data = input_data
        return output_data

    def _data_aug(image, box, is_training):
        """Data augmentation function."""
        image_bgr = image.copy()
        image_bgr[:, :, 0] = image[:, :, 2]
        image_bgr[:, :, 1] = image[:, :, 1]
        image_bgr[:, :, 2] = image[:, :, 0]
        image_shape = image_bgr.shape[:2]
        gt_box = box[:, :4]
        gt_label = box[:, 4]
        gt_valid = box[:, 4]
        input_data = image_bgr, image_shape, gt_box, gt_label, gt_valid
        if not is_training:
            return _infer_data(image_bgr, image_shape, gt_box, gt_label, gt_valid)
        expand = (np.random.rand() < config.expand_ratio)
        if expand:
            input_data = expand_column(*input_data)
        input_data = photo_crop_column(*input_data)
        if config.keep_ratio:
            input_data = rescale_column(*input_data)
        else:
            input_data = resize_column(*input_data)
        input_data = pad_label(*input_data)
        input_data = image_bgr_rgb(*input_data)
        output_data = input_data
        return output_data

    return _data_aug(image, box, is_training)

def anno_parser(annos_str):
    """Parse annotation from string to list."""
    annos = []
    for anno_str in annos_str:
        anno = list(map(int, anno_str.strip().split(',')))
        annos.append(anno)
    return annos

def filter_valid_data(image_dir, anno_path):
    """Filter valid image file, which both in image_dir and anno_path."""
    image_files = []
    image_anno_dict = {}
    if not os.path.isdir(image_dir):
        raise RuntimeError("Path given is not valid.")
    if not os.path.isfile(anno_path):
        raise RuntimeError("Annotation file is not valid.")

    with open(anno_path, "rb") as f:
        lines = f.readlines()
    for line in lines:
        line_str = line.decode("utf-8").strip()
        line_split = str(line_str).split(' ')
        file_name = line_split[0]
        image_path = os.path.join(image_dir, file_name)
        if os.path.isfile(image_path):
            image_anno_dict[image_path] = anno_parser(line_split[1:])
            image_files.append(image_path)
    return image_files, image_anno_dict

def data_to_mindrecord_byte_image(is_training=True, prefix="cptn_mlt.mindrecord", file_num=8):
    """Create MindRecord file."""
    mindrecord_dir = config.mindrecord_dir
    mindrecord_path = os.path.join(mindrecord_dir, prefix)
    writer = FileWriter(mindrecord_path, file_num)
    image_files, image_anno_dict = create_icdar_test_label()
    ctpn_json = {
        "image": {"type": "bytes"},
        "annotation": {"type": "int32", "shape": [-1, 6]},
    }
    writer.add_schema(ctpn_json, "ctpn_json")
    for image_name in image_files:
        with open(image_name, 'rb') as f:
            img = f.read()
        annos = np.array(image_anno_dict[image_name], dtype=np.int32)
        row = {"image": img, "annotation": annos}
        writer.write_raw_data([row])
    writer.commit()

def create_ctpn_dataset(mindrecord_file, batch_size=1, repeat_num=1, device_num=1, rank_id=0,
                        is_training=True, num_parallel_workers=4):
    """Creatr deeptext dataset with MindDataset."""
    ds = de.MindDataset(mindrecord_file, columns_list=["image", "annotation"], num_shards=device_num, shard_id=rank_id,\
        num_parallel_workers=8, shuffle=is_training)
    decode = C.Decode()
    ds = ds.map(operations=decode, input_columns=["image"], num_parallel_workers=1)
    compose_map_func = (lambda image, annotation: preprocess_fn(image, annotation, is_training))
    hwc_to_chw = C.HWC2CHW()
    normalize_op = C.Normalize((123.675, 116.28, 103.53), (58.395, 57.12, 57.375))
    type_cast0 = CC.TypeCast(mstype.float32)
    type_cast1 = CC.TypeCast(mstype.float16)
    type_cast2 = CC.TypeCast(mstype.int32)
    type_cast3 = CC.TypeCast(mstype.bool_)
    if is_training:
        ds = ds.map(operations=compose_map_func, input_columns=["image", "annotation"],
                    output_columns=["image", "image_shape", "box", "label", "valid_num"],
                    column_order=["image", "image_shape", "box", "label", "valid_num"],
                    num_parallel_workers=num_parallel_workers)
        ds = ds.map(operations=[normalize_op, type_cast0], input_columns=["image"],
                    num_parallel_workers=12)
        ds = ds.map(operations=[hwc_to_chw, type_cast1], input_columns=["image"],
                    num_parallel_workers=12)
    else:
        ds = ds.map(operations=compose_map_func,
                    input_columns=["image", "annotation"],
                    output_columns=["image", "image_shape", "box", "label", "valid_num"],
                    column_order=["image", "image_shape", "box", "label", "valid_num"],
                    num_parallel_workers=num_parallel_workers)

        ds = ds.map(operations=[normalize_op, hwc_to_chw, type_cast1], input_columns=["image"],
                    num_parallel_workers=24)
    # transpose_column from python to c
    ds = ds.map(operations=[type_cast1], input_columns=["image_shape"])
    ds = ds.map(operations=[type_cast1], input_columns=["box"])
    ds = ds.map(operations=[type_cast2], input_columns=["label"])
    ds = ds.map(operations=[type_cast3], input_columns=["valid_num"])
    ds = ds.batch(batch_size, drop_remainder=True)
    ds = ds.repeat(repeat_num)
    return ds