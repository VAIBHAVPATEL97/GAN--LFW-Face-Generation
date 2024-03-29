# -*- coding: utf-8 -*-
"""ganfacegenrator.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Faq0pCq6x7CtQnWoh9y-r7bKOHCjFvDW
"""
import tensorflow as tf
import matplotlib as pyplot

#%% DOWNLOAD DATABASE
data_dir = './data'

# FloydHub - Use with data ID "R5KrjnANiKVhLWAkpXhNBe"
data_dir = './input'


"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
import helper

#helper.download_extract('mnist', data_dir)
helper.download_extract('celeba', data_dir)
#%% EXPLORE MNIST DATABASE
#show_n_images = 25
#
#"""
#DON'T MODIFY ANYTHING IN THIS CELL
#"""
## %matplotlib inline
import os
from glob import glob
from matplotlib import pyplot
#
#mnist_images = helper.get_batch(glob(os.path.join(data_dir, 'mnist/*.jpg'))[:show_n_images], 28, 28, 'L')
#pyplot.imshow(helper.images_square_grid(mnist_images, 'L'), cmap='gray')
#%% EXPLORE celebA database
show_n_images = 25

"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
mnist_images = helper.get_batch(glob(os.path.join(data_dir, 'img_align_celeba/*.jpg'))[:show_n_images], 28, 28, 'RGB')
pyplot.imshow(helper.images_square_grid(mnist_images, 'RGB'))
#%% INPUT
import problem_unittests as tests

def model_inputs(image_width, image_height, image_channels, z_dim):
    """
    Create the model inputs
    :param image_width: The input image width
    :param image_height: The input image height
    :param image_channels: The number of image channels
    :param z_dim: The dimension of Z
    :return: Tuple of (tensor of real input images, tensor of z data, learning rate)
    """
    
    inputs_real = tf.placeholder(tf.float32, [None, image_width, image_height, image_channels], name="input_real")
    inputs_z = tf.placeholder(tf.float32, [None, z_dim], name="input_z") 
    learning_rate = tf.placeholder(tf.float32, name="learning_rate")
    
    return inputs_real, inputs_z, learning_rate



"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_model_inputs(model_inputs)
#%% DISCRIMINATOR
def discriminator(images, reuse=False):
    """
    Create the discriminator network
    :param image: Tensor of input image(s)
    :param reuse: Boolean if the weights should be reused
    :return: Tuple of (tensor output of the discriminator, tensor logits of the discriminator)
    """

    alpha = 0.2
        
    with tf.variable_scope('discriminator', reuse=reuse):
        
        # Start conv stack
        
        # Input layer shape 28x28x3 
        x1 = tf.layers.conv2d(images, 64, 5, strides=2, padding='same')
        relu1 = tf.maximum(alpha * x1, x1) # relu1.shape: 14x14x64
                
                
        # Second convolution layer
        x2 = tf.layers.conv2d(relu1, 128, 5, strides=2, padding='same')
        bn2 = tf.layers.batch_normalization(x2, training=True)
        relu2 = tf.maximum(alpha * bn2, bn2) # relu2.shape: 7x7x128
                
        # Third convolution layer
        x3 = tf.layers.conv2d(relu2, 256, 5, strides=2, padding='same')
        bn3 = tf.layers.batch_normalization(x3, training=True)
        relu3 = tf.maximum(alpha * bn3, bn3)  # relu3.shape: 4x4x256
              
        # Flatten it
        flat = tf.reshape(relu3, (-1, 4*4*256))
        logits = tf.layers.dense(flat, 1)
        out = tf.sigmoid(logits)
                              
        return out, logits

"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_discriminator(discriminator, tf)
#%% GENERATOR
#from IPython.core.debugger import set_trace
import tensorflow as tf
def generator(z, out_channel_dim, is_train=True):
    """
    Create the generator network
    :param z: Input z
    :param out_channel_dim: The number of channels in the output image
    :param is_train: Boolean if generator is being used for training
    :return: The tensor output of the generator
    """
    
    alpha = 0.2
             
    with tf.variable_scope('generator', reuse=not is_train):
        
        # reuse = not is_train should be used because we want to reuse the parameters when we are generating 
        # the samples but that will not be during the training. 
        # initially the generator will start off by training and not by generating images....
        # so the value of is_train should be True...because it decides whether generator is training or not
        
        # https://stackoverflow.com/questions/35980044/getting-the-output-shape-of-deconvolution-layer-using-tf-nn-conv2d-transpose-in
               
        # First fully connected layer
        # x1 = tf.layers.dense(z, 2*2*256) # starting with this number of units performs worse
        x1 = tf.layers.dense(z, 7*7*256)
                
        # Reshape and start deconv stack
        x1 = tf.reshape(x1, (-1, 7, 7, 256))
        x1 = tf.layers.batch_normalization(x1, training=is_train)
        x1 = tf.maximum(alpha * x1, x1) # shape: 7x7x256
   
        # Second convolution layer
        x2 = tf.layers.conv2d_transpose(x1, 128, 5, strides=2, padding='same')   
        x2 = tf.layers.batch_normalization(x2, training=is_train)
        x2 = tf.maximum(alpha * x2, x2) # shape 14x14x128
        
        # Third convolution layer    
        x3 = tf.layers.conv2d_transpose(x2, 64, 5, strides=2, padding='same')
        x3 = tf.layers.batch_normalization(x3, training=is_train)
        x3 = tf.maximum(alpha * x3, x3) # shape: 28x28x64
        # print(x3.shape)
        
        # Dropout --> loss is not improving adding dropout
        drop = tf.nn.dropout(x3, keep_prob=0.5)
               
        # Output layer
        logits = tf.layers.conv2d_transpose(drop, out_channel_dim, 5, strides=1, padding='same')
               
        # print(logits.shape) # 28x28x5
                               
        out = tf.tanh(logits)
            
        return out
       


