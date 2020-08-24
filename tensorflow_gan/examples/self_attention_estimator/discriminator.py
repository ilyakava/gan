# coding=utf-8
# Copyright 2020 The TensorFlow GAN Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Discriminator definitions."""

import tensorflow as tf
from tensorflow_gan.examples import compat_utils
from tensorflow_gan.examples.self_attention_estimator import ops

from absl import flags

import pdb

def dsample(x):
  """Downsamples the input volume by means of average pooling.

  Args:
    x: The 4D input tensor.
  Returns:
    An downsampled version of the input tensor.
  """
  xd = compat_utils.nn_avg_pool2d(
      input=x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='VALID')
  return xd


def block(x, out_channels, name, downsample=True, act=tf.nn.relu):
  """Builds the residual blocks used in the discriminator.

  Args:
    x: The 4D input vector.
    out_channels: Number of features in the output layer.
    name: The variable scope name for the block.
    downsample: If True, downsample the spatial size the input tensor by
                a factor of 2 on each side. If False, the spatial size of the
                input tensor is unchanged.
    act: The activation function used in the block.
  Returns:
    A `Tensor` representing the output of the operation.
  """
  with tf.compat.v1.variable_scope(name):
    input_channels = x.shape.as_list()[-1]
    x_0 = x
    x = act(x)
    x = ops.snconv2d(x, out_channels, 3, 3, 1, 1, name='sn_conv1')
    x = act(x)
    x = ops.snconv2d(x, out_channels, 3, 3, 1, 1, name='sn_conv2')
    if downsample:
      x = dsample(x)
    if downsample or input_channels != out_channels:
      x_0 = ops.snconv2d(x_0, out_channels, 1, 1, 1, 1, name='sn_conv3')
      if downsample:
        x_0 = dsample(x_0)
    return x_0 + x
    

def optimized_block(x, out_channels, name, act=tf.nn.relu):
  """Builds optimized residual blocks for downsampling.

  Compared with block, optimized_block always downsamples the spatial resolution
  by a factor of 2 on each side.

  Args:
    x: The 4D input vector.
    out_channels: Number of features in the output layer.
    name: The variable scope name for the block.
    act: The activation function used in the block.
  Returns:
    A `Tensor` representing the output of the operation.
  """
  with tf.compat.v1.variable_scope(name):
    x_0 = x
    x = ops.snconv2d(x, out_channels, 3, 3, 1, 1, name='sn_conv1')
    x = act(x)
    x = ops.snconv2d(x, out_channels, 3, 3, 1, 1, name='sn_conv2')
    x = dsample(x)
    x_0 = dsample(x_0)
    x_0 = ops.snconv2d(x_0, out_channels, 1, 1, 1, 1, name='sn_conv3')
    return x + x_0

def discriminator_32_kplusone_wgan(image, labels, df_dim, number_classes, act=tf.nn.relu):
  """Builds the discriminator graph.

  Args:
    image: The current batch of images to classify as fake or real.
    labels: The corresponding labels for the images.
    df_dim: The df dimension.
    number_classes: The number of classes in the labels.
    act: The activation function used in the discriminator.
  Returns:
    - A `Tensor` representing the logits of the discriminator.
    - A list containing all trainable varaibles defined by the model.
  """
  del labels
  with tf.compat.v1.variable_scope(
      'discriminator', reuse=tf.compat.v1.AUTO_REUSE) as dis_scope:
    h0 = optimized_block(
        image, df_dim, 'd_optimized_block1', act=act)  # 64 * 64
    h1 = block(h0, df_dim * 4, 'd_block2', act=act)  # 32 * 32
    # h1 = ops.sn_non_local_block_sim(h1, name='d_ops')  # 32 * 32
    h2 = block(h1, df_dim * 4, 'd_block3', act=act)  # 16 * 16
    # h3 = block(h2, df_dim * 8, 'd_block4', act=act)  # 8 * 8
    # h4 = block(h3, df_dim * 16, 'd_block5', act=act)  # 4 * 4
    h5 = block(h2, df_dim * 4, 'd_block6', downsample=False, act=act)
    h5_act = act(h5)
    h6 = tf.reduce_sum(input_tensor=h5_act, axis=[1, 2])
    # output = ops.snlinear(h6, 1, name='d_sn_linear')
    # h_labels = ops.sn_embedding(labels, number_classes, df_dim * 4, name='d_embedding')
    classification_output = ops.snlinear(h6, flags.FLAGS.num_classes+1, name='d_sn_linear_kplusone')
    # output += tf.reduce_sum(input_tensor=h6 * h_labels, axis=1, keepdims=True)
    output = classification_output[:,flags.FLAGS.num_classes:]
    
  var_list = tf.compat.v1.get_collection(
      tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, dis_scope.name)
  return output, classification_output, var_list

