#!/usr/bin/env python3


#!/usr/bin/env python3

import sys
import re
import urllib.request
import requests
import os
import logging
from bs4 import BeautifulSoup

#setup: pip3 install beautifulsoup4
#See the "sending mail" part below to hook up mailgun
#run this scrip on a cronjob in a git repo
#Look at get_git_diff to see what you need to change if your git setup is weird

#modify this to run in debugging mode
TEST = False

###############
#LOGGING SETUP
###############


#Log to stdout when testing, else log to file
if not TEST:
    logging.basicConfig(filename="scandiff.log",
                   encoding="utf-8",
                   level=logging.WARNING,
                   format='%(asctime)s %(message)s')
else:
    logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s %(message)s')


logging.info("If you're seeing this, I'm running in debug mode")

##################
######SENDING MAIL
##################

#This is set up for mailgun (mailgun.org)
#Use your own setup if not

#Store your info in env variables
try:
    apikey = os.environ['MAILGUN_API_KEY'] #your mailgun api key
    mgdomain = os.environ['MAILGUN_DOMAIN'] #your mailgun domain
    targetmail = os.environ['TARGET_EMAIL'] #the mail you want to send this to
except:
    logging.critical("Mailgun config variables not readable. Program unable to run until these are set")
    sys.exit()

name = "Notes robot" #The sender of the mail

subject = "Your notes digest!"

url = "https://api.mailgun.net/v3/" + mgdomain + "/messages"
sender = name + " <mailgunbot@" + mgdomain + ">"

def sendmail(text):
    logging.info("Sending mail. Length of message: %i", len(text))
    r = requests.post(
        url,
        auth=("api",apikey),
        data={
            "from": sender,
            "to": [targetmail],
            "subject": subject,
            "text": text})
    return(r.text)



#############
#GET GIT DIFF
#############

def get_git_diff():
    logging.info("Getting git diff")
    #I actually want to save this in the log files
    logging.warning("Current commit: %s", os.popen("git show").readlines()[0])

    diff = os.popen("git diff master origin/master").readlines()
    if TEST:
        diff = os.popen("git diff $(git rev-list -n1 --before \"7 days ago\" origin/master)").readlines()
    pull = os.popen("git pull").read()
    logging.info("Result of pull: %s", pull)
    return diff

diff_lines = get_git_diff()


###############
#FORMATTING
###############
def display_list(title,ls):
    return (title + "\n" + ("=" * len(title)) + "\n\n" + "\n".join(["- " + l for l in ls]))

###############
## External links dump
###############


#links regex defined by https:// followed by a string w no spaces, newlines
#or "[]" - the latter to avoid capturing more than necessary in org contexts.
extlink_regex = re.compile(r"https?:\/\/([^ \n\]\[]*)")

links = []

def find_title(url):
    try:
        soup = BeautifulSoup(urllib.request.urlopen(url), features='lxml')
        logging.info("Found title of link %s successfully", url)
        return soup.title.string
    except urllib.error.URLError(r):
        logging.warning("Error getting title of link: %s", url)
        logging.warning("Error: %s", r)
    except:
        logging.warning("Undetermined error getting title of link: %s", url)
        return "[Error getting title]"

def display_link(url):
    return (find_title(url).strip() + " : " + url)

for line in diff_lines:
    if(line[0] != '+'): #if we're not looking at an added line
        continue #skip this line

    #Pull out links

    match = extlink_regex.search(line)
    if(match):
        links.append(match.group(0))

linktexts = [display_link(url) for url in links]
link_output = display_list("LINKS", linktexts)

######################
#TYING THINGS TOGETHER
######################

sendmail(link_output)
