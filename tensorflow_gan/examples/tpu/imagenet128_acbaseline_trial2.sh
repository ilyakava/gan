
export EXPERIMENT_NAME=imagenet128_acbaseline_trial3
export BATCH_SIZE=1024
export TRAIN_STEPS_PER_EVAL=5000
export DATASET_ARGS='--image_size=128 --dataset_name=imagenet2012 --num_classes=1000 --dataset_val_split_name=validation'

export ADDITIONAL='--critic_type=acgan \
--aux_cond_generator_weight=0.1 \
--aux_cond_discriminator_weight=1.0 \
--extra_eval_metrics=true \
--tpu_gan_estimator_d_step=2 \
--keep_checkpoint_max=20'

bash tpu/_base.sh