def discriminator_32_kplusone_fm(image, labels, df_dim, number_classes, act=tf.nn.relu):
  """Builds the discriminator graph.

  Args:
    image: The current batch of images to classify as fake or real.
    labels: The corresponding labels for the images.
    df_dim: The df dimension.
    number_classes: The number of classes in the labels.
    act: The activation function used in the discriminator.
  Returns:
    - A `Tensor` representing the logits of the discriminator.
    - A list containing all trainable varaibles defined by the model.
  """
  del labels
  with tf.compat.v1.variable_scope(
      'discriminator', reuse=tf.compat.v1.AUTO_REUSE) as dis_scope:
    h0 = optimized_block(
        image, df_dim, 'd_optimized_block1', act=act)  # 64 * 64
    h1 = block(h0, df_dim * 4, 'd_block2', act=act)  # 32 * 32
    # h1 = ops.sn_non_local_block_sim(h1, name='d_ops')  # 32 * 32
    h2 = block(h1, df_dim * 4, 'd_block3', act=act)  # 16 * 16
    # h3 = block(h2, df_dim * 8, 'd_block4', act=act)  # 8 * 8
    # h4 = block(h3, df_dim * 16, 'd_block5', act=act)  # 4 * 4
    h5 = block(h2, df_dim * 4, 'd_block6', downsample=False, act=act)
    h5_act = act(h5)
    h6 = tf.reduce_sum(input_tensor=h5_act, axis=[1, 2])
    # output = ops.snlinear(h6, 1, name='d_sn_linear')
    # h_labels = ops.sn_embedding(labels, number_classes, df_dim * 4, name='d_embedding')
    classification_output = ops.snlinear(h6, flags.FLAGS.num_classes+1, name='d_sn_linear_kplusone')
    # output += tf.reduce_sum(input_tensor=h6 * h_labels, axis=1, keepdims=True)
    # output = classification_output[:,flags.FLAGS.num_classes:]
    output = h6
    
  var_list = tf.compat.v1.get_collection(
      tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, dis_scope.name)
  return output, classification_output, var_list
  
def discriminator_32_kplusone_fm_badgan(image, labels, df_dim, number_classes, act=tf.nn.leaky_relu):
  """Builds the discriminator graph.

  Args:
    image: The current batch of images to classify as fake or real.
    labels: The corresponding labels for the images.
    df_dim: The df dimension.
    number_classes: The number of classes in the labels.
    act: The activation function used in the discriminator.
  Returns:
    - A `Tensor` representing the logits of the discriminator.
    - A list containing all trainable varaibles defined by the model.
  """
  del labels
  noise = tf.compat.v1.keras.layers.GaussianNoise(0.05)
  with tf.compat.v1.variable_scope(
      'discriminator', reuse=tf.compat.v1.AUTO_REUSE) as dis_scope:
    
    image = tf.nn.dropout(noise(image), 0.2)
    x = act(ops.snconv2d(image, df_dim, 3, 3, 1, 1, name='sn_conv1'))
    x = act(ops.snconv2d(x, df_dim, 3, 3, 1, 1, name='sn_conv2'))
    x = act(ops.snconv2d(x, df_dim, 3, 3, 2, 2, name='sn_conv3'))
    x = tf.nn.dropout(x, 0.5)
    x = act(ops.snconv2d(x, 2*df_dim, 3, 3, 1, 1, name='sn_conv4'))
    x = act(ops.snconv2d(x, 2*df_dim, 3, 3, 1, 1, name='sn_conv5'))
    x = act(ops.snconv2d(x, 2*df_dim, 3, 3, 2, 2, name='sn_conv6'))
    x = tf.nn.dropout(x, 0.5)
    x = act(ops.snconv2d(x, 2*df_dim, 3, 3, 1, 1, name='sn_conv7'))
    x = act(ops.snconv2d(x, 2*df_dim, 1, 1, 1, 1, name='sn_conv8'))
    x = act(ops.snconv2d(x, 2*df_dim, 1, 1, 2, 2, name='sn_conv9'))

    h6 = tf.reduce_sum(input_tensor=x, axis=[1, 2])
    classification_output = ops.snlinear(h6, flags.FLAGS.num_classes+1, name='d_sn_linear_kplusone')
    output = h6
    
  var_list = tf.compat.v1.get_collection(
      tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, dis_scope.name)
  return output, classification_output, var_list
  
