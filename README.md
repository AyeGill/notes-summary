# notes-summary
A simple script that sends you a periodic email summarizing your notes

## Features
- [x] List of new external links
- [ ] List of new internal, i.e note->note links
- [ ] List of new files
  - Filtered by properties like length etc
  - List of orphaned files, files without links
  - List of new "non-note" files, like pictures etc
  - [ ] Summary of specific "journal" files?

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
