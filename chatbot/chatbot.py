import numpy as np
import datetime
import pickle
import names
import sys
import os
import re

from random import choice, shuffle, randint
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout
from keras.optimizers import Adam
from time import sleep

posSynonyms = [
    "VERY GOOD",
    "phenominal",
    "stupendous",
    "exceptional",
    "amazing",
    "VERY trustworthy",
    "among some of the best",
    "excellent",
    "fantastic",
]


# Default bot info
botInfo = {
    "name": "???",  # Changes for every user
    "description": f"I am a chatbot who loves giving {choice(posSynonyms)} advice.",
    "version": "1.0",
    "author": "Kevin Roa",
    "creationDate": datetime.datetime(2022, 11, 12),
}

# Default user model
userModel = {
    "name": "You",
    "age": 0,
    "location": "",
    "likes": [""],
    "dislikes": [""],
    "mood": [""],
    "botName": "",
}

# User intents for the ML model
# Detect intent via phrase => random response
def getIntents():
    return {
        "greetings": {
            "phrases": [
                "Hi",
                "Hello",
                "Hey",
                "Yo",
                "whats up",
                "howdy",
                "greetings",
                "hows it going",
                "pleasure to meet you",
                "nice to meet you",
            ],
            "responses": ["Hello!", "Hey!", "Hi!", "Howdy!", "Greetings!"],
        },
        "goodbyes": {
            "phrases": [
                "bye",
                "goodbye",
                "see you later",
                "see you soon",
                "talk to you later",
                "talk to you soon",
                "have to go",
                "gotta go",
                "cya",
                "im leaving",
                "quit",
                "exit",
            ],
            "responses": [
                "Bye!",
                "Goodbye!",
                "Talk to you later!",
                "It was a pleasure talking to you!",
                "I hope we can chat again soon! Bye!",
            ],
        },
        "name": {
            "phrases": [
                "What is your name?",
                "What should I call you?",
                "What do you go by?",
                "What do people call you?",
                "What do you call yourself?",
                "What did you say your name was?",
                "who are you",
            ],
            "responses": [
                f"My name is {botInfo['name']}!",
                f"You can call me {botInfo['name']}",
                f"I go by {botInfo['name']}.",
                f"Just call me {botInfo['name']}.",
            ],
        },
        "age": {
            "phrases": ["How old are you?", "What is your age?", "When were you made?"],
            "responses": [
                f"I was made on {botInfo['creationDate'].strftime('%B %d, %Y')}.",
                f"I was developed {datetime.datetime.now().day - botInfo['creationDate'].day} days ago.",
                "I am a newborn! I was developed quite recently!",
                f"{botInfo['author']} made me on {botInfo['creationDate'].strftime('%B %d, %Y')}.",
                f"My birthday is on {botInfo['creationDate'].strftime('%B %d, %Y')}.",
            ],
        },
        "creator": {
            "phrases": ["Who made you?", "Who created you?", "Who is your creator?"],
            "responses": [
                f"I was created by {botInfo['author']}!",
                f"{botInfo['author']} made me!",
                f"{botInfo['author']} is my dad :)",
            ],
        },
        "advice": {
            "phrases": [
                "What is your advice?",
                "Give me some advice",
                "Do you have any advice for me",
                "I'm looking for advice",
                "What should I do?",
                "What do you think about XXX?",
                "What do you suggest?",
                "What do you recommend?",
                "What is your opinion on this?",
                "What is your take on this?",
                "Im having trouble with this",
                "Could you help me with this?",
                "how come XXX is YYY",
                "can you give me advice on how to",
                "can you give me advice",
                "i need some advice on",
                "i need some advice",
                "please give me advice on",
                "advise me on",
                "help me out with" "i need help on",
            ],
            "responses": [
                "I think you should take a hike!",
                "Go on a run or something..",
                "Maybe just give up.",
                "I think you should just give up.",
                "Giving up is always an option.",
                "You could just give up.",
                "Just go an cry yourself to sleep.",
                "Maybe search that up on google instead. Bing it, perhaps. Or Yahoo it even.",
                f"YOU want advice from ME? {userModel['name']} you are hopeless.",
                f"{userModel['name']}... you overthink things too much. Just do it.",
                "Hmm... thats a dumb question.",
                "I don't know, I'm just a chatbot.",
                "Perhaps you should consult your daily horoscope.",
                "Honestly, I don't know how to help you.",
                "My advice is to just give up.",
                "Step 1: Give up. Step 2: ??? Step 3: Profit.",
                "First, abandon all hope. Then, do whatever you want.",
                "First, ghost everyone. Then, move to Alaska and forget about everything. Live a new life.",
                "Go down to the local bar and get drunk. That's what I would do.",
                "Sink into a deep depression. That's what I would do.",
                "Go down with the ship.",
                "Just ignore your problems and it will all go away.",
                "Go bug some people on social media and see if they can help you.",
            ],
        },
        "advice2": {
            "phrases": [
                "wow",
                "damn",
                "that was mean",
                "you are useless",
                "trash bot",
                "that wasnt helpful",
                "fuck you",
                "eat shit",
                "your are not good",
                "give better advice",
                "you suck",
                "your advice is bad",
            ],
            "responses": [
                "Hey, I don't get payed to do this.",
                "I don't get paid enough for this.",
                f"Well, I thought what I said was {choice(posSynonyms)}.",
                "You don't have to listen to me if you don't want to..",
                "Maybe ask me for something else then.",
                "To each their own..",
                "Sorry if you didn't like what I said.",
                "I'm sorry if you didn't like what I said.",
                "lol",
            ],
        },
        "jokes": {
            "phrases": [
                "Tell me a joke",
                "Tell me something funny",
                "Tell me a funny joke",
                "Do you know any good jokes",
                "Do you know any funny jokes",
                "what is a good joke",
                "tell me a good joke",
            ],
            "responses": [
                f"Once upon a time there was a person named {userModel['name']} who spent their time talking to a chatbot. The end.",
                f"Imagine being from {userModel['location']}. Couldn't be me.",
                f"It's crazy how you are spending your time talking to a chatbot instead of going out.",
                f"People who like {choice(userModel['likes'])} are a joke.",
                "You LMFAOOO",
                "I'm a chatbot, I'm not that funny.",
                "No. 😐",
            ],
        },
        "about": {
            "phrases": [
                "what can you do",
                "what are you capable of",
                "what can you do for me",
                "what do you do",
                "what are you able to do",
                "what are your abilities",
                "what can i do with you",
                "what else can you do",
            ],
            "responses": [
                "I give great advice!",
                "I can give you advice on things.",
                f"I give out {choice(posSynonyms)} advice.",
                "I can give you advice on anything.",
                "People say my advice is {choice(posSynonyms)}.",
                "I can tell you more about myself if you ask.",
                "I can tell you all about myself! Just ask.",
                "I'm a fantastic comedian! Ask me for a joke.",
                "I can tell you jokes! Just ask.",
            ],
        },
        "aboutSelf": {
            "phrases": [
                "what do you know about me",
                "tell me about myself",
                "what have you learned from me",
                "who am i",
            ],
            "responses": [
                f"I know that you are from {userModel['location']}.",
                f"I know that you like {choice(userModel['likes'])}.",
                f"I know that you are {userModel['age']} years old.",
                f"Your name is {userModel['name']} and you are {userModel['age']} years old.",
                f"Your name is {userModel['name']} and you are from {userModel['location']}.",
                f"I know that you are {userModel['age']} years old and you are from {userModel['location']}.",
                f"I know that you are {userModel['age']} years old and you like {userModel['likes']}.",
            ],
        },
    }