def discriminator_32_kplusone_fm_lrelu_dropout(image, labels, df_dim, number_classes, act=tf.nn.leaky_relu):
  """Builds the discriminator graph.

  Args:
    image: The current batch of images to classify as fake or real.
    labels: The corresponding labels for the images.
    df_dim: The df dimension.
    number_classes: The number of classes in the labels.
    act: The activation function used in the discriminator.
  Returns:
    - A `Tensor` representing the logits of the discriminator.
    - A list containing all trainable varaibles defined by the model.
  """
  del labels
  with tf.compat.v1.variable_scope(
      'discriminator', reuse=tf.compat.v1.AUTO_REUSE) as dis_scope:
    h0 = optimized_block(
        image, df_dim, 'd_optimized_block1', act=act)  # 16 * 16
    h0 = tf.nn.dropout(h0, 0.5)
    h1 = block(h0, df_dim * 4, 'd_block2', act=act)  # 8 * 8
    h1 = tf.nn.dropout(h1, 0.5)
    h2 = block(h1, df_dim * 4, 'd_block3', act=act)  # 4 * 4
    h2 = tf.nn.dropout(h2, 0.5)
    h5 = block(h2, df_dim * 4, 'd_block6', downsample=False, act=act)
    h5_act = act(h5)
    h6 = tf.reduce_sum(input_tensor=h5_act, axis=[1, 2])
    
    classification_output = ops.snlinear(h6, flags.FLAGS.num_classes+1, name='d_sn_linear_kplusone')
    
    output = h6
    
  var_list = tf.compat.v1.get_collection(
      tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, dis_scope.name)
  return output, classification_output, var_list

def discriminator_64_kplusone_fm(image, labels, df_dim, number_classes, act=tf.nn.relu):
  """Builds the discriminator graph.

  Args:
    image: The current batch of images to classify as fake or real.
    labels: The corresponding labels for the images.
    df_dim: The df dimension.
    number_classes: The number of classes in the labels.
    act: The activation function used in the discriminator.
  Returns:
    - A `Tensor` representing the logits of the discriminator.
    - A list containing all trainable varaibles defined by the model.
  """
  del labels
  with tf.compat.v1.variable_scope(
      'discriminator', reuse=tf.compat.v1.AUTO_REUSE) as dis_scope:
    h0 = optimized_block(
        image, df_dim, 'd_optimized_block1', act=act)  # 64 * 64
    h1 = block(h0, df_dim * 2, 'd_block2', act=act)  # 32 * 32
    h1 = ops.sn_non_local_block_sim(h1, name='d_ops')  # 32 * 32
    h2 = block(h1, df_dim * 4, 'd_block3', act=act)  # 16 * 16
    h3 = block(h2, df_dim * 8, 'd_block4', act=act)  # 8 * 8
    # h4 = block(h3, df_dim * 16, 'd_block5', act=act)  # 4 * 4
    h5 = block(h3, df_dim * 8, 'd_block6', downsample=False, act=act)
    h5_act = act(h5)
    h6 = tf.reduce_sum(input_tensor=h5_act, axis=[1, 2])
    # output = ops.snlinear(h6, 1, name='d_sn_linear')
    # h_labels = ops.sn_embedding(labels, number_classes, df_dim * 4, name='d_embedding')
    classification_output = ops.snlinear(h6, flags.FLAGS.num_classes+1, name='d_sn_linear_kplusone')
    # output += tf.reduce_sum(input_tensor=h6 * h_labels, axis=1, keepdims=True)
    # output = classification_output[:,flags.FLAGS.num_classes:]
    output = h6
    
  var_list = tf.compat.v1.get_collection(
      tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, dis_scope.name)
  return output, classification_output, var_list
  
