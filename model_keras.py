import os
import pickle
from keras.preprocessing.text import Tokenizer
import pandas as pd
import numpy as np

from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Embedding, Dense, GRU
from keras.optimizers import Adam

## Randomly eliminate some elements in the sequence
def random_eliminate(sequences, max_drop=6):
    seqs = []
    for sequence in sequences:
        r = range(len(sequence))
        keep =  max(1, len(r) - np.random.randint(0, max_drop))
        try:
            keep_idx = sorted(np.random.choice(r, keep, replace=False))
            new_sequence = [sequence[k] for k in keep_idx]
        except:
            new_sequence = sequence
        seqs.append(new_sequence)
    return seqs

## Combine some good sentences and bad sentences in a batch
## and keep them roughly 50/50
def batch_generator(
  good_seq,
  bad_seq,
  batch_size=256,
  random_drop=True):
    half_batch = batch_size // 2
    if half_batch > min(len(good_seq), len(bad_seq)):
        raise Exception("choose a smaller batch size")

    while True:
        good_batch = good_seq.sample(half_batch).values.copy()
        bad_batch = bad_seq.sample(half_batch).values.copy()

        if random_drop:
            good_batch = random_eliminate(good_batch)
            bad_batch = random_eliminate(bad_batch)

        combined_seq = np.hstack([good_batch, bad_batch])
        X = pad_sequences(combined_seq)
        y = half_batch * [False] + half_batch * [True]
        yield (X, y)


# read training csv data
df = pd.read_csv('./data/toxic_comment_train.csv')

# set toxic level target classes
targets = ['toxic', 'severe_toxic', 'obscene',
           'threat', 'insult', 'identity_hate']

df[targets].sum(axis='rows')
df[targets].sum(axis='rows') / len(df)
df['bad_message'] = df[targets].any(axis='columns')
#print(df['bad_message'].value_counts() / len(df))

tokenizer = Tokenizer()
tokenizer.fit_on_texts(df['comment_text'])
#print len(tokenizer.word_index)

threshold = 3
vocab_size = len([el for el in tokenizer.word_counts.items() if el[1] > threshold])
#print vocab_size

tokenizer = Tokenizer(num_words=vocab_size)
tokenizer.fit_on_texts(df['comment_text'])

sequences = np.array(tokenizer.texts_to_sequences(df['comment_text']))
longest_sequence = max([len(seq) for seq in sequences])
max_index = max([max(seq) for seq in sequences if len(seq) > 1])

# dump the tockenizer values
with open('tokenizer.pickle', 'wb') as handle:
    pickle.dump([
        tokenizer,
        longest_sequence], handle, protocol=pickle.HIGHEST_PROTOCOL)

data = df[['bad_message']].copy()
data['seq'] = sequences
#print data.head()

from sklearn.model_selection import train_test_split
data_train, data_test = train_test_split(data,
                                          test_size=0.3,
                                          random_state=0,
                                          stratify=data['bad_message'])

data_train_good_messages = data_train[data_train['bad_message'] == False].copy()
data_train_bad_messages = data_train[data_train['bad_message'] == True].copy()

data_test_good_messages = data_test[data_test['bad_message'] == False].copy()
data_test_bad_messages = data_test[data_test['bad_message'] == True].copy()

batch_size = 256
train_gen = batch_generator(data_train_good_messages['seq'],
                            data_train_bad_messages['seq'],
                            batch_size=batch_size)

# defining a model
model = Sequential()
model.add(Embedding(input_dim=vocab_size, output_dim=16))
model.add(GRU(32, dropout=0.15, recurrent_dropout=0.15))
model.add(Dense(1, activation='sigmoid'))
model.compile(
    optimizer=Adam(lr=0.01),
    loss='binary_crossentropy',
    metrics=['accuracy'])

model.summary()

for X_val, y_val in batch_generator(
  data_test_good_messages['seq'],
  data_test_bad_messages['seq'],
  batch_size=1024,
  random_drop=False):
    break

h = model.fit_generator(train_gen,
                        steps_per_epoch=len(data_train_bad_messages) / batch_size,
                        epochs=10,
                        verbose=1,
                        validation_data=(X_val, y_val))

#dfhistory = pd.DataFrame(h.history)
#dfhistory.plot()

dest_dir = "./result"
model_name = "toxic_model"
model_basename = os.path.join(dest_dir, model_name)
model.save(model_basename + ".h5")
print("Saved model to disk")
