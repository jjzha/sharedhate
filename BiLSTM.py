from keras.engine.topology import Layer, InputSpec
from keras import initializers
from keras import regularizers
from keras import constraints
from keras import backend as K
from keras.models import Model
from keras.layers import Dense, Dropout, LSTM, Input, Bidirectional, Embedding
from keras.callbacks import ModelCheckpoint
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from keras.utils.np_utils import to_categorical
from keras.models import load_model
from sklearn.metrics import precision_recall_fscore_support, classification_report, accuracy_score
import numpy as np
import pickle

# Import Files



class AttentionWithContext(Layer):
	"""
		Attention operation, with a context/query vector, for temporal data.
		Supports Masking.
		Follows the work of Yang et al. [https://www.cs.cmu.edu/~diyiy/docs/naacl16.pdf]
		"Hierarchical Attention Networks for Document Classification"
		by using a context vector to assist the attention
		# Input shape
			3D tensor with shape: `(samples, steps, features)`.
		# Output shape
			2D tensor with shape: `(samples, features)`.
		:param kwargs:
		Just put it on top of an RNN Layer (GRU/LSTM/SimpleRNN) with return_sequences=True.
		The dimensions are inferred based on the output shape of the RNN.
		Example:
			model.add(LSTM(64, return_sequences=True))
			model.add(AttentionWithContext())
		"""

	def __init__(self, init='glorot_uniform', kernel_regularizer=None, bias_regularizer=None, kernel_constraint=None, bias_constraint=None,  **kwargs):
		self.supports_masking = True
		self.init = initializers.get(init)
		self.kernel_initializer = initializers.get('glorot_uniform')

		self.kernel_regularizer = regularizers.get(kernel_regularizer)
		self.bias_regularizer = regularizers.get(bias_regularizer)

		self.kernel_constraint = constraints.get(kernel_constraint)
		self.bias_constraint = constraints.get(bias_constraint)

		super(AttentionWithContext, self).__init__(**kwargs)

	def build(self, input_shape):
		self.kernel = self.add_weight((input_shape[-1], 1),
								 initializer=self.kernel_initializer,
								 name='{}_W'.format(self.name),
								 regularizer=self.kernel_regularizer,
								 constraint=self.kernel_constraint)
		self.b = self.add_weight((input_shape[1],),
								 initializer='zero',
								 name='{}_b'.format(self.name),
								 regularizer=self.bias_regularizer,
								 constraint=self.bias_constraint)

		self.u = self.add_weight((input_shape[1],),
								 initializer=self.kernel_initializer,
								 name='{}_u'.format(self.name),
								 regularizer=self.kernel_regularizer,
								 constraint=self.kernel_constraint)
		self.built = True

	def compute_mask(self, input, mask):
		return None

	def call(self, x, mask=None):
		# (x, 40, 300) x (300, 1)
		multData =  K.dot(x, self.kernel) # (x, 40, 1)
		multData = K.squeeze(multData, -1) # (x, 40)
		multData = multData + self.b # (x, 40) + (40,)

		multData = K.tanh(multData) # (x, 40)

		multData = multData * self.u # (x, 40) * (40, 1) => (x, 1)
		multData = K.exp(multData) # (X, 1)

		# apply mask after the exp. will be re-normalized next
		if mask is not None:
			mask = K.cast(mask, K.floatx()) #(x, 40)
			multData = mask*multData #(x, 40) * (x, 40, )

		# in some cases especially in the early stages of training the sum may be almost zero
		# and this results in NaN's. A workaround is to add a very small positive number ε to the sum.
		# a /= K.cast(K.sum(a, axis=1, keepdims=True), K.floatx())
		multData /= K.cast(K.sum(multData, axis=1, keepdims=True) + K.epsilon(), K.floatx())
		multData = K.expand_dims(multData)
		weighted_input = x * multData
		return K.sum(weighted_input, axis=1)


	def compute_output_shape(self, input_shape):
		return (input_shape[0], input_shape[-1],)