def discriminator_128_kplusone_fm(image, labels, df_dim, number_classes, act=tf.nn.relu):
  """Builds the discriminator graph.

  Args:
    image: The current batch of images to classify as fake or real.
    labels: The corresponding labels for the images.
    df_dim: The df dimension.
    number_classes: The number of classes in the labels.
    act: The activation function used in the discriminator.
  Returns:
    - A `Tensor` representing the logits of the discriminator.
    - A list containing all trainable varaibles defined by the model.
  """
  del labels
  with tf.compat.v1.variable_scope(
      'discriminator', reuse=tf.compat.v1.AUTO_REUSE) as dis_scope:
    h0 = optimized_block(
        image, df_dim, 'd_optimized_block1', act=act)  # 64 * 64
    h1 = block(h0, df_dim * 2, 'd_block2', act=act)  # 32 * 32
    h1 = ops.sn_non_local_block_sim(h1, name='d_ops')  # 32 * 32
    h2 = block(h1, df_dim * 4, 'd_block3', act=act)  # 16 * 16
    h3 = block(h2, df_dim * 8, 'd_block4', act=act)  # 8 * 8
    h4 = block(h3, df_dim * 16, 'd_block5', act=act)  # 4 * 4
    h5 = block(h4, df_dim * 16, 'd_block6', downsample=False, act=act)
    h5_act = act(h5)
    h6 = tf.reduce_sum(input_tensor=h5_act, axis=[1, 2])
    # output = ops.snlinear(h6, 1, name='d_sn_linear')
    # h_labels = ops.sn_embedding(labels, number_classes, df_dim * 4, name='d_embedding')
    classification_output = ops.snlinear(h6, flags.FLAGS.num_classes+1, name='d_sn_linear_kplusone')
    # output += tf.reduce_sum(input_tensor=h6 * h_labels, axis=1, keepdims=True)
    # output = classification_output[:,flags.FLAGS.num_classes:]
    output = h6
    
  var_list = tf.compat.v1.get_collection(
      tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, dis_scope.name)
  return output, classification_output, var_list

def discriminator_32(image, labels, df_dim, number_classes, act=tf.nn.relu):
  """Builds the discriminator graph.

  Args:
    image: The current batch of images to classify as fake or real.
    labels: The corresponding labels for the images.
    df_dim: The df dimension.
    number_classes: The number of classes in the labels.
    act: The activation function used in the discriminator.
  Returns:
    - A `Tensor` representing the logits of the discriminator.
    - A list containing all trainable varaibles defined by the model.
  """
  with tf.compat.v1.variable_scope(
      'discriminator', reuse=tf.compat.v1.AUTO_REUSE) as dis_scope:
    h0 = optimized_block(
        image, df_dim, 'd_optimized_block1', act=act)  # 64 * 64
    h1 = block(h0, df_dim * 4, 'd_block2', act=act)  # 32 * 32
    # h1 = ops.sn_non_local_block_sim(h1, name='d_ops')  # 32 * 32
    h2 = block(h1, df_dim * 4, 'd_block3', act=act)  # 16 * 16
    # h3 = block(h2, df_dim * 8, 'd_block4', act=act)  # 8 * 8
    # h4 = block(h3, df_dim * 16, 'd_block5', act=act)  # 4 * 4
    h5 = block(h2, df_dim * 4, 'd_block6', downsample=False, act=act)
    h5_act = act(h5)
    h6 = tf.reduce_sum(input_tensor=h5_act, axis=[1, 2])
    output = ops.snlinear(h6, 1, name='d_sn_linear')
    classification_output = ops.snlinear(h6, flags.FLAGS.num_classes, name='d_sn_linear_class')
    if labels is None:
      pseudo_labels = tf.argmax(classification_output, axis=1)
      h_labels = ops.sn_embedding(pseudo_labels, number_classes, df_dim * 4, name='d_embedding')
    else:
      h_labels = ops.sn_embedding(labels, number_classes, df_dim * 4, name='d_embedding')
    
    output += tf.reduce_sum(input_tensor=h6 * h_labels, axis=1, keepdims=True)
    
  var_list = tf.compat.v1.get_collection(
      tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, dis_scope.name)
  return output, classification_output, var_list
  
def discriminator_32_noproj(image, labels, df_dim, number_classes, act=tf.nn.relu):
  """Builds the discriminator graph.

  Args:
    image: The current batch of images to classify as fake or real.
    labels: The corresponding labels for the images.
    df_dim: The df dimension.
    number_classes: The number of classes in the labels.
    act: The activation function used in the discriminator.
  Returns:
    - A `Tensor` representing the logits of the discriminator.
    - A list containing all trainable varaibles defined by the model.
  """
  with tf.compat.v1.variable_scope(
      'discriminator', reuse=tf.compat.v1.AUTO_REUSE) as dis_scope:
    h0 = optimized_block(
        image, df_dim, 'd_optimized_block1', act=act)  # 64 * 64
    h1 = block(h0, df_dim * 4, 'd_block2', act=act)  # 32 * 32
    # h1 = ops.sn_non_local_block_sim(h1, name='d_ops')  # 32 * 32
    h2 = block(h1, df_dim * 4, 'd_block3', act=act)  # 16 * 16
    # h3 = block(h2, df_dim * 8, 'd_block4', act=act)  # 8 * 8
    # h4 = block(h3, df_dim * 16, 'd_block5', act=act)  # 4 * 4
    h5 = block(h2, df_dim * 4, 'd_block6', downsample=False, act=act)
    h5_act = act(h5)
    h6 = tf.reduce_sum(input_tensor=h5_act, axis=[1, 2])
    output = ops.snlinear(h6, 1, name='d_sn_linear')
    # h_labels = ops.sn_embedding(labels, number_classes, df_dim * 4,
    #                             name='d_embedding')
    classification_output = ops.snlinear(h6, flags.FLAGS.num_classes, name='d_sn_linear_class')
    # output += tf.reduce_sum(input_tensor=h6 * h_labels, axis=1, keepdims=True)
    
  var_list = tf.compat.v1.get_collection(
      tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, dis_scope.name)
  return output, classification_output, var_list
  


