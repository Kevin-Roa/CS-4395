import sys
import os
import pickle
from nltk import word_tokenize
from nltk.util import ngrams


def main(files):
    for file in files:
        filePath = os.path.join(os.getcwd(), file)

        data = readFile(filePath)
        unigrams, bigrams = getNGrams(data)
        saveData(filePath, unigrams, bigrams)


def readFile(filePath):
    with open(filePath, "r", encoding="utf-8") as f:
        return f.read()


def getNGrams(data):
    def generateNGramDict(ngramList):
        ngramDict = {}
        for ngram in ngramList:
            ng = " ".join(ngram)
            if ng in ngramDict:
                ngramDict[ng] += 1
            else:
                ngramDict[ng] = 1
        return ngramDict

    data = data.lower().replace("\n", " ")
    tokens = word_tokenize(data)

    unigrams = list(ngrams(tokens, 1))
    bigrams = list(ngrams(tokens, 2))

    unigramDict = generateNGramDict(unigrams)
    bigramDict = generateNGramDict(bigrams)

    return unigramDict, bigramDict


# pickle the unigrams and bigrams in separate files
def saveData(filePath, unigrams, bigrams):
    file = open(filePath + "_out.pkl", "wb")
    lang = os.path.basename(filePath).split(".")[-1]
    out = {"unigrams": unigrams, "bigrams": bigrams, "lang": lang}
    pickle.dump(out, file)
    file.close()


# Run the program
# Get the file path from the command line
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide at least 1 input file.")
        exit()

    main(sys.argv[1:])
