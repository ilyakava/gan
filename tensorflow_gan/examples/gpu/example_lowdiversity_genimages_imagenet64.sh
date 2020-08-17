# For this experiment compare steps 999999 and 1014999.
# The model was trained like a normal SAGAN until 1M steps.
# Then the model was trained according to the high fidelity low diversity
# method described in the paper.

export EXPERIMENT_NAME=imagenet64_baseline_ctd
export OUTPUT_DIR=/scratch0/ilya/locDoc/tfgan/examples/${EXPERIMENT_NAME}
export DATA_DIR=/scratch1/ilya/locDoc/data/tfdf

export BATCH_SIZE=64
export DATASET_ARGS='--image_size=64 --dataset_name=imagenet_resized/64x64 --num_classes=1000 --dataset_val_split_name=validation'

export ADDITIONAL='--critic_type=acgan \
--mode=gen_images \
--n_images_per_side_to_gen_per_tile=8'

bash gpu/_eval_base.sh