def discriminator_64(image, labels, df_dim, number_classes, act=tf.nn.relu):
  """Builds the discriminator graph.

  Args:
    image: The current batch of images to classify as fake or real.
    labels: The corresponding labels for the images.
    df_dim: The df dimension.
    number_classes: The number of classes in the labels.
    act: The activation function used in the discriminator.
  Returns:
    - A `Tensor` representing the logits of the discriminator.
    - A list containing all trainable varaibles defined by the model.
  """
  with tf.compat.v1.variable_scope(
      'discriminator', reuse=tf.compat.v1.AUTO_REUSE) as dis_scope:
    h0 = optimized_block(
        image, df_dim, 'd_optimized_block1', act=act)  # 64 * 64
    h1 = block(h0, df_dim * 2, 'd_block2', act=act)  # 32 * 32
    h1 = ops.sn_non_local_block_sim(h1, name='d_ops')  # 32 * 32
    h2 = block(h1, df_dim * 4, 'd_block3', act=act)  # 16 * 16
    h3 = block(h2, df_dim * 8, 'd_block4', act=act)  # 8 * 8
    # h4 = block(h3, df_dim * 16, 'd_block5', act=act)  # 4 * 4
    h5 = block(h3, df_dim * 8, 'd_block6', downsample=False, act=act)
    h5_act = act(h5)
    h6 = tf.reduce_sum(input_tensor=h5_act, axis=[1, 2])
    output = ops.snlinear(h6, 1, name='d_sn_linear')
    classification_output = ops.snlinear(h6, flags.FLAGS.num_classes, name='d_sn_linear_class')
    if labels is None:
      pseudo_labels = tf.argmax(classification_output, axis=1)
      h_labels = ops.sn_embedding(pseudo_labels, number_classes, df_dim * 8, name='d_embedding')
    else:
      h_labels = ops.sn_embedding(labels, number_classes, df_dim * 8, name='d_embedding')
    
    output += tf.reduce_sum(input_tensor=h6 * h_labels, axis=1, keepdims=True)
    
  var_list = tf.compat.v1.get_collection(
      tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, dis_scope.name)
  return output, classification_output, var_list
  
def discriminator_64_noproj(image, labels, df_dim, number_classes, act=tf.nn.relu):
  """Builds the discriminator graph.

  Args:
    image: The current batch of images to classify as fake or real.
    labels: The corresponding labels for the images.
    df_dim: The df dimension.
    number_classes: The number of classes in the labels.
    act: The activation function used in the discriminator.
  Returns:
    - A `Tensor` representing the logits of the discriminator.
    - A list containing all trainable varaibles defined by the model.
  """
  with tf.compat.v1.variable_scope(
      'discriminator', reuse=tf.compat.v1.AUTO_REUSE) as dis_scope:
    h0 = optimized_block(
        image, df_dim, 'd_optimized_block1', act=act)  # 64 * 64
    h1 = block(h0, df_dim * 2, 'd_block2', act=act)  # 32 * 32
    h1 = ops.sn_non_local_block_sim(h1, name='d_ops')  # 32 * 32
    h2 = block(h1, df_dim * 4, 'd_block3', act=act)  # 16 * 16
    h3 = block(h2, df_dim * 8, 'd_block4', act=act)  # 8 * 8
    # h4 = block(h3, df_dim * 16, 'd_block5', act=act)  # 4 * 4
    h5 = block(h3, df_dim * 8, 'd_block6', downsample=False, act=act)
    h5_act = act(h5)
    h6 = tf.reduce_sum(input_tensor=h5_act, axis=[1, 2])
    output = ops.snlinear(h6, 1, name='d_sn_linear')
    # h_labels = ops.sn_embedding(labels, number_classes, df_dim * 16,
    #                             name='d_embedding')
    classification_output = ops.snlinear(h6, flags.FLAGS.num_classes, name='d_sn_linear_class')
    # output += tf.reduce_sum(input_tensor=h6 * h_labels, axis=1, keepdims=True)
    
  var_list = tf.compat.v1.get_collection(
      tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, dis_scope.name)
  return output, classification_output, var_list