inqueries = {
    "metBefore": [
        "Before we begin, have we ever met before?",
        "Hey, have we met before?",
        "Have we met before?",
        "Hmmm... have I chatted with you before?",
        "Have we talked before?",
        "Have we chatted before?",
        "Hello! Wait.. do I know you?",
    ],
    "name1": [
        "Wait.. what was your name again?",
        "Your name is...?",
        "What was your name again?",
        "Your name is on the tip of by tongue.. what was it again?",
        "I may have forgotten your name.. what was it again?",
        "I forgot your name, could you remind me?",
        "Sorry, I forgot your name. What was it again?",
        "Sorry, I forgot your name. What was it?",
    ],
    "name2": [
        "What is your name?",
        "What should I call you?",
        "What name do you go by?",
    ],
    "age": [
        "How old are you?",
        "What is your age?",
    ],
    "location": [
        "Where are you from?",
        "Where do you live?",
        "Where are you located?",
    ],
    "likes": [
        "What do you like?",
        "What are your interests?",
        "What are your hobbies?",
    ],
    "dislikes": [
        "What do you dislike?",
        "What are your pet peeves?",
        "What do you hate?",
    ],
    "mood": [
        "How are you?",
        "How are you feeling?",
        "How are you doing?",
        "How's it going?",
    ],
}

