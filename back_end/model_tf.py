import os
import tensorflow as tf
import keras.backend as K
from keras.models import load_model
from tensorflow.python.saved_model.builder import SavedModelBuilder
from tensorflow.python.saved_model.signature_def_utils_impl import predict_signature_def
from tensorflow.python.saved_model import tag_constants

# model parameters
export_base = "./result"
model_version = 1
model_name = "toxic_model"

# set the model save/export path
export_path = os.path.join(export_base, model_name, str(model_version))
print(export_path)

# initialise and open tf session
with tf.Session() as sess:

    # set keras backend to use this session
    K.set_session(sess)

    # load the saved model
    model_path = os.path.join(export_base, model_name + ".h5")
    model = load_model(model_path)

    # load global vars into the tf session
    sess.run(tf.global_variables_initializer())

    # for testing set to 0, for training model set to 1
    K.set_learning_phase(0)

    # builder for saving the model at the export path
    builder = SavedModelBuilder(export_path)

    # generate model signature map to use the model in the tf serving
    signature = predict_signature_def(
        inputs={"inputs": model.input},
        outputs={"outputs": model.output})

    # tag the model
    builder.add_meta_graph_and_variables(
        sess=sess,
        tags=[tag_constants.SERVING],
        signature_def_map={'predict': signature})

    # save builder instance and get the .pb file for deployment
    builder.save()