def discriminator_32_multiproj(image, labels, df_dim, number_classes, act=tf.nn.relu):
  """Builds the discriminator graph.

  Args:
    image: The current batch of images to classify as fake or real.
    labels: The corresponding labels for the images.
    df_dim: The df dimension.
    number_classes: The number of classes in the labels.
    act: The activation function used in the discriminator.
  Returns:
    - A `Tensor` representing the logits of the discriminator.
    - A list containing all trainable varaibles defined by the model.
  """
  with tf.compat.v1.variable_scope(
      'discriminator', reuse=tf.compat.v1.AUTO_REUSE) as dis_scope:
    h0 = optimized_block(
        image, df_dim, 'd_optimized_block1', act=act)  # 64 * 64
    h1 = block(h0, df_dim * 4, 'd_block2', act=act)  # 32 * 32
    # h1 = ops.sn_non_local_block_sim(h1, name='d_ops')  # 32 * 32
    h2 = block(h1, df_dim * 4, 'd_block3', act=act)  # 16 * 16
    # h3 = block(h2, df_dim * 8, 'd_block4', act=act)  # 8 * 8
    # h4 = block(h3, df_dim * 16, 'd_block5', act=act)  # 4 * 4
    h5 = block(h2, df_dim * 4, 'd_block6', downsample=False, act=act)
    h5_act = act(h5)
    h6 = tf.reduce_sum(input_tensor=h5_act, axis=[1, 2])
    output = ops.snlinear(h6, 1, name='d_sn_linear')
    
    h_labels = ops.sn_embedding(labels, number_classes, df_dim * 4, name='d_embedding')
    all_labels = ops.sn_embedding(tf.range(0,flags.FLAGS.num_classes), number_classes, df_dim * 4, name='d_embedding')
    classification_output = tf.matmul(a=h6, b=all_labels, transpose_b=True)
    output += tf.reduce_sum(input_tensor=h6 * h_labels, axis=1, keepdims=True)
    
  var_list = tf.compat.v1.get_collection(
      tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, dis_scope.name)
  return output, classification_output, var_list

def discriminator_64_multiproj(image, labels, df_dim, number_classes, act=tf.nn.relu):
  """Builds the discriminator graph.

  Args:
    image: The current batch of images to classify as fake or real.
    labels: The corresponding labels for the images.
    df_dim: The df dimension.
    number_classes: The number of classes in the labels.
    act: The activation function used in the discriminator.
  Returns:
    - A `Tensor` representing the logits of the discriminator.
    - A list containing all trainable varaibles defined by the model.
  """
  with tf.compat.v1.variable_scope(
      'discriminator', reuse=tf.compat.v1.AUTO_REUSE) as dis_scope:
    h0 = optimized_block(
        image, df_dim, 'd_optimized_block1', act=act)  # 64 * 64
    h1 = block(h0, df_dim * 2, 'd_block2', act=act)  # 32 * 32
    h1 = ops.sn_non_local_block_sim(h1, name='d_ops')  # 32 * 32
    h2 = block(h1, df_dim * 4, 'd_block3', act=act)  # 16 * 16
    h3 = block(h2, df_dim * 8, 'd_block4', act=act)  # 8 * 8
    # h4 = block(h3, df_dim * 16, 'd_block5', act=act)  # 4 * 4
    h5 = block(h3, df_dim * 8, 'd_block6', downsample=False, act=act)
    h5_act = act(h5)
    h6 = tf.reduce_sum(input_tensor=h5_act, axis=[1, 2])
    output = ops.snlinear(h6, 1, name='d_sn_linear')
    h_labels = ops.sn_embedding(labels, number_classes, df_dim * 8, name='d_embedding')
    all_labels = ops.sn_embedding(tf.range(0,flags.FLAGS.num_classes), number_classes, df_dim * 8, name='d_embedding')
    classification_output = tf.matmul(a=h6, b=all_labels, transpose_b=True)
    output += tf.reduce_sum(input_tensor=h6 * h_labels, axis=1, keepdims=True)
    
  var_list = tf.compat.v1.get_collection(
      tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, dis_scope.name)
  return output, classification_output, var_list

