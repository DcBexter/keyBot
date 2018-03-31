import os
import praw
import time
import logging
import csv
from fake_useragent import UserAgent


def useragent():
    ua = UserAgent()
    return ua.random


def checkrepeat(text):
    count = {}
    returnlist = []
    for char in text:
        if char in count:
            count[char] += 1
        else:
            count[char] = 1
    for key in count:
        if count[key] > 2:
            returnlist.append(key)
    if len(returnlist) > 0:
        return True
    else:
        return False


def split(text):
    return text.upper().split()


def numdash(var):
    num = 0
    for x in var:
        if x == "-":
            num += 1
    if num == 2 or num == 4:
        return True
    return False


def checklist(key, dropliste):
    if any(item in key for item in dropliste):
        return True
    else:
        return False


def alreadyvisited(postid):
    with open(CSVFILE, 'r', newline='') as posts:
        reader = csv.reader(posts)
        for row in reader:
            if row[0] == postid:
                return True
        return False


def visitedpost(postid):
    with open(CSVFILE, 'a', newline='') as posts:
        writer = csv.writer(posts)
        writer.writerow([postid])


def findkey(text, dropliste, blackliste):
    matched = []
    allkeys = []
    matchedkeys = []
    verifiedkeys = []
    text = split(text)
    text = [x for x in text if "-" in x]
    for x in text:
        if numdash(x):
            matched.append(x)
        else:
            continue
    keys = [x.replace("-", "") for x in matched]
    keys = [x for x in keys if len(x) == 15 or len(x) == 25]
    for x in keys:
        allkeys.append("-".join([x[i:i + 5] for i in range(0, len(x), 5)]))
    for key in allkeys:
        fullkey = key.replace("-", "")
        if not checkrepeat(fullkey):
            verifiedkeys.append(key)
    for x in verifiedkeys:
        chunk = x.split("-")
        if len(chunk) == 5 or len(chunk) == 3:
            if not checklist(x, blackliste):
                if not checklist(x, dropliste):
                    matchedkeys.append(x)
    return matchedkeys


def trykey(key, cached):
    print("trying key: " + str(key))
    if len(key) > 1:
        for x in key:
            if x not in cached:
                print(x)
                os.system(AHKFILE + " " + str(x))
                cached.append(x)
                time.sleep(1)
    else:
        print(key[0])
        os.system(AHKFILE + " " + str(key[0]))
        cached.append(key)
        time.sleep(1)


def getposts(sub, dropliste, blackliste, cached):
    reddit = praw.Reddit(client_id='', client_secret='',
                         user_agent=useragent(), username='', password='')
    for comment in reddit.subreddit(sub).stream.comments():
        try:
            if not alreadyvisited(comment.id):
                if comment.created_utc < STARTTIME:
                    print("Comment too old: " + comment.id)
                    continue
                print("Parsing comment: " + "https://reddit.com" + comment.permalink + " by: " + str(comment.author))
                key = findkey(comment.body, dropliste, blackliste)
                if len(key) > 0:
                    print("!!! Found possible key in: " + comment.shortlink + " " + comment.title + " by: " + str(
                        comment.author))
                    trykey(key, cached)
                visitedpost(comment.id)
        except Exception as e:
            logging.exception(e)
            pass


SUBREDDIT = "steam"
DROPLIST = ["GREAT", "RIGHT", "GGXDD", "GABEN", "G4B3N", "SCUM"]
BLACKLIST = ["\\", "!", "§", "%", "&", "/", "?", "*", "@", "#", "_", "-"]
CACHE = []
CSVFILE = "posts.csv"
AHKFILE = "sbka.ahk"
STARTTIME = time.time()

getposts(SUBREDDIT, DROPLIST, BLACKLIST, CACHE)
print("done for now")
