#!/usr/bin/env python3.8

# stdlib
import re
import sys
import os
import pathlib
import argparse
from time import sleep
import json
from typing import List, Dict, Any, Tuple
from pprint import pprint as pp

# 3rd party
import aiohttp
import discord
from redbot.core import commands, bot, checks, data_manager
from tqdm import tqdm

# training libs, not important for anything but devwork
try:
    import sklearn as sk
    from sklearn import model_selection
    import numpy as np
    import keras
    from keras.models import Sequential
    from keras.layers import LSTM, Dense, Dropout, Embedding
    from keras.callbacks import EarlyStopping, ModelCheckpoint
except ImportError as e:
    print(e)
    print("Warning! You wont be able to train the model")
    pass

# webserver
import flask

# local
try:
    from .eris_event_lib import ErisEventMixin
except ImportError:
    print("Warning, need mixin for cog")

    class ErisEventMixin:
        pass

    pass


BaseCog = getattr(commands, "Cog", object)


ALLPAPI = 160611518264639488


def main():
    args = get_args()
    if args.train:
        messages = load_from_json(args.data)
        processed, word_index = preprocess(messages)
        (
            feature_train,
            feature_test,
            label_train,
            label_test,
        ) = generate_features_and_labels(processed, word_index)

        build_model(
            feature_train,
            feature_test,
            label_train,
            label_test,
            word_index,
            args.embedding_file,
        )
    elif args.deploy:
        pass
    else:

        raise NotImplemented("Model not trained")


########################################################################################################################
# MODEL                                                                                                                #
########################################################################################################################


def load_from_json(datafile: pathlib.Path) -> List[Dict[str, Any]]:
    messages = json.loads(datafile.read_text())  # pulled from .reap below

    # just use the first 10k for dev
    messages = [m for m in messages if m["author"] == ALLPAPI]
    messages = messages[:1000]

    # remove emoji
    custom_emoji = "<a?:\w+:[0-9]+>"
    messages = [
        {
            "id": m["id"],
            "author": m["author"],
            "content": re.subn(custom_emoji, "", m["content"])[0].strip(),
        }
        for m in messages
    ]

    new_messages = []
    previous_author = None
    current_message = {}
    message_ids = []
    for m in tqdm(messages[::-1]):  # since reap saves them in reverse-chronological
        if m["id"] in message_ids:
            continue
        message_ids.append(m["id"])
        if re.match("^[\n ]*$", m["content"]):
            continue
        if m["content"].startswith("http"):
            continue
        if m["author"] == previous_author:
            current_message["content"] += f"\n{m['content']}"
        else:
            if current_message:
                new_messages.append(current_message)
            current_message = m
            previous_author = m["author"]
    new_messages.append(current_message)
    return new_messages


def preprocess(text: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict]:
    # https://keras.io/api/preprocessing/text/
    tokenizer = keras.preprocessing.text.Tokenizer(
        num_words=None,  # keep all words
        filters='"#$%&()*+-<=>@[\\]^_`{|}~\t\n',  # edited from docs to include what we care about and exclude nums
        lower=False,  # don't convert to lowercase
        split=" ",  # default
    )
    just_content = [t["content"] for t in text]
    tokenizer.fit_on_texts(just_content)
    sequences = tokenizer.texts_to_sequences(just_content)

    word_index = tokenizer.word_index

    for i, seq in enumerate(sequences):
        text[i]["sequence"] = seq

    return text, word_index


def generate_features_and_labels(text: List[Dict[str, Any]], word_index: Dict):
    features = []
    labels = []

    training_length = 10
    for message in text:
        sequence = message["sequence"]
        if len(sequence) < training_length:
            continue

        for i in range(training_length, len(sequence)):
            extract = sequence[i - training_length : i + 1]

            features.append(extract[:-1])  # train on first 4
            labels.append(extract[-1])  # label is last

    features = np.array(features)

    # one-hot encode (switch to binary representation) for words
    num_words = len(word_index) + 1
    label_array = np.zeros((len(features), num_words), dtype=np.int8)
    for i, label in enumerate(labels):
        label_array[i, label] = 1

    print(f"Feature Dimensions: {features.shape}")
    print(f"Label Dimensions: {label_array.shape}")

    (
        feature_train,
        feature_test,
        label_train,
        label_test,
    ) = model_selection.train_test_split(
        features, label_array, test_size=0.25, shuffle=True
    )

    return feature_train, feature_test, label_train, label_test


