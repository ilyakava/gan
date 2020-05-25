
export EXPERIMENT_NAME=imagenet128_expt_1ctd
export BATCH_SIZE=1024
export TRAIN_STEPS_PER_EVAL=5000
export DATASET_ARGS='--image_size=128 --dataset_name=imagenet2012 --num_classes=1000 --dataset_val_split_name=validation'

export ADDITIONAL='--critic_type=acgan \
--aux_mhinge_cond_generator_weight=0.05 \
--aux_mhinge_cond_discriminator_weight=1.0'

bash tpu/_base.sh