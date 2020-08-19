
export EXPERIMENT_NAME=cifar_marygan
export BATCH_SIZE=1024
export TRAIN_STEPS_PER_EVAL=10000
export DATASET_ARGS='--image_size=32 --dataset_name=cifar10 --num_classes=10 --dataset_val_split_name=test'

export ADDITIONAL='--critic_type=kplusone_fm \
--num_eval_steps=9 \
--mode=continuous_eval \
--extra_eval_metrics'

bash tpu/_eval_base.sh