def discriminator_128_multiproj(image, labels, df_dim, number_classes, act=tf.nn.relu):
  """Builds the discriminator graph.

  Args:
    image: The current batch of images to classify as fake or real.
    labels: The corresponding labels for the images.
    df_dim: The df dimension.
    number_classes: The number of classes in the labels.
    act: The activation function used in the discriminator.
  Returns:
    - A `Tensor` representing the logits of the discriminator.
    - A list containing all trainable varaibles defined by the model.
  """
  with tf.compat.v1.variable_scope(
      'discriminator', reuse=tf.compat.v1.AUTO_REUSE) as dis_scope:
    h0 = optimized_block(
        image, df_dim, 'd_optimized_block1', act=act)  # 64 * 64
    h1 = block(h0, df_dim * 2, 'd_block2', act=act)  # 32 * 32
    h1 = ops.sn_non_local_block_sim(h1, name='d_ops')  # 32 * 32
    h2 = block(h1, df_dim * 4, 'd_block3', act=act)  # 16 * 16
    h3 = block(h2, df_dim * 8, 'd_block4', act=act)  # 8 * 8
    h4 = block(h3, df_dim * 16, 'd_block5', act=act)  # 4 * 4
    h5 = block(h4, df_dim * 16, 'd_block6', downsample=False, act=act)
    h5_act = act(h5)
    h6 = tf.reduce_sum(input_tensor=h5_act, axis=[1, 2])
    output = ops.snlinear(h6, 1, name='d_sn_linear')
    h_labels = ops.sn_embedding(labels, number_classes, df_dim * 16, name='d_embedding')
    all_labels = ops.sn_embedding(tf.range(0,flags.FLAGS.num_classes), number_classes, df_dim * 16, name='d_embedding')
    classification_output = tf.matmul(a=h6, b=all_labels, transpose_b=True)
    output += tf.reduce_sum(input_tensor=h6 * h_labels, axis=1, keepdims=True)
    
  var_list = tf.compat.v1.get_collection(
      tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, dis_scope.name)
  return output, classification_output, var_list
  
def discriminator_128(image, labels, df_dim, number_classes, act=tf.nn.relu):
  """Builds the discriminator graph.

  Args:
    image: The current batch of images to classify as fake or real.
    labels: The corresponding labels for the images.
    df_dim: The df dimension.
    number_classes: The number of classes in the labels.
    act: The activation function used in the discriminator.
  Returns:
    - A `Tensor` representing the logits of the discriminator.
    - A list containing all trainable varaibles defined by the model.
  """
  with tf.compat.v1.variable_scope(
      'discriminator', reuse=tf.compat.v1.AUTO_REUSE) as dis_scope:
    h0 = optimized_block(
        image, df_dim, 'd_optimized_block1', act=act)  # 64 * 64
    h1 = block(h0, df_dim * 2, 'd_block2', act=act)  # 32 * 32
    h1 = ops.sn_non_local_block_sim(h1, name='d_ops')  # 32 * 32
    h2 = block(h1, df_dim * 4, 'd_block3', act=act)  # 16 * 16
    h3 = block(h2, df_dim * 8, 'd_block4', act=act)  # 8 * 8
    h4 = block(h3, df_dim * 16, 'd_block5', act=act)  # 4 * 4
    h5 = block(h4, df_dim * 16, 'd_block6', downsample=False, act=act)
    h5_act = act(h5)
    h6 = tf.reduce_sum(input_tensor=h5_act, axis=[1, 2])
    output = ops.snlinear(h6, 1, name='d_sn_linear')
    classification_output = ops.snlinear(h6, flags.FLAGS.num_classes, name='d_sn_linear_class')
    if labels is None:
      pseudo_labels = tf.argmax(classification_output, axis=1)
      h_labels = ops.sn_embedding(pseudo_labels, number_classes, df_dim * 16, name='d_embedding')
    else:
      h_labels = ops.sn_embedding(labels, number_classes, df_dim * 16, name='d_embedding')
    
    output += tf.reduce_sum(input_tensor=h6 * h_labels, axis=1, keepdims=True)
    
  var_list = tf.compat.v1.get_collection(
      tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, dis_scope.name)
  return output, classification_output, var_list
  
