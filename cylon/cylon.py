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
import gc
import random
import pickle

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
    from keras.models import Sequential, load_model
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
TIMESTEP = 5


def main():
    args = get_args()
    messages = load_from_json(args.data)
    processed, word_index, index_word = preprocess(messages)
    # for message in processed:
    #     print(message['content'])
    #     print(' '.join(index_word[c] for c in message['sequence']))
    #     print('~~~')
    if args.train:
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

    model_dir = pathlib.Path('../../models')
    model = (model_dir / 'model.h5')
    if not model.exists():
        raise FileNotFoundError

    response = []
    model = load_model(model)
    start = random.choice(processed)
    pp(start)
    start = np.array([start['sequence'][-TIMESTEP:]])

    for i in range(20):
        preds = model.predict(start)[0]
        preds = preds / sum(preds)    # normalize
        probas = np.random.multinomial(1, preds, 1)[0]

        next_idx = np.argmax(probas)
        response.append(next_idx)

        start = np.array([
            [*start[0], next_idx][-TIMESTEP:]
        ])

    print(' '.join(index_word[s] for s in response))


########################################################################################################################
# MODEL                                                                                                                #
########################################################################################################################


def load_from_json(datafile: pathlib.Path) -> List[Dict[str, Any]]:
    messages = json.loads(datafile.read_text())  # pulled from .reap below

    # messages = messages[:100000]

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
    for m in tqdm(messages[::-1]):  # since reap saves them in reverse-chronological
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

    new_messages = [m for m in new_messages if m['author'] == ALLPAPI]

    return new_messages


def preprocess(text: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict, Dict]:
    just_content = [t["content"].lower() for t in text]

    chars_to_remove = '"#$%&()*+-<=>@[\\]^_`{|}~/'

    index = 1
    word_index = {}
    sequences = []
    for message in just_content:
        message = ''.join(c for c in message if c not in chars_to_remove)
        message = re.subn(r',', ' , ', message)[0]
        message = re.subn(r'\.', ' . ', message)[0]
        message = re.subn(r'\?', ' ? ', message)[0]
        message = re.subn(r'\!', ' ! ', message)[0]
        words = [w for w in re.split(r'\s', message) if w != '']
        for word in words:
            if word not in word_index:
                word_index[word] = index
                index += 1
        sequences.append([word_index[word] for word in words])

    index_word = {v: k for k, v in word_index.items()}

    for i, seq in enumerate(sequences):
        text[i]["sequence"] = seq
        text[i]["tokenized"] = ' '.join(index_word[s] for s in seq)

    return text, word_index, index_word


def generate_features_and_labels(text: List[Dict[str, Any]], word_index: Dict):
    features = []
    labels = []

    training_length = TIMESTEP
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
    feature_train, feature_test, label_train, label_test, word_index, embedding, use_twitter=False
):
    num_words = len(word_index) + 1

    dim = 100
    if use_twitter:
        # load embedding
        glove = np.loadtxt(embedding, dtype=str, comments=None, delimiter=" ")
        vectors = glove[:, 1:].astype(float)
        words = glove[:, 0]
        word_lookup = {word: vector for word, vector in zip(words, vectors)}
        dim = vectors.shape[1]
        embedding = np.zeros((num_words, dim))
        for i, word in enumerate(word_index.keys()):
            vector = word_lookup.get(word, None)
            if vector is not None:
                embedding[i + 1, :] = vector

        gc.enable()
        del glove, vectors, words
        gc.collect()
        print(f"Embedding Dimension: {embedding.shape}")

    # set up model
    model = Sequential()  # Build model one layer at a time
    weights = None
    if use_twitter:
        weights = [embedding]
    model.add(
        Embedding(  # maps each input word to 100-dim vector
            input_dim=num_words,  # how many words can input
            input_length=TIMESTEP,  # timestep length
            output_dim=dim,  # output vector
            weights=weights,
            trainable=True,  # update embeddings
        )
    )
    model.add(LSTM(64, return_sequences=True, dropout=0.1, recurrent_dropout=0.1))
    model.add(LSTM(64, return_sequences=True, dropout=0.1, recurrent_dropout=0.1))
    model.add(LSTM(64, return_sequences=False, dropout=0.1, recurrent_dropout=0.1))
    model.add(Dense(64, activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(num_words, activation="softmax"))
    model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )
    model.summary()

    # train
    callbacks = [
        EarlyStopping(monitor="val_loss", patience=5),
        ModelCheckpoint(
            "../../models/model.h5", save_best_only=True, save_weights_only=False
        ),
    ]

    history = model.fit(
        feature_train,
        label_train,
        batch_size=2048,
        epochs=50,
        callbacks=callbacks,
        validation_data=(feature_test, label_test),
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
    if args.embedding_file is not None:
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
