import torch
import numpy as np
from tensorflow.python import pywrap_tensorflow


def weight_extract(file_dir):
    reader = pywrap_tensorflow.NewCheckpointReader(file_dir)
    var_to_shape_map = reader.get_variable_to_shape_map()
    keys_list=[]
    tensors=[]

    for key in sorted(var_to_shape_map):
        keys_list.append(key)
        tensors.append(reader.get_tensor(key))

    return keys_list, tensors


def get_value(keys, tensors, layer_key):
    id = np.where(keys == layer_key)[0][0]
    data = tensors[id]
    if len(data.shape)!=1:
        return data.shape[-1], torch.from_numpy(data).permute(4, 3, 0 , 1, 2)
    else:
        return torch.from_numpy(data)


# transfer_conv(state_dict, keys, tensors, 'features.0', 'Conv2d_1a_7x7')
def transfer_conv(state_dict, keys, tensors, layer_key_pt, layer_key_tf):
    keys = np.array(keys)
    key_tf = 'InceptionV1/' + layer_key_tf
    key_pt = 'module.' + layer_key_pt

    # conv
    key_tf_weight = key_tf + '/weights'
    key_pt_weight = key_pt + '.conv.weight'
    oup, state_dict[key_pt_weight] = get_value(keys, tensors, key_tf_weight)
    # bn_gamma
    key_tf_bn_weight = torch.ones(oup)
    key_pt_bn_weight = key_pt + '.bn.weight'
    state_dict[key_pt_bn_weight] = key_tf_bn_weight
    # bn_beta
    key_tf_bn_bias = key_tf + '/BatchNorm/beta'
    key_pt_bn_bias = key_pt + '.bn.bias'
    state_dict[key_pt_bn_bias] = get_value(keys, tensors, key_tf_bn_bias)
    # bn_mean
    key_tf_bn_mean = key_tf + '/BatchNorm/moving_mean'
    key_pt_bn_mean = key_pt + '.bn.running_mean'
    state_dict[key_pt_bn_mean] = get_value(keys, tensors, key_tf_bn_mean)
    # bn_var
    key_tf_bn_var = key_tf + '/BatchNorm/moving_variance'
    key_pt_bn_var = key_pt + '.bn.running_var'
    state_dict[key_pt_bn_var] = get_value(keys, tensors, key_tf_bn_var)


# transfer_mixed_conv(state_dict, keys, tensors, 'features.5', 'Mixed_3b')
def transfer_mixed_conv(state_dict, keys, tensors, layer_key_pt, layer_key_tf):
    # branch 0
    key_tf = layer_key_tf + '/Branch_0/Conv2d_0a_1x1'
    key_pt = layer_key_pt + '.branch0.0'
    transfer_conv(state_dict, keys, tensors, key_pt, key_tf)
    # branch 1.0
    key_tf = layer_key_tf + '/Branch_1/Conv2d_0a_1x1'
    key_pt = layer_key_pt + '.branch1.0'
    transfer_conv(state_dict, keys, tensors, key_pt, key_tf)
    # branch 1.1
    key_tf = layer_key_tf + '/Branch_1/Conv2d_0b_3x3'
    key_pt = layer_key_pt + '.branch1.1'
    transfer_conv(state_dict, keys, tensors, key_pt, key_tf)
    # branch 2.0
    key_tf = layer_key_tf + '/Branch_2/Conv2d_0a_1x1'
    key_pt = layer_key_pt + '.branch2.0'
    transfer_conv(state_dict, keys, tensors, key_pt, key_tf)
    # branch 2.1
    key_tf = layer_key_tf + '/Branch_2/Conv2d_0b_3x3'
    key_pt = layer_key_pt + '.branch2.1'
    transfer_conv(state_dict, keys, tensors, key_pt, key_tf)
    # branch 3
    key_tf = layer_key_tf + '/Branch_3/Conv2d_0b_1x1'
    key_pt = layer_key_pt + '.branch3.1'
    transfer_conv(state_dict, keys, tensors, key_pt, key_tf)


def transfer_mixed_conv_5b(state_dict, keys, tensors, layer_key_pt, layer_key_tf):
    # branch 0
    key_tf = layer_key_tf + '/Branch_0/Conv2d_0a_1x1'
    key_pt = layer_key_pt + '.branch0.0'
    transfer_conv(state_dict, keys, tensors, key_pt, key_tf)
    # branch 1.0
    key_tf = layer_key_tf + '/Branch_1/Conv2d_0a_1x1'
    key_pt = layer_key_pt + '.branch1.0'
    transfer_conv(state_dict, keys, tensors, key_pt, key_tf)
    # branch 1.1
    key_tf = layer_key_tf + '/Branch_1/Conv2d_0b_3x3'
    key_pt = layer_key_pt + '.branch1.1'
    transfer_conv(state_dict, keys, tensors, key_pt, key_tf)
    # branch 2.0
    key_tf = layer_key_tf + '/Branch_2/Conv2d_0a_1x1'
    key_pt = layer_key_pt + '.branch2.0'
    transfer_conv(state_dict, keys, tensors, key_pt, key_tf)
    # branch 2.1************************************0a_3x3
    key_tf = layer_key_tf + '/Branch_2/Conv2d_0a_3x3'
    key_pt = layer_key_pt + '.branch2.1'
    transfer_conv(state_dict, keys, tensors, key_pt, key_tf)
    # branch 3
    key_tf = layer_key_tf + '/Branch_3/Conv2d_0b_1x1'
    key_pt = layer_key_pt + '.branch3.1'
    transfer_conv(state_dict, keys, tensors, key_pt, key_tf)


