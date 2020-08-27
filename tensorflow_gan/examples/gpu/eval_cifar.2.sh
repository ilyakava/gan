
# export EXPERIMENT_NAME=cifar_complement_4step_conf0p5_lrelu_dropout
export EXPERIMENT_NAME=cifar_improved_4step_lrelu_dropout
export OUTPUT_DIR=/scratch1/ilya/locDoc/experiments/tfgan/${EXPERIMENT_NAME}
export DATA_DIR=/scratch1/ilya/locDoc/data/tfdf
export BATCH_SIZE=64
export TRAIN_STEPS_PER_EVAL=10000
export DATASET_ARGS='--image_size=32 --dataset_name=cifar10 --num_classes=10 --dataset_val_split_name=test'

# cifar10_corrupted/speckle_noise_5
# cifar10_corrupted/snow_5
# cifar10_corrupted/pixelate_4
# cifar10_corrupted/jpeg_compression_5
# cifar10_corrupted/frosted_glass_blur_1
# cifar10_corrupted/saturate_4
# cifar10_corrupted/frost_5
# cifar10_corrupted/fog_4


export ADDITIONAL='--critic_type=kplusone_fm_lrelu_dropout \
--generator_loss_fn=kplusonegan_csc_generator_loss \
--kplusonegan_confuse_generator_weight=0.5 \
--kplusone_nll_discriminator_weight=1.0 \
--tpu_gan_estimator_d_step=4 \
--extra_eval_metrics \
--eval_batch_size=256 \
--num_eval_steps=36 \
--df_dim=96 \
--mode=continuous_eval \
--continuous_eval_timeout_secs=1'

bash gpu/_eval_base.sh