def build_model(
    feature_train, feature_test, label_train, label_test, word_index, embedding
):
    # load embedding
    glove = np.loadtxt(embedding, dtype=str, comments=None, delimiter=" ")
    vectors = glove[:, 1:].astype(float)
    words = glove[:, 0]
    word_lookup = {word: vector for word, vector in zip(words, vectors)}
    dim = vectors.shape[1]
    embedding = np.zeros((len(word_index) + 1, dim))
    for i, word in enumerate(word_index.keys()):
        vector = word_lookup.get(word, None)
        if vector is not None:
            embedding[i + 1, :] = vector

    print(f"Embedding Dimension: {embedding.shape}")

    # set up model
    model = Sequential()  # Build model one layer at a time
    model.add(
        Embedding(  # maps each input word to 100-dim vector
            input_dim=len(word_index) + 1,  # how many words can input
            input_length=len(feature_train),  # how many trainings
            output_dim=dim,  # output vector
            weights=[embedding],  # pre-trained weights
            trainable=True,  #   update embeddings
            mask_zero=True,
        )
    )
    model.add(LSTM(64, return_sequences=False, dropout=0.1, recurrent_dropout=0.1))
    model.add(Dense(64, activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(len(word_index) + 1, activation="softmax"))
    model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )
    print(model.summary())

    # train
    callbacks = [
        EarlyStopping(monitor="val_loss", patience=5),
        ModelCheckpoint(
            "../../models/model.h5", save_best_only=True, save_weights_only=False
        ),
    ]

    history = model.fit(
        [feature_train],
        label_train,
        batch_size=1024,
        epochs=5,
        callbacks=callbacks,
        validation_data=([feature_test], label_test),
    )


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data", type=str, default=None, help="Where to find input data"
    )
    parser.add_argument(
        "--embedding-file",
        type=str,
        default=None,
        help="Where to find pre-trained embeddings",
    )
    parser.add_argument(
        "--train", action="store_true", default=False, help="Train Model"
    )
    parser.add_argument(
        "--deploy", action="store_true", default=False, help="Deploy to ec2"
    )
    args = parser.parse_args()
    if args.data is None:
        raise FileNotFoundError("Please provide a data file!")
    args.data = pathlib.Path(args.data)
    args.embedding_file = pathlib.Path(args.embedding_file)
    return args


########################################################################################################################
# COG                                                                                                                  #
########################################################################################################################


class Cylon(BaseCog, ErisEventMixin):
    def __init__(self, bot_instance: bot):
        super().__init__()
        self.bot: bot = bot_instance
        self.data_dir = data_manager.bundled_data_path(self)

        self.bot.add_listener(self.watch_message_history, "on_message")

    @commands.command()
    @checks.is_owner()
    async def reap(self, ctx):
        channel: discord.TextChannel = ctx.channel
        server: discord.Guild = ctx.guild

        message_list = []

        # let's start with just the latest 500
        message: discord.Message
        last_message_examined: discord.Message = None
        message_count = 0
        while True:
            chunk = await channel.history(
                limit=500, before=last_message_examined
            ).flatten()
            if len(chunk) == 0:
                break
            message_count += len(chunk)
            for message in chunk:
                if message.clean_content.startswith("."):
                    continue
                if message.author.bot:
                    continue
                message_list.append(
                    {
                        "id": message.id,
                        "author": message.author.id,
                        "content": message.clean_content,
                    }
                )

            last_message_examined = message

        filename = f"{server.name}-{channel.name}.json"
        output_file = self.data_dir / filename
        output_file.write_text(json.dumps(message_list))

        await ctx.send(f"Done. Processed {message_count} messages.")

    async def watch_message_history(self, message: discord.Message):
        pass

    @commands.command()
    async def cylon(self, ctx):
        return
        async with ctx.typing():
            sleep(1)
            url = "foobar"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    insult = await resp.text()


########################################################################################################################
# WEB SERVER                                                                                                           #
########################################################################################################################


if __name__ == "__main__":
    sys.exit(main())
