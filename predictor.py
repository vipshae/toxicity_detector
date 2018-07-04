##predictor model to actually make the connection to our tensorflow serving
import re
import pickle

import numpy as np
from keras.preprocessing.sequence import pad_sequences

from grpc.beta import implementations
import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2

# class
class Predictor:
    def __init__(self, server="localhost:9000"):
        with open('./tokenizer.pickle', 'rb') as f:
            self.tokenizer, self.maxlen = pickle.load(f)
        host, port = server.split(':')
        ## Set up channel to gRPC server
        channel = implementations.insecure_channel(host, int(port))
        self.stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

    def predict_toxicity(self, text, model_version=1):
        text = re.sub(r'\W+', ' ', text)
        intArray = []
        wordArray = text.lower().split()
        for word in wordArray:
            if word in self.tokenizer.word_index:
                intArray.append(self.tokenizer.word_index[word])
            else:
                print("Not including word: {}".format(word))

        x = pad_sequences(np.array([intArray]),
                          maxlen=self.maxlen)

        request = predict_pb2.PredictRequest()
        ## Set up the request here
        request.model_spec.name = 'toxic_model'
        request.model_spec.signature_name = 'predict'
        request.model_spec.version.value = model_version

        tp = tf.contrib.util.make_tensor_proto(x,
                                               dtype='float32',
                                               shape=[1, x.size])
        request.inputs['inputs'].CopyFrom(tp)
        return self.stub.Predict(request, 20.0)