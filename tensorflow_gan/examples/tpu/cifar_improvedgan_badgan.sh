
export EXPERIMENT_NAME=cifar_improved_badgan1
export BATCH_SIZE=128
export TRAIN_STEPS_PER_EVAL=10000
export DATASET_ARGS='--image_size=32 --dataset_name=cifar10 --num_classes=10 --dataset_val_split_name=test'


export ADDITIONAL='--critic_type=kplusone_fm_badgan \
--generator_loss_fn=kplusone_featurematching_generator_loss \
--kplusone_nll_discriminator_weight=1.0 \
--tpu_gan_estimator_d_step=1 \
--discriminator_lr=0.0006 \
--generator_lr=0.0003 \
--extra_eval_metrics \
--eval_batch_size=1024 \
--num_eval_steps=9 \
--df_dim=96'

bash tpu/_base.sh