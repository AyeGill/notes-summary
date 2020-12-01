#!/usr/bin/env python3


#!/usr/bin/env python3

import sys
import re
import urllib.request
import configparser
import os
import logging
import requests
import orgparse
from bs4 import BeautifulSoup

#setup: pip3 install beautifulsoup4
#See the "sending mail" part below to hook up mailgun
#run this scrip on a cronjob in a git repo
#Look at get_git_diff to see what you need to change if your git setup is weird

###############
#LOADING CONFIG
###############

configfiles = [os.path.abspath("notes-summary.ini"),
               os.path.abspath(".notes-summary.ini"),
               os.path.expanduser("~/notes-summary.ini"),
               os.path.expanduser("~/.notes-summary.ini")] #add lines here to add config files
configfiles += sys.argv[1:]
config = configparser.ConfigParser()
config.read(configfiles)

try:
    TEST = config.getboolean("settings","Test",fallback=False)
    SHOW_EXTLINKS = config.getboolean("settings","ExternalLinks",fallback=True)
    SHOW_NEWNOTES = config.getboolean("settings","NewNotes",fallback=True)
    SHOW_NOTELINKS = config.getboolean("settings","NoteLinks",fallback=True)
    MAILGUN_APIKEY = config.get("settings","MailgunApiKey")
    MAILGUN_DOMAIN = config.get("settings","MailgunDomain")
    TARGET_MAIL = config.get("settings","TargetMail")
    NOTES_EXTENSION = config.get("settings","NotesExtension",fallback=".org")
    SENDER_NAME = config.get("settings","SenderName",fallback="Summary bot :)")
    LOGFILE = config.get("settings","LogFile",fallback="notes_summary_log.txt")
    GIT_MAIN_BRANCH = config.get("settings","GitMainBranch",fallback="master")
except:
    logging.critical("Error reading config!")
    sys.exit()

###############
#LOGGING SETUP
###############


#Log to stdout when testing, else log to file
if not TEST:
    logging.basicConfig(filename=LOGFILE,
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

subject = "Your notes digest!"

mgurl = "https://api.mailgun.net/v3/" + MAILGUN_DOMAIN + "/messages"
sender = SENDER_NAME + " <mailgun@" + MAILGUN_DOMAIN + ">"

def sendmail(text):
    logging.info("Sending mail. Length of message: %i", len(text))
    r = requests.post(
        mgurl,
        auth=("api",MAILGUN_APIKEY),
        data={
            "from": sender,
            "to": [TARGET_MAIL],
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
    fetch = os.popen("git fetch").read()
    logging.info("Result of fetch: %s", fetch)
    diff = os.popen("git diff " + GIT_MAIN_BRANCH + " origin/"+GIT_MAIN_BRANCH).readlines()
    logging.info("Diff:")
    logging.info("".join(diff))
    #if TEST:
    #    diff = os.popen("git diff $(git rev-list -n1 --before \"7 days ago\" origin/"+GIT_MAIN_BRANCH+")").readlines()
    merge = os.popen("git merge").read()
    logging.info("Result of merge: %s", merge)
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


def find_title(url):
    try:
        soup = BeautifulSoup(urllib.request.urlopen(url), features='lxml')
        logging.info("Found title of link %s successfully", url)
        return soup.title.string
    except urllib.error.URLError as r:
        logging.warning("URLError getting title of link: %s", url)
        logging.warning("Error: %s", r)
        return "[Error getting title]"
    except Exception as e:
        logging.warning("Undetermined error getting title of link: %s", url)
        logging.warning("Error: %s", e)
        return "[Error getting title]"


def display_link(url):
    return (find_title(url).strip() + " : " + url)
#links regex defined by https:// followed by a string w no spaces, newlines
#or "[]" - the latter to avoid capturing more than necessary in org contexts.
extlink_regex = re.compile(r"https?:\/\/([^ \n\]\[]*)")

def get_extlinks(lines):

    links = []

    for line in lines:
        if(line[0] != '+'): #if we're not looking at an added line
            continue #skip this line
        #
        #Pull out links

        match = extlink_regex.search(line)
        if(match):
            links.append(match.group(0))

    logging.info("External links: %s", links)

    linktexts = [display_link(url) for url in links]
    link_output = display_list("LINKS", linktexts)
    return link_output

###############
#New notes list
###############

newfile_regex = re.compile("b\\/([^\\n]*)\\nnew file mode")

def find_new_files(lines):
    diff = "".join(lines)
    logging.info("Identifying new files")
    newfiles = newfile_regex.findall(diff)
    logging.info("New files: %s", newfiles)
    return newfiles

def is_note(filename):
    return (filename[-4:] == NOTES_EXTENSION)

def get_title(filename):
    logging.info("Getting title of %s", filename)
    try:
        org = orgparse.load(filename)
    except FileNotFoundError as e:
        logging.info("FileNotFoundError: %s", e)
        logging.info("looking in root dir")
        return get_title(os.path.basename(filename))
    except e:
        logging.info("Error: %s", e)
    try:
        x = org.get_file_property("title")
        if x:
            return x
    except RuntimeError as e:
        logging.info("Trying to see if title was list")
        x = org.get_file_property_list("title")
        if x:
            return ": ".join(x)
    except _:
        logging.info("Unrecognized error getting title, falling back")
    return filename #fallback

def get_newnotes(lines):
    newfiles = find_new_files(lines)
    newnotenames = [get_title(f) for f in newfiles if is_note(f)]
    return display_list("NEW NOTES",newnotenames)

###################
#New internal links
###################

# this is a bit tricky because we need to
# 1) look for new internal links, like [[file:...]], and also:
# 2) For each such link, find out which file it was added to.
# We do this by going through lines and maintaining the file we're in as state.

diff_start_regex = re.compile("diff --git [^\n]* b\/([^\n]*)")
file_link_regex = re.compile("\[\[file:(.*?)\]\[(.*)\]\]")

def get_new_int_links(lines):
    curr_file = None
    intlinks = []
    for line in lines:
        f = diff_start_regex.match(line)
        if f:
            curr_file = f.group(1)
            logging.info("Now in file %s", curr_file)
        if (line[0] != '+'):
            continue
        m = file_link_regex.search(line)
        if m:
            linked_file = m.group(1)
            alias = m.group(2)
            intlinks.append((curr_file,linked_file,alias))
            logging.info("Adding link %s %s %s", curr_file, linked_file, alias)
    return intlinks

def get_notelinks(lines):
    intlinks = get_new_int_links(lines)
    notelinks = [get_title(domain) + " -> " + get_title(target)
                 for (domain,target,_) in intlinks
                 if is_note(domain) & is_note(target)]
    return display_list("NEW NOTE LINKS",notelinks)

######################
#TYING THINGS TOGETHER
######################

msg = ""
if SHOW_EXTLINKS:
    msg += get_extlinks(diff_lines)
    msg += "\n\n"

if SHOW_NEWNOTES:
    msg += get_newnotes(diff_lines)
    msg += "\n\n"

if SHOW_NOTELINKS:
    msg += get_notelinks(diff_lines)
    msg += "\n\n"

logging.warning("Sending mail now. Length = %i", len(msg))
sendmail(msg)
