import sys
import os
import re
import shutil
import requests
import pandas as pd
import json

from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords as sw
from bs4 import BeautifulSoup
from collections import deque
from random import sample
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from sklearn.feature_extraction.text import TfidfVectorizer

# Maximum possible searches = maxSiteLinks ^ maxSearchDepth
maxSearchDepth = 2
maxSiteLinks = 20

desiredTerms = [
    "anime",
    "manga",
    "movie",
    "show",
    "airing",
    "character",
    "chainsaw",
    "denji",
    "bleach",
    "gundam",
    "psycho",
    "hero",
    "isekai",
]


def main(websites):
    dirs = createDirectories()

    siteQ = deque((website, 0) for website in websites)
    linkSet = set()

    # Key = term, Value = list of usage in sentences
    userKB = {}  # User defined terms
    autoKB = {}  # Automatically added terms

    # Loop through all websites
    while siteQ:
        website = siteQ.popleft()

        if website[1] < maxSearchDepth:
            # Get the website
            soup = getWebsiteSoup(website[0])
            soup = cleanWebsiteSoup(soup)

            # Extract the links
            links = getWebsiteLinks(soup)
            # Reduce links to random subset of maxSiteLinks length
            if website[1] == 0:
                links = sample(links, min(maxSiteLinks * 2, len(links)))
            else:
                links = sample(links, min(maxSiteLinks, len(links)))

            # Add new links to the queue
            for link in links:
                if link not in linkSet:
                    linkSet.add(link)
                    siteQ.append((link, website[1] + 1))

            # Extract the text
            t = getWebsiteText(soup)

            # Tokenize the text
            sentTokens = sent_tokenize(t)
            wordTokens = word_tokenize(t)

            # Store the site data
            webFileName = re.sub(r"[^a-zA-Z0-9]", "", website[0])
            storeData(dirs[0], webFileName, t)
            storeData(dirs[1], webFileName, "\n".join(sentTokens))

            # Get important words
            terms = getImportantTerms(wordTokens)
            print(f"{webFileName}:\n{str(terms)}\n")

            # Add terms to knowledge base
            addToKnowledgeBase(autoKB, terms.keys(), sentTokens, [])
            # userKB is techincally a subset of autoKB, but it is easier to simply re-add the terms
            addToKnowledgeBase(userKB, terms.keys(), sentTokens, desiredTerms)

    # Convert sets to lists
    userKB = {k: list(v) for k, v in userKB.items()}
    autoKB = {k: list(v) for k, v in autoKB.items()}
    # Save knowledge bases to files
    storeData(dirs[2], "userKB.json", json.dumps(userKB))
    storeData(dirs[2], "autoKB.json", json.dumps(autoKB))


uas = UserAgent(
    software_names=[SoftwareName.CHROME.value],
    operating_systems=[OperatingSystem.WINDOWS.value],
    limit=20,
)


def getWebsiteSoup(website) -> BeautifulSoup:
    # Catch invalid URLs
    try:
        site = requests.get(
            website, headers={"User-Agent": uas.get_random_user_agent()}
        ).text
        return BeautifulSoup(site, "html.parser")
    except:
        return BeautifulSoup("", "html.parser")


rmTag = [
    "script",
    "style",
    "head",
    "header",
    "footer",
    "form",
    "input",
    "select",
    "option",
]
rmClass = [
    "_1FUNcfOeszr8eruqLxCMcR",
    "_3ZmEUUvrdj4LXpXC9XZdN7",
    " wBtTDilkW_rtT2k5x3eie",
    "MSTY2ZpsdupobywLEfx9u",
    "user-status-block",
    "js-user-status-block",
    "page-forum",
]
rmId = ["headerSmall", "menu"]


def cleanWebsiteSoup(soup: BeautifulSoup) -> BeautifulSoup:
    # Remove unwanted tags
    [t.decompose() for t in soup(rmTag)]

    # Remove unwanted tags with classes
    [c.decompose() for c in soup.find_all("div", attrs={"class": rmClass})]

    # Remove unwanted tags with ids
    [i.decompose() for i in soup.find_all("div", attrs={"id": rmId})]

    return soup


sites = [
    "reddit.com",
    "redd.it",
    "myanimelist.net",
    "anilist.co",
    "anime-planet.com",
    "animenewsnetwork.com",
    "crunchyroll.com",
    "vrv.co",
    "funimation.com",
    "youtube.com",
    "youtu.be",
    "wikipedia.org",
]
ignore = [
    "/u/",
    "/user/",
    "/profile",
    "/membership",
    "/people",
    "/dbchanges",
    "login",
    "register",
    "forum",
    "facebook",
    "twitter",
    "javascript",
    ".php",
]


def getWebsiteLinks(soup: BeautifulSoup) -> list:
    links = []
    for link in soup.find_all("a"):
        l = link.get("href")

        if l is None or l == "":
            continue

        # Ignore links containing ignored keywords
        if any(i in l for i in ignore):
            continue

        # Ignore links that are too long
        if len(l) > 256:
            continue

        # If it is a relative subreddit link, make it absolute, add it to the list
        if l.startswith("/r/"):
            links.append("https://reddit.com" + l)

        # If it is any other link, add it to the list
        elif l.startswith("https://"):
            links.append(l)

    # Filter out links that are not from the given sites
    links = [l for l in links if any(s in l for s in sites)]

    return links


def getWebsiteText(soup) -> str:
    text = soup.get_text()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\n", " ")
    # Remove reddit old browser warning
    text = text.replace(
        "Looks like you're using new Reddit on an old browser. The site may not work properly if you don't update your browser ! If you do not update your browser, we suggest you visit old reddit .Found the internet!",
        " ",
    )

    return text


def createDirectories():
    dirs = ["raw_files", "tokenized_files", "knowledge_base"]
    cwd = os.getcwd()

    for d in dirs:
        d = os.path.join(cwd, d)
        if os.path.exists(d):
            shutil.rmtree(d)
        os.mkdir(d)

    return dirs


def storeData(dir, filename, text):
    filename = os.path.join(dir, filename)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


def sentTokenizeText(text):
    return sent_tokenize(text)


extra = ["edit", "add", "main", "supporting", "director", "producer", "entries", "list"]


def getImportantTerms(word_tokens):
    # lowercase, get alphas
    tokens = [w.lower() for w in word_tokens if w.isalpha()]
    # Get enlish stopwords
    stopwords = set(sw.words("english")).union(set(extra))

    # Use TfIdf to get the most important terms
    tfidf = TfidfVectorizer(use_idf=True, stop_words=stopwords)
    tfs = tfidf.fit_transform(tokens)
    feature_names = tfidf.get_feature_names_out()
    dense = tfs.todense()
    denselist = dense.tolist()
    df = pd.DataFrame(denselist, columns=feature_names)

    return dict(df.sum().nlargest(40))


def addToKnowledgeBase(kb, terms, sentTokens, desiredTerms):
    for term in terms:
        if term in desiredTerms or len(desiredTerms) == 0:
            if term not in kb:
                kb[term] = set()
            for sent in sentTokens:
                if term in sent.lower():
                    kb[term].add(sent)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide at least 1 anime site to crawl.")
        exit()
    main(sys.argv[1:])