"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_generator(generator, tf)
#%% LOSS
def model_loss(input_real, input_z, out_channel_dim):
    """
    Get the loss for the discriminator and generator
    :param input_real: Images from the real dataset
    :param input_z: Z input
    :param out_channel_dim: The number of channels in the output image
    :return: A tuple of (discriminator loss, generator loss)
    """
    
    smooth = 0.1 # label smoothing
    
    g_model = generator(input_z, out_channel_dim, is_train=True)
    d_model_real, d_logits_real = discriminator(input_real, reuse=False)
    d_model_fake, d_logits_fake = discriminator(g_model, reuse=True)

    d_loss_real = tf.reduce_mean(
        tf.nn.sigmoid_cross_entropy_with_logits(logits=d_logits_real, labels=tf.ones_like(d_model_real)*(1 - smooth)))
    
    d_loss_fake = tf.reduce_mean(
        tf.nn.sigmoid_cross_entropy_with_logits(logits=d_logits_fake, labels=tf.zeros_like(d_model_fake)))
    
    g_loss = tf.reduce_mean(
        tf.nn.sigmoid_cross_entropy_with_logits(logits=d_logits_fake, labels=tf.ones_like(d_model_fake)))

    d_loss = d_loss_real + d_loss_fake
        
    return d_loss, g_loss
    

"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_model_loss(model_loss)
#%% OPTIMIZATION
def model_opt(d_loss, g_loss, learning_rate, beta1):
    """
    Get optimization operations
    :param d_loss: Discriminator loss Tensor
    :param g_loss: Generator loss Tensor
    :param learning_rate: Learning Rate Placeholder
    :param beta1: The exponential decay rate for the 1st moment in the optimizer
    :return: A tuple of (discriminator training operation, generator training operation)
    """
    
    # https://discussions.udacity.com/t/project-5-net-not-training/246936/10
    
    # Get weights and bias to update
    
    t_vars = tf.trainable_variables()
    d_vars = [var for var in t_vars if var.name.startswith('discriminator')]
    g_vars = [var for var in t_vars if var.name.startswith('generator')]
    
    update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
    
    d_updates = [opt for opt in update_ops if opt.name.startswith('discriminator')]
    g_updates = [opt for opt in update_ops if opt.name.startswith('generator')]

    with tf.control_dependencies(d_updates):
        d_opt = tf.train.AdamOptimizer(learning_rate=learning_rate, beta1=beta1).minimize(d_loss, var_list=d_vars)

    with tf.control_dependencies(g_updates):
        g_opt = tf.train.AdamOptimizer(learning_rate=learning_rate, beta1=beta1).minimize(g_loss, var_list=g_vars)
            
    return d_opt, g_opt

"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
tests.test_model_opt(model_opt, tf)
#%% NEURAL NETWORK TRAINING
"""
DON'T MODIFY ANYTHING IN THIS CELL
"""
import numpy as np
import matplotlib.pyplot as plt
#import cv2

def show_generator_output(sess, n_images, input_z, out_channel_dim, image_mode):
    """
    Show example output for the generator
    :param sess: TensorFlow session
    :param n_images: Number of Images to display
    :param input_z: Input Z Tensor
    :param out_channel_dim: The number of channels in the output image
    :param image_mode: The mode to use for images ("RGB" or "L")
    """
    cmap = None if image_mode == 'RGB' else 'gray'
    z_dim = input_z.get_shape().as_list()[-1]
    example_z = np.random.uniform(-1, 1, size=[n_images, z_dim])

    samples = sess.run(
        generator(input_z, out_channel_dim, False),
        feed_dict={input_z: example_z})
   
    images_grid = helper.images_square_grid(samples, image_mode)