def biLSTM(Xtrain, Ytrain, Xtest, Ytest, training, output):
	if training:
		y_train_reshaped = to_categorical(Ytrain, num_classes=2)

		t = Tokenizer()
		t.fit_on_texts(Xtrain)
		vocab_size = len(t.word_index) + 1
		Xtrain = t.texts_to_sequences(Xtrain)
		max_length = max([len(s) for s in Xtrain + Xtest])
		X_train_reshaped = pad_sequences(Xtrain, maxlen=max_length, padding='post')
		with open('tokenizer.pickle', 'wb') as handle:
			pickle.dump(t, handle, protocol=pickle.HIGHEST_PROTOCOL)
		print('Padded the data')
		## Loading in word embeddings and setting up matrix


		embeddings_index = dict()
		f = open('glove.840B.300d.txt')
		for line in f:
			values = line.split(' ')
			word = values[0]
			coefs = np.asarray(values[1:], dtype='float32')
			embeddings_index[word] = coefs
		f.close()

		print('Loaded %s word vectors.' % len(embeddings_index))
		embedding_matrix = np.zeros((vocab_size, 300)) #Dimension vector in embeddings
		for word, i in t.word_index.items():
			embedding_vector = embeddings_index.get(word)
			if embedding_vector is not None:
				embedding_matrix[i] = embedding_vector

		print("Loaded embeddings")

		### Setting up model
		embedding_layer = Embedding(vocab_size, 300, weights=[embedding_matrix], input_length=max_length, trainable=False, mask_zero=True)
		sequence_input = Input(shape=(max_length,), dtype='int32')
		embedded_sequences = embedding_layer(sequence_input)
		l_lstm = Bidirectional(LSTM(512, return_sequences=True))(embedded_sequences)
		l_drop = Dropout(0.4)(l_lstm)
		l_att = AttentionWithContext()(l_drop)
		preds = Dense(2, activation='softmax')(l_att)
		model = Model(sequence_input, preds)
		model.compile(loss='categorical_crossentropy', optimizer='Adam', metrics=['acc'])
		print(model.summary())
		print("Setting up model")


		######## Preparing test data
		y_test_reshaped = to_categorical(Ytest, num_classes=2)

		X_test = t.texts_to_sequences(Xtest)
		X_test_reshaped = pad_sequences(X_test, maxlen=max_length, padding='post')
		print("Done preparing testdata")


		filepath = "modelA.h5"
		checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=1, save_best_only=True, mode='min')
		callbacks_list = [checkpoint]
		model.fit(X_train_reshaped, y_train_reshaped, epochs=10, batch_size=64, validation_data=(X_test_reshaped, y_test_reshaped), callbacks=callbacks_list, verbose=1)
		loss, accuracy = model.evaluate(X_test_reshaped, y_test_reshaped, verbose=1)

		print("Done training")

	if output:
		print("Loading tokenizer...")
		with open('oldTokenizer.pickle', 'rb') as handle:
			t = pickle.load(handle)
		handle.close()
		print("Tokenizer loaded! Loading model...")
		model = load_model("oldModel.h5", custom_objects={'AttentionWithContext': AttentionWithContext})
		print("Model loaded! Processing data...")

		max_length = max([len(s) for s in Xtrain+ Xtest])
		datalist_reshaped = t.texts_to_sequences(Xtest)
		datalist_reshaped = pad_sequences(datalist_reshaped, maxlen=851, padding='post')

		print("Data processed! Predicting values...")
		score = model.predict(datalist_reshaped)
		yguess = np.argmax(score, axis=1)

		yguess = [str(item) for item in yguess]
		Ytest = [str(item) for item in Ytest]

		# with open('yguess_BiLSTM_' + task + '.txt', 'w+') as yguess_output:
		# 	for line in yguess:
		# 		yguess_output.write('%s\n' % line)

		accuracy = accuracy_score(Ytest, yguess)
		precision, recall, f1score, support = precision_recall_fscore_support(Ytest, yguess, average="weighted")
		report = classification_report(Ytest, yguess)

		print("Predictions made! returning output")
		return yguess, accuracy, f1score, report

	return True


