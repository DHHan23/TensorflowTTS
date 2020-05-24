# -*- coding: utf-8 -*-

# Copyright 2020 Minh Nguyen (@dathudeptrai)
#  MIT License (https://opensource.org/licenses/MIT)

"""Dataset modules."""

import logging
import os
import numpy as np

import tensorflow as tf

from tensorflow_tts.utils import find_files

from tensorflow_tts.datasets.abstract_dataset import AbstractDataset


class MelDataset(AbstractDataset):
    """Tensorflow compatible mel dataset."""

    def __init__(self,
                 root_dir,
                 mel_query="*-raw-feats.h5",
                 mel_load_fn=np.load,
                 mel_length_threshold=None,
                 return_utt_id=False
                 ):
        """Initialize dataset.

        Args:
            root_dir (str): Root directory including dumped files.
            mel_query (str): Query to find feature files in root_dir.
            mel_load_fn (func): Function to load feature file.
            mel_length_threshold (int): Threshold to remove short feature files.
            return_utt_id (bool): Whether to return the utterance id with arrays.

        """
        # find all of mel files.
        mel_files = sorted(find_files(root_dir, mel_query))
        mel_lengths = [mel_load_fn(f).shape[0] for f in mel_files]

        # filter by threshold
        if mel_length_threshold is not None:
            idxs = [idx for idx in range(len(mel_files)) if mel_lengths[idx] > mel_length_threshold]
            if len(mel_files) != len(idxs):
                logging.warning(f"Some files are filtered by mel length threshold "
                                f"({len(mel_files)} -> {len(idxs)}).")
            mel_files = [mel_files[idx] for idx in idxs]

        # assert the number of files
        assert len(mel_files) != 0, f"Not found any mel files in ${root_dir}."

        if ".npy" in mel_query:
            utt_ids = ["-".join([os.path.basename(f).split("-")[0], os.path.basename(f).split("-")[1]])
                       for f in mel_files]

        # set global params
        self.utt_ids = utt_ids
        self.mel_files = mel_files
        self.mel_lengths = mel_lengths
        self.mel_load_fn = mel_load_fn
        self.return_utt_id = return_utt_id

    def get_args(self):
        return [self.utt_ids]

    def generator(self, utt_ids):
        for i, utt_id in enumerate(utt_ids):
            mel_file = self.mel_files[i]
            mel = self.mel_load_fn(mel_file)
            mel_length = self.mel_lengths[i]
            if self.return_utt_id:
                items = utt_id, mel, mel_length
            else:
                items = mel, mel_length
            yield items

    def get_output_dtypes(self):
        output_types = (tf.float32, tf.int32)
        if self.return_utt_id:
            output_types = (tf.dtypes.string, *output_types)
        return output_types

    def create(self,
               allow_cache=False,
               batch_size=1,
               is_shuffle=False,
               map_fn=None,
               reshuffle_each_iteration=True
               ):
        """Create tf.dataset function."""
        output_types = self.get_output_dtypes()
        datasets = tf.data.Dataset.from_generator(
            self.generator,
            output_types=output_types,
            args=(self.get_args())
        )

        if allow_cache:
            datasets = datasets.cache()

        if is_shuffle:
            datasets = datasets.shuffle(
                self.get_len_dataset(), reshuffle_each_iteration=reshuffle_each_iteration)

        # define padded_shapes.
        padded_shapes = ([None, None], [])
        if self.return_utt_id:
            padded_shapes = ([], *padded_shapes)

        datasets = datasets.padded_batch(batch_size, padded_shapes=padded_shapes)
        datasets = datasets.prefetch(tf.data.experimental.AUTOTUNE)
        return datasets

    def get_len_dataset(self):
        return len(self.utt_ids)

    def __name__(self):
        return "MelDataset"