
export EXPERIMENT_NAME=cifar_complement_4step_2eqlr
export BATCH_SIZE=64
export TRAIN_STEPS_PER_EVAL=10000
export DATASET_ARGS='--image_size=32 --dataset_name=cifar10 --num_classes=10 --dataset_val_split_name=test'


export ADDITIONAL='--critic_type=kplusone_fm \
--generator_loss_fn=kplusonegan_csc_generator_loss \
--kplusonegan_confuse_generator_weight=1.0 \
--kplusone_nll_discriminator_weight=1.0 \
--tpu_gan_estimator_d_step=4 \
--discriminator_lr=0.0002 \
--generator_lr=0.0002'

bash tpu/_base.sh