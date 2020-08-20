export EXPERIMENT_NAME='cifar_complementgan2'
export OUTPUT_DIR=/scratch1/ilya/locDoc/experiments/tfgan/${EXPERIMENT_NAME}
export DATA_DIR=/scratch1/ilya/locDoc/data/tfdf

export BATCH_SIZE=64
export DATASET_ARGS='--image_size=32 --dataset_name=cifar10 --num_classes=10 --dataset_val_split_name=test'

# Complement GAN
# d loss is nll
# g loss is csc and confuse
export ADDITIONAL='--critic_type=kplusone_fm \
--generator_loss_fn=kplusonegan_csc_generator_loss \
--kplusonegan_confuse_generator_weight=1.0 \
--kplusone_nll_discriminator_weight=1.0'



bash gpu/_base.sh