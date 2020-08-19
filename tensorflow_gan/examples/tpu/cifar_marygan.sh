
export EXPERIMENT_NAME=cifar_mary_4step
export BATCH_SIZE=64
export TRAIN_STEPS_PER_EVAL=10000
export DATASET_ARGS='--image_size=32 --dataset_name=cifar10 --num_classes=10 --dataset_val_split_name=test'


export ADDITIONAL='--critic_type=kplusone_fm \
--generator_loss_fn=kplusonegan_pll_generator_loss \
--kplusone_nll_discriminator_weight=1.0 \
--tpu_gan_estimator_d_step=4 \
--extra_eval_metrics \
--eval_batch_size=1024 \
--num_eval_steps=9'

bash tpu/_base.sh