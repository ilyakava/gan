
export EXPERIMENT_NAME=late_cifar_base
export BATCH_SIZE=64
export TRAIN_STEPS_PER_EVAL=10000
export DATASET_ARGS='--image_size=32 --dataset_name=cifar10 --num_classes=10 --dataset_val_split_name=test'

# for k+1 mhinge with fm
export ADDITIONAL='--critic_type=kplusone_fm \
--generator_loss_fn=kplusone_featurematching_generator_loss \
--kplusone_mhinge_cond_discriminator_weight=1.0 \
--aux_mhinge_cond_generator_weight=0.05 \
--tpu_gan_estimator_d_step=4 \
--extra_eval_metrics'


bash tpu/_base.sh