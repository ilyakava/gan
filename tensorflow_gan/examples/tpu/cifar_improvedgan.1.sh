
export EXPERIMENT_NAME=cifar_improved_4step_2eqlr
export BATCH_SIZE=64
export TRAIN_STEPS_PER_EVAL=10000
export DATASET_ARGS='--image_size=32 --dataset_name=cifar10 --num_classes=10 --dataset_val_split_name=test'


export ADDITIONAL='--critic_type=kplusone_fm \
--generator_loss_fn=kplusone_featurematching_generator_loss \
--kplusone_nll_discriminator_weight=1.0 \
--tpu_gan_estimator_d_step=4 \
--discriminator_lr=0.0002 \
--generator_lr=0.0002 \
--extra_eval_metrics \
--eval_batch_size=1024 \
--num_eval_steps=9'

bash tpu/_base.sh