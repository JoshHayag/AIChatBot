import random
import json
import pickle
import numpy as np
import tensorflow as tf

#natural log tool kit
import nltk
from nltk.stem import WordNetLemmatizer

#sets the words to their base form
lemmatizer= WordNetLemmatizer()

intents = json.loads(open('/Users/joshh/Desktop/CodeProjects/AISetUp/intents.json').read())

#load json file
words = []
classes = []
documents = []
ignore_letters = ['?', '!', '.', ',']

#establishes the patterns pulled from intents file
for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

#Lemmatizes and sorts the words from intents
words = [lemmatizer.lemmatize(word) for word in words if word not in ignore_letters]
words = sorted(set(words))

classes = sorted(set(classes))

pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

training = []
output_empty = [0] * len(classes)

#establish training data
for document in documents:
    bag = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append(bag + output_row)

random.shuffle(training)
training = np.array(training)

trainX = training[: , :len(words)]
trainY = training[: , len(words):]

#establishes model
model = tf.keras.Sequential()
#Dense creates the neurons for the network
model.add(tf.keras.layers.Dense(128, input_shape= (len(trainX[0]),), activation = 'relu'))
model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(64, activation = 'relu'))
model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(len(trainY[0]), activation = 'softmax'))

sgd = tf.keras.optimizers.SGD(learning_rate=0.01, momentum = 0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics = ['accuracy'])

hist = model.fit(trainX, trainY, epochs=200, batch_size=5, verbose=1)
model.save('chatbot_model.h5', hist)
print('Done')