# Used when low confidence
defaultResponses = [
    "I don't quite understand.",
    "I don't know what you mean.",
    "Could you rephrase that?",
    "I don't know what you're talking about.",
    "I don't know what you mean by that.",
    "I don't know what you're trying to say.",
]

# Introduce other inqueries
redirections = [
    "Lets talk about something else.",
    "How about we change the subject?",
    "What else do you want to talk about?",
    "Ask me anything!",
    "What else do you want advice on?",
    "Do you have any other questions?",
    "Do you want more advice on something else?",
]


def getIntentsData():
    lemmatizer = WordNetLemmatizer()

    words = []
    classes = []
    documents = []

    intents = getIntents()

    for intent in intents:
        for phrase in intents[intent]["phrases"]:
            w = word_tokenize(phrase)
            words.extend(w)
            documents.append((w, intent))

            if intent not in classes:
                classes.append(intent)

    ignore = [".", "?", "!", ",", "'", '"']

    words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore]
    words = sorted(set(words))
    classes = sorted(set(classes))

    return words, classes, documents


def buildModel(X, y):
    model = Sequential()
    model.add(Dense(128, input_shape=(len(X[0]),), activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(len(y[0]), activation="softmax"))

    opt = Adam(learning_rate=0.001)
    # opt = SGD(learning_rate=0.01, momentum=0.9, decay=1e-6, nesterov=True)

    model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])

    print("Training model...")
    print(model.summary())
    hist = model.fit(np.array(X), np.array(y), epochs=200, verbose=1, batch_size=5)
    print("Finished training model.")

    return model, hist


def trainModel():
    words, classes, documents = getIntentsData()

    lemmatizer = WordNetLemmatizer()
    training = []

    # Bag of words approach
    for doc in documents:
        bag = []
        d_phrases = doc[0]
        d_class = doc[1]

        d_phrases = [lemmatizer.lemmatize(word.lower()) for word in d_phrases]

        for w in words:
            bag.append(1) if w in d_phrases else bag.append(0)

        out = list([0] * len(classes))
        out[classes.index(d_class)] = 1

        training.append([bag, out])

    shuffle(training)
    training = np.array(training)

    X = list(training[:, 0])
    y = list(training[:, 1])

    model, hist = buildModel(X, y)

    saveModel(model, hist, words, classes)

    return model, words, classes


def saveModel(model, hist, words, classes):
    model.save("model", hist)

    with open("model/words.pkl", "wb") as f:
        pickle.dump(words, f)

    with open("model/classes.pkl", "wb") as f:
        pickle.dump(classes, f)

    print("Saved model to ./model")


def loadModel():
    if not os.path.exists("model"):
        yn = input("Model not found. Would you like to train a new model? (y/n): ")
        if yn.lower() == "y":
            return trainModel()
        else:
            print(
                'Please run the program with the "-train" or "-T" flag to train a new model.'
            )
            exit()
    else:
        model = load_model("model")
        words = pickle.load(open("model/words.pkl", "rb"))
        classes = pickle.load(open("model/classes.pkl", "rb"))

        return model, words, classes


