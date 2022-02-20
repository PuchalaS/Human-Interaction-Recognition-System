# encoding: utf-8

import argparse
import os
import sys
from os import mkdir

import wandb
from keras.utils.vis_utils import plot_model

sys.path.append(".")
from config import cfg
from data.dataset import Dataset
from engine.trainer import do_train
from engine.test import do_test
from engine.summarize import summarize
from modeling import SingleLSTM, DoubleLSTM,TripleLSTM, ConvNet, CNN3D
from utils.logger import setup_logger
from utils.wandblog import setup_wandb_logger


def train(cfg):

    run = setup_wandb_logger(cfg)
    dataset = Dataset(cfg)
    data = dataset.create_test_train_sets()
    if cfg.MODEL.ARCH == "single":
        X_train_seq, y_train_seq, X_test_seq, y_test_seq = data
        model = SingleLSTM().build_model(
            X_train_seq.shape[1], X_train_seq.shape[2], y_train_seq.shape[1], cfg
        )
    elif cfg.MODEL.ARCH == "double":
        (
            X_train_seq_per1,
            X_train_seq_per2,
            y_train_seq,
            X_test_seq_per1,
            X_test_seq_per2,
            y_test_seq,
        ) = data
        model = DoubleLSTM.build_model(
            X_train_seq_per1.shape[1],
            X_train_seq_per2.shape[2],
            y_train_seq.shape[1],
            cfg,
        )
    elif cfg.MODEL.ARCH == "triple":
        (
            X_train_seq_per1,
            X_train_seq_per2,
            X_train_dist_seq,
            X_test_seq_per1,
            X_test_seq_per2,
            X_test_dist_seq,
            y_train_seq,
            y_test_seq,
        ) = data
        model = TripleLSTM.build_model(
            X_train_seq_per1.shape[1],
            X_train_seq_per2.shape[2],
            y_train_seq.shape[1],
            X_train_dist_seq.shape[2],
            cfg,
        )
    elif cfg.MODEL.ARCH == "convnet":
        model = ConvNet.build_model(
            (24, 24, wandb.config.number_of_frames, 1),
            11,
            cfg,
        )
    elif cfg.MODEL.ARCH == "CNN3D":
        model = CNN3D.build_model(
            (24, 24, wandb.config.number_of_frames, 1),
            11,
            cfg,
        )
   
    model = do_train(
        cfg,
        model,
        data,
    )
    print(model.summary())
    plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)

    score = do_test(cfg, model, data)
    summarize(
        cfg,
        model,
        data,
    )


def main():
    parser = argparse.ArgumentParser(description="Keras training")
    parser.add_argument(
        "--config_file", default="", help="path to config file", type=str
    )
    parser.add_argument(
        "opts",
        help="Modify config options using the command-line",
        default=None,
        nargs=argparse.REMAINDER,
    )

    args = parser.parse_args()

    num_gpus = int(os.environ["WORLD_SIZE"]) if "WORLD_SIZE" in os.environ else 1

    if args.config_file != "":
        cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)
    cfg.freeze()

    output_dir = cfg.OUTPUT_DIR
    if output_dir and not os.path.exists(output_dir):
        mkdir(output_dir)

    logger = setup_logger("model", output_dir, 0)
    logger.info("Using {} GPUS".format(num_gpus))
    logger.info(args)
    logger.propagate = False

    if args.config_file != "":
        logger.info("Loaded configuration file {}".format(args.config_file))
        with open(args.config_file, "r") as cf:
            config_str = "\n" + cf.read()
            logger.info(config_str)
    logger.info("Running with config:\n{}".format(cfg))

    train(cfg)


if __name__ == "__main__":
    main()
