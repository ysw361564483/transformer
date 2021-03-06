# -*- coding: utf-8 -*-
# /usr/bin/python3
'''
Feb. 2019 by kyubyong park.
kbpark.linguist@gmail.com.
https://www.github.com/kyubyong/transformer

Transformer network
'''
import tensorflow as tf

from data_load import load_vocab
from modules import get_token_embeddings, ff, positional_encoding, multihead_attention, label_smoothing, noam_scheme
from utils import convert_idx_to_token_tensor
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)

class Transformer:
    '''
    xs: tuple of
        x: int32 tensor. (N, T1)
        x_seqlens: int32 tensor. (N,)
        sents1: str tensor. (N,)
    ys: tuple of
        decoder_input: int32 tensor. (N, T2)
        y: int32 tensor. (N, T2)
        y_seqlen: int32 tensor. (N, )
        sents2: str tensor. (N,)
    training: boolean.
    '''
    def __init__(self, hp):
        self.hp = hp
        # 预测时词表用错! 应该用目标语言的词表而不是源语言的词表!!! 浪费了我四天的时间!!
        # 而且应该用dev的词表而不是train的！！ 其实用train也可以的吧 因为train基本包括了dev的 dev的词表小会报keyerror
        self.token2idx, self.idx2token = load_vocab(hp.vocab1)
        self.embeddings = get_token_embeddings(self.hp.vocab_size, self.hp.d_model, zero_pad=True)
        print('embeddings size =', self.hp.vocab_size)

    def encode(self, xs, training=True):
        '''
        Returns
        memory: encoder outputs. (N, T1, d_model)
        '''
        with tf.variable_scope("encoder", reuse=tf.AUTO_REUSE):
            x, seqlens, sents1 = xs
            # x = tf.Print(x, [x], message='x =', summarize=10)
            # print_sent = tf.Print(sents1, [sents1], message='sents1 =', summarize=3)
            # with tf.control_dependencies([print_sent]):
            # embedding
            # xs_pri = tf.print('xs =', tf.shape(x), summarize=3)
            enc = tf.nn.embedding_lookup(self.embeddings, x) # (N, T1, d_model)
            enc *= self.hp.d_model**0.5 # scale

            enc += positional_encoding(enc, self.hp.maxlen1)
            enc = tf.layers.dropout(enc, self.hp.dropout_rate, training=training)
            # enc_pri = tf.print('enc =', tf.shape(enc), enc, summarize=3)
            ## Blocks
            # with tf.control_dependencies([xs_pri, enc_pri]):

            for i in range(self.hp.num_blocks):
                with tf.variable_scope("num_blocks_{}".format(i), reuse=tf.AUTO_REUSE):
                    # self-attention
                    enc = multihead_attention(queries=enc,
                                              keys=enc,
                                              values=enc,
                                              num_heads=self.hp.num_heads,
                                              dropout_rate=self.hp.dropout_rate,
                                              training=training,
                                              causality=False)
                    # feed forward
                    enc = ff(enc, num_units=[self.hp.d_ff, self.hp.d_model])
        memory = enc
        return memory, sents1

    def decode(self, ys, memory, training=True):
        '''
        memory: encoder outputs. (N, T1, d_model)

        Returns
        logits: (N, T2, V). float32.
        y_hat: (N, T2). int32
        y: (N, T2). int32
        sents2: (N,). string.
        '''
        with tf.variable_scope("decoder", reuse=tf.AUTO_REUSE):
            decoder_inputs, y, seqlens, sents2 = ys
            # decoder_inputs = tf.Print(decoder_inputs, [decoder_inputs], 
                # message='decoder_inputs =', summarize=10)
            # embedding
            # ys_pri = tf.print('y =', tf.shape(y), summarize=3)
            dec = tf.nn.embedding_lookup(self.embeddings, decoder_inputs)  # (N, T2, d_model)
            dec *= self.hp.d_model ** 0.5  # scale

            dec += positional_encoding(dec, self.hp.maxlen2)
            dec = tf.layers.dropout(dec, self.hp.dropout_rate, training=training)
            # dec = tf.Print(dec, [dec], message='dec =', summarize=10)
            # dec_pri = tf.print('dec =', tf.shape(dec), dec, summarize=3)
            # Blocks
            for i in range(self.hp.num_blocks):
                with tf.variable_scope("num_blocks_{}".format(i), reuse=tf.AUTO_REUSE):
                    # Masked self-attention (Note that causality is True at this time)
                    dec = multihead_attention(queries=dec,
                                              keys=dec,
                                              values=dec,
                                              num_heads=self.hp.num_heads,
                                              dropout_rate=self.hp.dropout_rate,
                                              training=training,
                                              causality=True,
                                              scope="self_attention")

                    # Vanilla attention
                    dec = multihead_attention(queries=dec,
                                              keys=memory,
                                              values=memory,
                                              num_heads=self.hp.num_heads,
                                              dropout_rate=self.hp.dropout_rate,
                                              training=training,
                                              causality=False,
                                              scope="vanilla_attention")
                    ### Feed Forward
                    dec = ff(dec, num_units=[self.hp.d_ff, self.hp.d_model])

        # dec = tf.Print(dec, [dec], message='dec_finally =', summarize=10)
        # Final linear projection (embedding weights are shared)
        # with tf.control_dependencies([ys_pri, dec_pri]):
        weights = tf.transpose(self.embeddings) # (d_model, vocab_size)
        logits = tf.einsum('ntd,dk->ntk', dec, weights) # (N, T2, vocab_size)
        y_hat = tf.to_int32(tf.argmax(logits, axis=-1))

        return logits, y_hat, y, sents2

    def train(self, xs, ys):
        '''
        Returns
        loss: scalar.
        train_op: training operation
        global_step: scalar.
        summaries: training summary node
        '''
        # forward
        memory, sents1 = self.encode(xs)
        # memory = tf.Print(memory, [memory], message='memory =', summarize=10)
        logits, preds, y, sents2 = self.decode(ys, memory)
        # logits = tf.Print(logits, [logits], message='logits =', summarize=10)

        print('train logits.shape, y.shape =', logits.shape, y.shape)
        # train scheme
        y_ = label_smoothing(tf.one_hot(y, depth=self.hp.vocab_size))
        # logits = tf.Print(logits, [logits], message='logits =', summarize=10)
        # y_ = tf.Print(y_, [y_], message='y_ =', summarize=10)
        ce = tf.nn.softmax_cross_entropy_with_logits_v2(logits=logits, labels=y_)
        nonpadding = tf.to_float(tf.not_equal(y, self.token2idx["<pad>"]))  # 0: <pad>
        # nonpadding = tf.Print(nonpadding, [nonpadding], message='nonpadding =',
        #     summarize=100)
        # nonpadding_print = tf.print('nonpadding =', tf.shape(nonpadding) 
        #     , summarize=20)
        # with tf.control_dependencies([nonpadding_print]):
        loss = tf.reduce_sum(ce * nonpadding) / (tf.reduce_sum(nonpadding) + 1e-7)  
        # loss = tf.Print(loss, [loss], message='loss =', summarize=10)

        global_step = tf.train.get_or_create_global_step()
        lr = noam_scheme(self.hp.lr, global_step, self.hp.warmup_steps)
        optimizer = tf.train.AdamOptimizer(lr)
        # gradients = optimizer.compute_gradients(loss)
        # # print_grad = tf.print('gradients =', gradients, summarize=10)
        # # with tf.control_dependencies([print_grad]):
        # clip_grads = [(tf.clip_by_value(grad, -100., 100.), var) for grad, var in gradients]
        # train_op = optimizer.apply_gradients(clip_grads, global_step=global_step)
        train_op = optimizer.minimize(loss, global_step=global_step)
               
        tf.summary.scalar('lr', lr)
        tf.summary.scalar("loss", loss)
        tf.summary.scalar("global_step", global_step)

        summaries = tf.summary.merge_all()

        return loss, train_op, global_step, summaries

    def eval(self, xs, ys):
        '''Predicts autoregressively
        At inference, input ys is ignored.
        Returns
        y_hat: (N, T2)
        '''
        decoder_inputs, y, y_seqlen, sents2 = ys
        # decoder_inputs (N, 1)
        decoder_inputs = tf.ones((tf.shape(xs[0])[0], 1), tf.int32) * self.token2idx["<s>"]
        ys = (decoder_inputs, y, y_seqlen, sents2)

        memory, sents1 = self.encode(xs, False)

        logging.info("Inference graph is being built. Please be patient.")
        for _ in tqdm(range(self.hp.maxlen2)):
            logits, y_hat, y, sents2 = self.decode(ys, memory, False)
            # if tf.reduce_sum(y_hat, 1) == self.token2idx["<pad>"] or \
            #     tf.reduce_sum(y_hat, 1) == self.token2idx["<s>"]: break
            # # # print('y_hat.shape = ', y_hat.shape)

            _decoder_inputs = tf.concat((decoder_inputs, y_hat), 1)

            # print('_decoder_inputs.shape =', _decoder_inputs.shape)
            _decoder_inputs = tf.cond(
                tf.cast(tf.reduce_sum(y_hat, 1) == self.token2idx["<pad>"], tf.bool),
                lambda: _decoder_inputs , 
                lambda: tf.concat((decoder_inputs, y_hat), 1))
            ys = (_decoder_inputs, y, y_seqlen, sents2)
            # print('ys =', ys)
        # loss
        # logits, y_hat, y, sents2 = self.decode(ys, memory, False)
        # _decoder_inputs = tf.concat((decoder_inputs, y_hat), 1)

        # def cond(_decoder_inputs, y, y_seqlen, sents2, memory, y_hat, logits):
        #     return tf.reduce_sum(y_hat, 1) == self.token2idx["<pad>"] or \
        #     tf.reduce_sum(y_hat, 1) == self.token2idx["<s>"]
        # def body(_decoder_inputs, y, y_seqlen, sents2, memory, y_hat, logits):
        #     _decoder_inputs = tf.concat((decoder_inputs, y_hat), 1)
        #     ys = (_decoder_inputs, y, y_seqlen, sents2)
        #     logits, y_hat, y, sents2 = self.decode(ys, memory, False)
        #     return _decoder_inputs, y, y_seqlen, sents2, memory, y_hat, logits

        # _decoder_inputs, y, y_seqlen, sents2, memory, y_hat, logits = \
        #     tf.while_loop(cond, body,
        #     [_decoder_inputs, y, y_seqlen, sents2, memory, y_hat, logits],
        #     shape_invariants=[
        #     tf.TensorShape([None, None]), y.get_shape(), y_seqlen.get_shape(),
        #     sents2.get_shape(), memory.get_shape(), tf.TensorShape([None, None]),
        #     tf.TensorShape([None, None, self.hp.vocab_size])
        #     ])
        
        shape_pri = tf.print('eval logits.shape, y.shape =', 
            tf.shape(logits), tf.shape(y))
        # with tf.control_dependencies([shape_pri]):
        y_ = label_smoothing(tf.one_hot(y, depth=self.hp.vocab_size))
        # logits = tf.Print(logits, [logits], message='logits =', summarize=10)
        # y_ = tf.Print(y_, [y_], message='y_ =', summarize=10)
        ce = tf.nn.softmax_cross_entropy_with_logits_v2(
            logits=logits[:,:tf.shape(y_)[1],:], labels=y_)
        nonpadding = tf.to_float(tf.not_equal(y, self.token2idx["<pad>"]))  # 0: <pad>
        loss = tf.reduce_sum(ce * nonpadding) / (tf.reduce_sum(nonpadding) + 1e-7)

        # monitor a random sample
        n = tf.random_uniform((), 0, tf.shape(y_hat)[0]-1, tf.int32)
        sent1 = sents1[n]
        pred = convert_idx_to_token_tensor(y_hat[n], self.idx2token)
        sent2 = sents2[n]

        tf.summary.text("sent1", sent1)
        tf.summary.text("pred", pred)
        tf.summary.text("sent2", sent2)
        summaries = tf.summary.merge_all()

        return y_hat, summaries, loss

