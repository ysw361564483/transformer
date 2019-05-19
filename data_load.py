# -*- coding: utf-8 -*-
#/usr/bin/python3
'''
Feb. 2019 by kyubyong park.
kbpark.linguist@gmail.com.
https://www.github.com/kyubyong/transformer

Note.
if safe, entities on the source side have the prefix 1, and the target side 2, for convenience.
For example, fpath1, fpath2 means source file path and target file path, respectively.
'''
import tensorflow as tf
from utils import calc_num_batches
import pickle
import os

def load_vocab(vocab_fpath):
    '''Loads vocabulary file and returns idx<->token maps
    vocab_fpath: string. vocabulary file path.
    Note that these are reserved
    0: <pad>, 1: <unk>, 2: <s>, 3: </s>

    Returns
    two dictionaries.
    '''
    # vocab = [line.split() for line in open(vocab_fpath, 'r').read().splitlines()]
    # token2idx = {token: idx for token, idx in vocab}
    # idx2token = {idx: token for token, idx in vocab}
    dict_name = str(vocab_fpath).split('/')[-1].split('.')[0]+'.pkl'
    print('Building ' +dict_name+ ' vocab')
    if os.path.exists(dict_name):
        with open(dict_name, 'rb') as f:
            token2idx = pickle.load(f)
            idx2token = pickle.load(f)
        print('loading pkl vocab size =', len(idx2token), len(token2idx))
        return token2idx, idx2token

    vocab = [line.split()[0] for line in open(vocab_fpath, 'r').read().splitlines()]
    for i in ['</s>', '<s>', '<unk>', '<pad>']:
        vocab.insert(0, i)
    vocab = vocab[:10000]
    token2idx = {token: idx for idx, token in enumerate(vocab)}
    idx2token = {idx: token for idx, token in enumerate(vocab)}
    # token2idx.update({'<s>':len(token2idx)})
    # token2idx.update({'</s>':len(token2idx)})
    # token2idx.update({'<pad>':len(token2idx)})
    # token2idx.update({'<unk>':len(token2idx)})
    # idx2token.update({len(idx2token): '<s>'})
    # idx2token.update({len(idx2token): '<s>'})
    # idx2token.update({len(idx2token): '<pad>'})
    # idx2token.update({len(idx2token): '<unk>'})
    print('vocab size =', len(idx2token), len(token2idx))
    with open(dict_name, 'wb') as f:
        pickle.dump(token2idx, f, True)
        pickle.dump(idx2token, f, True)
    with open('dict_'+str(vocab_fpath).split('/')[-1], 'w') as f:
        for item in token2idx.items():
            f.write(str(item))
            f.write('\n')
    return token2idx, idx2token

def load_data(fpath1, fpath2, maxlen1, maxlen2):
    '''Loads source and target data and filters out too lengthy samples.
    fpath1: source file path. string.
    fpath2: target file path. string.
    maxlen1: source sent maximum length. scalar.
    maxlen2: target sent maximum length. scalar.

    Returns
    sents1: list of source sents
    sents2: list of target sents
    '''
    sents1, sents2 = [], []
    with open(fpath1, 'r') as f1, open(fpath2, 'r') as f2:
        for sent1, sent2 in zip(f1, f2):
            if len(sent1.split()) + 1 > maxlen1: continue # 1: </s>
            if len(sent2.split()) + 1 > maxlen2: continue  # 1: </s>
            sents1.append(sent1.strip())
            sents2.append(sent2.strip())
    return sents1, sents2


def encode(inp, type, dict):
    '''Converts string to number. Used for `generator_fn`.
    inp: 1d byte array.
    type: "x" (source side) or "y" (target side)
    dict: token2idx dictionary

    Returns
    list of numbers
    '''
    inp_str = inp.decode("utf-8")
    if type=="x": tokens = inp_str.split() + ["</s>"]
    else: tokens = ["<s>"] + inp_str.split() + ["</s>"]

    x = [dict.get(t, dict.get('<unk>')) for t in tokens]
    # print('len(x) =', len(x))
    return x

def generator_fn(sents1, sents2, vocab_fpath, vocab_fpath1):
    '''Generates training / evaluation data
    sents1: list of source sents
    sents2: list of target sents
    vocab_fpath: string. vocabulary file path.

    yields
    xs: tuple of
        x: list of source token ids in a sent
        x_seqlen: int. sequence length of x
        sent1: str. raw source (=input) sentence
    labels: tuple of
        decoder_input: decoder_input: list of encoded decoder inputs
        y: list of target token ids in a sent
        y_seqlen: int. sequence length of y
        sent2: str. target sentence
    '''
    q_token2idx, _ = load_vocab(vocab_fpath)
    a_token2idx, _ = load_vocab(vocab_fpath1)
    for sent1, sent2 in zip(sents1, sents2):
        x = encode(sent1, "x", q_token2idx)
        y = encode(sent2, "y", a_token2idx)
        
        decoder_input, y = y[:-1], y[1:]

        x_seqlen, y_seqlen = len(x), len(y)
        yield (x, x_seqlen, sent1), (decoder_input, y, y_seqlen, sent2)

def input_fn(sents1, sents2, vocab_fpath, vocab_fpath1, batch_size, shuffle=False):
    '''Batchify data
    sents1: list of source sents
    sents2: list of target sents
    vocab_fpath: string. vocabulary file path.
    batch_size: scalar
    shuffle: boolean

    Returns
    xs: tuple of
        x: int32 tensor. (N, T1)
        x_seqlens: int32 tensor. (N,)
        sents1: str tensor. (N,)
    ys: tuple of
        decoder_input: int32 tensor. (N, T2)
        y: int32 tensor. (N, T2)
        y_seqlen: int32 tensor. (N, )
        sents2: str tensor. (N,)
    '''
    shapes = (([None], (), ()),
              ([None], [None], (), ()))
    types = ((tf.int32, tf.int32, tf.string),
             (tf.int32, tf.int32, tf.int32, tf.string))
    paddings = ((0, 0, ''),
                (0, 0, 0, ''))

    dataset = tf.data.Dataset.from_generator(
        generator_fn,
        output_shapes=shapes,
        output_types=types,
        args=(sents1, sents2, vocab_fpath, vocab_fpath1))  # <- arguments for generator_fn. converted to np string arrays

    if shuffle: # for training
        dataset = dataset.shuffle(128*batch_size)

    dataset = dataset.repeat()  # iterate forever
    dataset = dataset.padded_batch(batch_size, shapes, paddings).prefetch(1)
    # If the dimension is unknown (e.g. tf.Dimension(None)), the component will be padded out to the maximum length of all elements in that dimension.
    return dataset

def get_batch(fpath1, fpath2, maxlen1, maxlen2, vocab_fpath, vocab_fpath1, batch_size, shuffle=False):
    '''Gets training / evaluation mini-batches
    fpath1: source file path. string.
    fpath2: target file path. string.
    maxlen1: source sent maximum length. scalar.
    maxlen2: target sent maximum length. scalar.
    vocab_fpath: string. vocabulary file path.
    batch_size: scalar
    shuffle: boolean

    Returns
    batches
    num_batches: number of mini-batches
    num_samples
    '''
    sents1, sents2 = load_data(fpath1, fpath2, maxlen1, maxlen2)
    batches = input_fn(sents1, sents2, vocab_fpath, vocab_fpath1, batch_size, shuffle=shuffle)
    num_batches = calc_num_batches(len(sents1), batch_size)
    return batches, num_batches, len(sents1)
