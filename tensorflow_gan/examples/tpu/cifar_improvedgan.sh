
export EXPERIMENT_NAME=cifar_improved_1step
export BATCH_SIZE=64
export TRAIN_STEPS_PER_EVAL=10000
export DATASET_ARGS='--image_size=32 --dataset_name=cifar10 --num_classes=10 --dataset_val_split_name=test'


export ADDITIONAL='--critic_type=kplusone_fm \
--generator_loss_fn=kplusone_featurematching_generator_loss \
--kplusone_nll_discriminator_weight=1.0'

bash tpu/_base.sh