def loadUserModel(name):
    try:
        global userModel

        f = open(f"usermodels/{name.lower()}.pkl", "rb")
        userModel = pickle.load(f)

        f.close()
    except Exception:
        print("User model not found.")
        exit()


def saveUserModel(userModel):
    if not os.path.exists("usermodels"):
        os.makedirs("usermodels")

    with open(f"usermodels/{userModel['name'].lower()}.pkl", "wb") as f:
        pickle.dump(userModel, f)


def promptUserModel():
    global userModel
    global botInfo

    yes = ["yes", "yeah", "yea", "yup", "we have"]
    no = ["no", "nah", "na", "nope", "we havent"]

    inp = botAsk(choice(inqueries["metBefore"])).lower()

    # remove non alpha characters
    inp = re.sub(r"[^a-zA-Z\s]", "", inp)

    if any(x in inp for x in yes):
        name = botAsk(choice(inqueries["name1"])).lower()
        loadUserModel(name)
        botInfo["name"] = userModel["botName"]

        oldUser = [
            f'Hey {userModel["name"]}! It\'s nice to chat with you again.',
            f"Oh hey {userModel['name']}, I didn't recognize you.",
            f"I'm glad you're back {userModel['name']}!",
            f"Welcome back {userModel['name']}!",
            f"It's good to see you again {userModel['name']}!",
            f"{userModel['name']}!!! Hey!!",
        ]

        botPrint(choice(oldUser))

    elif any(x in inp for x in no):
        # Generate a random bot name
        userModel["botName"] = names.get_first_name()
        botInfo["name"] = userModel["botName"]

        newUser = [
            "Oh! Nice to meet you!",
            "Nice to meet you!",
            "Pleasure meeting you.",
            "Pleased to meet you.",
        ]

        botPrint(choice(newUser))
        botPrint(choice(getIntents()["name"]["responses"]))
        botPrint(
            "I'd like to get to know you a bit better, could you answer some questions for me?"
        )

        userModel["name"] = botAsk(choice(inqueries["name2"])).capitalize()
        userModel["age"] = botAsk(choice(inqueries["age"]))
        userModel["location"] = botAsk(choice(inqueries["location"]))
        userModel["likes"] = botAsk(choice(inqueries["likes"]))
        userModel["dislikes"] = botAsk(choice(inqueries["dislikes"]))

        saveUserModel(userModel)

        botPrint(
            f"Great! I'm {botInfo['name']} version {botInfo['version']}. {botInfo['description']}"
        )

    else:
        print(choice(defaultResponses))
        promptUserModel()

    return userModel


def botPrint(str):
    # Respond after .1 to .4 seconds
    sleep(randint(2, 4) / 10)
    print(f'{botInfo["name"]}: {str}')


def botAsk(question):
    botPrint(question)
    return input(f"{userModel['name']}: ")


def userPrint(str):
    print(f'{userModel["name"]}: {str}')


def userInput():
    return input(f"{userModel['name']}: ")


def preProcessText(text):
    words = word_tokenize(text)

    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(w.lower()) for w in words]

    return words


def bagOfWords(text, words):
    textWords = preProcessText(text)
    bag = [0] * len(words)

    for w in textWords:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1

    return np.array(bag)


def predict(text, model, words, classes):
    bag = bagOfWords(text, words)

    preds = model.predict(np.array([bag]), verbose=0)

    return classes[np.argmax(preds)]


def getReply(pred, intents):
    return choice(intents[pred]["responses"])


def main():
    global userModel

    print("\nLoading ML model...")
    model, words, classes = loadModel()

    print("\nInitializing chatbot...")
    userModel = promptUserModel()
    intents = getIntents()

    while True:
        inp = userInput()

        pred = predict(inp, model, words, classes)

        reply = getReply(pred, intents)
        botPrint(reply)

        # Exit the program
        if pred == "goodbyes":
            exit()

        # Randomly talk back to the user
        if randint(1, 4) == 1:
            botPrint(choice(redirections))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If args has --train or -T
        if any(x in sys.argv for x in ["--train", "-T"]):
            trainModel()

    main()
