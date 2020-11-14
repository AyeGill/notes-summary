configfiles = [os.path.abspath("notes-summary.ini"),
               os.path.abspath(".notes-summary.ini"),
               os.path.expanduser("~/notes-summary.ini"),
               os.path.expanduser("~/.notes-summary.ini")] #add lines here to add config files
    except urllib.error.URLError as r:
        return "[Error getting title]"
newfile_regex = re.compile("b\\/([^\\n]*)\\nnew file mode")
    logging.info("Identifying new files")
    diff = "".join(lines)
    logging.info("New files: %s", newfiles)
    logging.info("Getting title of %s", filename)
    try:
        org = orgparse.load(filename)
    except FileNotFoundError as e:
        logging.info("FileNotFoundError: %s", e)
        logging.info("looking in root dir")
        org = orgparse.load(os.path.basename(filename))
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
file_link_regex = re.compile("\[\[file:(.*?)\]\[(.*)\]\]")
        f = diff_start_regex.match(line)
            curr_file = f.group(1)
            logging.info("Now in file %s", curr_file)
        m = file_link_regex.search(line)
            linked_file = m.group(1)
            alias = m.group(2)
            logging.info("Adding link %s %s %s", curr_file, linked_file, alias)