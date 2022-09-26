import random
import sys
import os
from collections import Counter
import nltk
from nltk.corpus import stopwords


def main(filePath):
    file = readFile(filePath)

    calcLexicalDiversity(file)

    tokens, nouns = preProcessText(file)
    words = generateWordsDict(tokens, nouns)
    top50 = getTopNWords(words, 50)

    guessingGame(top50)


# Read the text file at the given path and return the text
def readFile(filePath):
    with open(os.path.join(os.getcwd(), filePath), "r") as f:
        return f.read()


# Calculate the lexical diversity of the given text
def calcLexicalDiversity(file):
    # Tokenize the text
    tokens = [t.lower() for t in nltk.word_tokenize(file)]
    # Get # unique tokens
    unique = set(tokens)
    print("Unique tokens: ", len(unique))
    print("Total tokens:  ", len(tokens))
    print(f"Lexical diversity: {len(unique) / len(tokens):.2f}")


# Take the text and split it into tokens and nouns
def preProcessText(file):
    print("\nPreprocessing text...")
    # Tokenize the text
    # Keep only alpha non-stopwords that are > 5 characters
    tokens = [
        t.lower()
        for t in nltk.word_tokenize(file)
        if t.isalpha() and t not in stopwords.words("english") and len(t) > 5
    ]

    # Lemmatize the tokens
    lemmas = set([nltk.WordNetLemmatizer().lemmatize(t) for t in tokens])

    # Tag the lemmatized tokens
    tags = nltk.pos_tag(lemmas)

    # Print the first 20 tagged tokens
    print("Sample Tagged Tokens: ")
    print(tags[:20])

    # Select the nouns from the tagged tokens
    nouns = [t[0] for t in tags if t[1].startswith("N")]

    # Print # tokens and # nouns
    print(f"Number of tokens: {len(tokens)}")
    print(f"Number of nouns:  {len(nouns)}")

    return tokens, nouns


# Create a dict of {noun: count}
def generateWordsDict(tokens, nouns):
    words = {}

    for noun in nouns:
        words[noun] = tokens.count(noun)

    return words


# Get the top N words from the given dict
# Ordered by count
def getTopNWords(words, n):
    # Sort the words dict by count
    top50 = Counter(words).most_common(n)

    # Print the top 50 most common words
    print("\nTop 50 most common nouns:")
    print(top50)

    return top50


# Play the guessing game
def guessingGame(words):
    print("\n############## !!Guessing Game!! ##############")
    # Select a random word from the top 50
    # Initialize other variables
    def getRandomWord():
        word = random.choice(list(words))
        letters = {l: False for l in word[0]}
        guesses = set()
        return word[0], letters, guesses

    # Get the guess from the user
    def getGuess():
        return input("Guess a letter or enter '!' to exit: ")[0].lower()

    # Check if the user has guessed the word
    def checkWinCondition():
        return all(letters.values())

    # Print the current state of the word
    def printHiddenWord():
        print("".join([f"{l} " if letters[l] else "_ " for l in word]))

    word, letters, guesses = getRandomWord()
    guess = ""

    wins = 0
    points = 0
    lives = 5

    # Loop until the user runs out of lives/exits
    while lives > 0:
        # Print current score
        print(f"\n### {lives} lives left ### \n")

        # Print hidden word
        printHiddenWord()

        # Get the user's guess
        guess = getGuess()

        # Check if the user wants to exit
        if guess == "!":
            break

        # Check if already guessed this letter
        if guess in guesses:
            print("You already guessed that letter!")
            continue
        else:
            guesses.add(guess)

        # Check if the guess is in the word
        if guess in word:
            print("Correct!")
            letters[guess] = True
            lives += 1
            points += 1
        else:
            print("Incorrect!")
            lives -= 1

        # Check if the user has won the round
        if checkWinCondition():
            print("You win!")
            wins += 1
            word, letters, guesses = getRandomWord()

    # Exit text
    print("\nGame over!")
    if lives == 0:
        print("You ran out of lives!")

    print(f"The word was: {word}")
    print(f"You got {wins} wins and scored {points} points!")
    print("Thanks for playing!")


# Run the program
# Get the file path from the command line
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide an input file.")
        exit()

    main(sys.argv[1])
