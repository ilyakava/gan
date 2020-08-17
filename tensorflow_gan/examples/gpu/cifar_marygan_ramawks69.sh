export EXPERIMENT_NAME='cifar_marygan'
export OUTPUT_DIR=/scratch1/ilya/locDoc/experiments/tfgan/${EXPERIMENT_NAME}
export DATA_DIR=/scratch1/ilya/locDoc/data/tfdf

export BATCH_SIZE=64
export DATASET_ARGS='--image_size=32 --dataset_name=cifar10 --num_classes=10 --dataset_val_split_name=test'

# Improved GAN
# d loss is nll
# g loss is positive log likelihood
export ADDITIONAL='--critic_type=kplusone_fm \
--generator_loss_fn=kplusonegan_pll_generator_loss \
--kplusone_nll_discriminator_weight=1.0'



bash gpu/_base.sh