def biggan_discriminator_128(image, labels, df_dim, number_classes, act=tf.nn.relu):
  """Builds the discriminator graph.
  
  TODO(ilyak): debug, this implementation doesn't work as is.
  ...
  Only position of the non local block changes
  """
  with tf.compat.v1.variable_scope(
      'discriminator', reuse=tf.compat.v1.AUTO_REUSE) as dis_scope:
    h0 = optimized_block(
        image, df_dim, 'd_optimized_block1', act=act)  # 64 * 64
    h0 = ops.sn_non_local_block_sim(h0, name='d_ops')  # 64 * 64
    h1 = block(h0, df_dim * 2, 'd_block2', act=act)  # 32 * 32
    h2 = block(h1, df_dim * 4, 'd_block3', act=act)  # 16 * 16
    h3 = block(h2, df_dim * 8, 'd_block4', act=act)  # 8 * 8
    h4 = block(h3, df_dim * 16, 'd_block5', act=act)  # 4 * 4
    h5 = block(h4, df_dim * 16, 'd_block6', downsample=False, act=act)
    h5_act = act(h5)
    h6 = tf.reduce_sum(input_tensor=h5_act, axis=[1, 2])
    output = ops.snlinear(h6, 1, name='d_sn_linear')
    classification_output = ops.snlinear(h6, flags.FLAGS.num_classes, name='d_sn_linear_class')
    if labels is None:
      pseudo_labels = tf.argmax(classification_output, axis=1)
      h_labels = ops.sn_embedding(pseudo_labels, number_classes, df_dim * 16, name='d_embedding')
    else:
      h_labels = ops.sn_embedding(labels, number_classes, df_dim * 16, name='d_embedding')
    
    output += tf.reduce_sum(input_tensor=h6 * h_labels, axis=1, keepdims=True)
    
  var_list = tf.compat.v1.get_collection(
      tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, dis_scope.name)
  return output, classification_output, var_list

def discriminator_128_noproj(image, labels, df_dim, number_classes, act=tf.nn.relu):
  """Builds the discriminator graph.

  Args:
    image: The current batch of images to classify as fake or real.
    labels: The corresponding labels for the images.
    df_dim: The df dimension.
    number_classes: The number of classes in the labels.
    act: The activation function used in the discriminator.
  Returns:
    - A `Tensor` representing the logits of the discriminator.
    - A list containing all trainable varaibles defined by the model.
  """
  with tf.compat.v1.variable_scope(
      'discriminator', reuse=tf.compat.v1.AUTO_REUSE) as dis_scope:
    h0 = optimized_block(
        image, df_dim, 'd_optimized_block1', act=act)  # 64 * 64
    h1 = block(h0, df_dim * 2, 'd_block2', act=act)  # 32 * 32
    h1 = ops.sn_non_local_block_sim(h1, name='d_ops')  # 32 * 32
    h2 = block(h1, df_dim * 4, 'd_block3', act=act)  # 16 * 16
    h3 = block(h2, df_dim * 8, 'd_block4', act=act)  # 8 * 8
    h4 = block(h3, df_dim * 16, 'd_block5', act=act)  # 4 * 4
    h5 = block(h4, df_dim * 16, 'd_block6', downsample=False, act=act)
    h5_act = act(h5)
    h6 = tf.reduce_sum(input_tensor=h5_act, axis=[1, 2])
    output = ops.snlinear(h6, 1, name='d_sn_linear')
    # h_labels = ops.sn_embedding(labels, number_classes, df_dim * 16,
    #                             name='d_embedding')
    classification_output = ops.snlinear(h6, flags.FLAGS.num_classes, name='d_sn_linear_class')
    # output += tf.reduce_sum(input_tensor=h6 * h_labels, axis=1, keepdims=True)
    
  var_list = tf.compat.v1.get_collection(
      tf.compat.v1.GraphKeys.TRAINABLE_VARIABLES, dis_scope.name)
  return output, classification_output, var_list

discriminators = {
  (32, 'kplusone_fm'): discriminator_32_kplusone_fm,
  (64, 'kplusone_fm'): discriminator_64_kplusone_fm,
  (128, 'kplusone_fm'): discriminator_128_kplusone_fm,
  (32, 'kplusone_wgan'): discriminator_32_kplusone_wgan,
  (32, 'acgan'): discriminator_32,
  (32, 'acgan_noproj'): discriminator_32_noproj,
  (64, 'acgan_noproj'): discriminator_64_noproj,
  (64, 'acgan_multiproj'): discriminator_64_multiproj,
  (128, 'acgan_noproj'): discriminator_128_noproj,
  (64, 'acgan'): discriminator_64,
  (128, 'acgan'): discriminator_128,
  (128, 'acgan_multiproj'): discriminator_128_multiproj,
  (32, 'acgan_multiproj'): discriminator_32_multiproj,
  (128, 'biggan_acgan'): biggan_discriminator_128,
  (32, 'kplusone_fm_badgan'): discriminator_32_kplusone_fm_badgan,
  (32, 'kplusone_fm_lrelu_dropout'): discriminator_32_kplusone_fm_lrelu_dropout,
}

discriminator = discriminators[flags.FLAGS.image_size, flags.FLAGS.critic_type]