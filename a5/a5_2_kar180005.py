import sys
import os
import pickle
from nltk import word_tokenize
from nltk.util import ngrams


def main(directory, testFileDir, solFileDir):
    files = getFiles(directory)
    data = readFiles(files)
    classify(testFileDir, data)
    evalAccuracy(testFileDir, solFileDir)


# Get all the pkl files in the given directory
def getFiles(directory):
    path = os.path.join(os.getcwd(), directory)
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".pkl")]

    if len(files) == 0:
        print("No pickle files found in the given directory")
        exit()

    return files


# Read the pickle files and return a dictionary of the data
def readFiles(paths):
    return [pickle.load(open(p, "rb")) for p in paths]


def classify(testFileDir, data):
    def getProbability(line, langData):
        unigrams = langData["unigrams"]
        bigrams = langData["bigrams"]
        V = len(unigrams)

        lineTokens = word_tokenize(line.lower())
        lineBi = list(ngrams(lineTokens, 2))

        prob = 1
        for bigram in lineBi:
            bg = " ".join(bigram)
            n = bigrams[bg] if bg in bigrams else 0
            d = unigrams[bigram[0]] if bigram[0] in unigrams else 0
            prob *= (n + 1) / (d + V)

        return prob

    # Get the test file
    testFilePath = os.path.join(os.getcwd(), testFileDir)
    file = open(testFilePath, "r", encoding="utf-8").readlines()
    outFile = open(testFilePath + "_out.txt", "w")

    for i, line in enumerate(file):
        maxProb = -1
        maxLang = ""
        for langData in data:
            prob = getProbability(line, langData)
            if prob > maxProb:
                maxProb = prob
                maxLang = langData["lang"]
        outFile.write(f"{i+1} {maxLang}\n")

    outFile.close()


def evalAccuracy(testFileDir, solFileDir):
    outFilePath = os.path.join(os.getcwd(), testFileDir + "_out.txt")
    outFile = open(outFilePath, "r").readlines()

    solFilePath = os.path.join(os.getcwd(), solFileDir)
    solFile = open(solFilePath, "r").readlines()

    correct = 0
    for i in range(len(outFile)):
        out = outFile[i].strip()
        sol = solFile[i].strip()

        if out == sol:
            correct += 1
        else:
            print(f"Line {i} incorrect. Expected {sol}, got {out}")

    print("Accuracy: " + str(correct / len(outFile) * 100) + "%")


# Run the program
# Get the file path from the command line
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a directory containing pkl files.")
        exit()

    if len(sys.argv) < 3:
        print("Please provide a test file.")
        exit()

    if len(sys.argv) < 4:
        print("Please provide a solution file.")
        exit()

    main(sys.argv[1], sys.argv[2], sys.argv[3])