#    op=images_mode
#    cv2.imwrite('ggg_n'+'.jpeg',op)
    #plt.savefig('image_grid.png')
    pyplot.imshow(images_grid, cmap=cmap)
#    plt.legend(img)
        
    #plt.savefig('image_grid.png')

    pyplot.show()
#%%TRAIN

    
def train(epoch_count, batch_size, z_dim, learning_rate, beta1, get_batches, data_shape, data_image_mode):
    """
    Train the GAN
    :param epoch_count: Number of epochs
    :param batch_size: Batch Size
    :param z_dim: Z dimension
    :param learning_rate: Learning Rate
    :param beta1: The exponential decay rate for the 1st moment in the optimizer
    :param get_batches: Function to get batches
    :param data_shape: Shape of the data
    :param data_image_mode: The image mode to use for images ("RGB" or "L")
    """
        
    import matplotlib.pyplot as plt
    import cv2   
    print_every=10 
    show_every=100
    
    input_real, input_z, lr = model_inputs(data_shape[1], data_shape[2], data_shape[3], z_dim)
    d_loss, g_loss = model_loss(input_real, input_z, data_shape[3])
    d_opt, g_opt = model_opt(d_loss, g_loss, learning_rate, beta1)
    
    steps = 0
    
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for epoch_i in range(epoch_count):
            for batch_images in get_batches(batch_size):
                
                steps += 1
                
                # https://discussions.udacity.com/t/generator-loss-greater-than-discriminator-loss/247897/3
                
                
                batch_z = np.random.uniform(-1, 1, size=(batch_size, z_dim))
                batch_images *= 2
                
                _ = sess.run(d_opt, feed_dict={input_real: batch_images, input_z: batch_z})
                _ = sess.run(g_opt, feed_dict={input_z: batch_z})

                if steps % print_every == 0:
                    train_loss_d = d_loss.eval({input_z: batch_z, input_real: batch_images})
                    train_loss_g = g_loss.eval({input_z: batch_z})
#                    lines=plt.plot( epoch_i,train_loss_d,'*')
#                    plt.legend(loc='best')
                    #plt.setp(lines)
#                    alpha: float
#                    animated: [True | False]
#                    plt.show()
                   

                    print("Epoch {}/{}...".format(epoch_i + 1, epochs),
                          "Discriminator Loss: {:.4f}...".format(train_loss_d),
                          "Generator Loss: {:.4f}".format(train_loss_g))
                    

                if steps % show_every == 0:
                     show_generator_output(sess, 25, input_z, data_shape[3], data_image_mode)
                   #  cv2.imwrite('image_)
                     
                  
#%% MNIST TRAIN
#batch_size = 64 # worse with 32 and greater lr
#z_dim = 100
#learning_rate = 0.002 # worse with greater lr
#beta1 = 0.3
#
#
#"""
#DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
#"""
#epochs = 2
#
#mnist_dataset = helper.Dataset('mnist', glob(os.path.join(data_dir, 'mnist/*.jpg')))
#with tf.Graph().as_default():
#    train(epochs, batch_size, z_dim, learning_rate, beta1, mnist_dataset.get_batches,
#          mnist_dataset.shape, mnist_dataset.image_mode)
#%% CELEB A TRAIN
batch_size = 1 # worse with 32 and greater lr
z_dim = 100
learning_rate = 0.001 # worse with greater lr
beta1 = 0.2



"""
DON'T MODIFY ANYTHING IN THIS CELL THAT IS BELOW THIS LINE
"""
epochs = 20

celeba_dataset = helper.Dataset('celeba', glob(os.path.join(data_dir, 'img_align_celeba/*.jpg')))
with tf.Graph().as_default():
    train(epochs, batch_size, z_dim, learning_rate, beta1, celeba_dataset.get_batches,
          celeba_dataset.shape, celeba_dataset.image_mode)
          #%%
#import plotly.plotly as py
#import plotly.graph_objs as go
#
## Create random data with numpy
#import numpy as np
#
#N = 500
#random_x = np.linspace(0, 1, N)
#random_y = np.random.randn(N)
#
## Create a trace
#trace = go.Scatter(
#    x = random_x,
#    y = random_y
#)
#
#data = [trace]
#
#py.iplot(data, filename='basic-line')
#%%
#  def save_imgs(, epoch):
#        r, c = 5, 5
#        noise = np.random.normal(0, 1, (r * c, self.latent_dim))
#        gen_imgs = self.generator.predict(noise)
#
#        # Rescale images 0 - 1
#        gen_imgs = 0.5 * gen_imgs + 0.5
#
#        fig, axs = plt.subplots(r, c)
#        cnt = 0
#        for i in range(r):
#            for j in range(c):
#                axs[i,j].imshow(gen_imgs[cnt, :,:,0], cmap='gray')
#                axs[i,j].axis('off')
#                cnt += 1
#        fig.savefig("images/mnist_%d.png" % epoch)