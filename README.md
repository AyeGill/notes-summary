# notes-summary
A simple script that sends you a periodic email summarizing your notes

## Overview
The purpose of this script is to send a periodic email summarizing the changes
to a git repository. The idea is that the repo contains some sort of notes, and
the email is a periodic summary of what you've done. The script uses 
[mailgun](https://mailgun.com) to send the mail. Support for other stuff is on
my list, but it should be pretty easy to add it yourself, too, if you really
need it. Just modify the `sendmail` function to be something else.

Currently the script assumes your notes are `.org` files. The list of links
should work whether or not this is the case, but the others don't. A more
format-agnostic version is on the list.

Currently the following things can be included in the mail:
- A list of new *external* links
- A list of new notes
- A list of *internal* links, i.e links between your notes

The script works by, each time it runs, comparing a local copy of the repo to a remote copy,
then pulling the remote copy. This obviously means you can't mess around with the local copy - there needs to be a copy just for this script to look at.
In the future this may be improved by having the script maintain a record of the commit last time it ran, and comparing that to the current commit.

## TODO
- [ ] Add support for using your own SMTP stuff.
  - See eg https://realpython.com/python-send-email/ for how to set this up using gmail.
- [ ] Add "interesting new *contents* to the email, e.g. all the stuff you wrote in your journal, or the contents of certain new files.
- [ ] Add support for other note formats.
- [ ] Record commits instead of using local/remote to remember the state

## Setup
- Before you use this script, make sure you have the following things:
  - A git repository somewhere containing your notes which is regularly updated
  - A server somewhere which is on all the time where you can run this script
  - A user on that server which can pull from the git repository without you entering a password. If it's a public github repo this isn't an issue, but if not you may need to set up som ssh stuff. Or you can try to fiddle with things to make it automatically enter your password. That's up to you.
  - An account with [mailgun](https://mailgun.com). Their free tier should be fine for your purposes. Find your api key and domain.
- Install python3 and pip3 (you probably already have these), then install the needed libraries:

``` shell
  $ apt install python3 pip3
  $ pip3 install requests beautifulsoup4 orgparse
```
- Create `notes-summary.ini` somewhere the script can find it (see below) and fill it out. This is *not optional* - you need to provide your mailgun api details
  - The script looks for `notes-summary.ini` and `.notes-summary.ini`, both in the home directory and in the directory where it runs (but this will be your notes directory itself, which you may not want to clutter up). You can modify this by adding items to the list `configfiles` at the top of the script, see the comment there. You can also pass these as command-line args.
  For example `python3 notes_summary.py /path/to/config.ini` adds `/path/to/config.ini` as a potential path.
- Make a local copy of the repo by doing `git clone <repo address>`
- Make a cronjob to run the script in the git repo. Example crontab:
```
0 0 * * 1 cd /path/to/repo && python3 /path/to/script
```
  - See [this page](https://ostechnix.com/a-beginners-guide-to-cron-jobs/) for a basic Cron tutorial.

## Configuration
Pretty self-explanatory by a `.ini` file (see above for location)
The options are as follows (or see the script itself)
