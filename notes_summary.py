import orgparse
    SHOW_NEWNOTES = config.getboolean("settings","NewNotes",fallback=True)
    SHOW_NOTELINKS = config.getboolean("settings","NoteLinks",fallback=True)
    NOTES_EXTENSION = config.get("settings","NotesExtension",fallback=".org")
###############
#New notes list
###############

newfile_regex = re.compile("b\/([^\n]*)\nnew file mode")

def find_new_files(lines):
    diff = "\n".join(lines)
    newfiles = newfile_regex.findall(diff)
    return newfiles

def is_note(filename):
    return (filename[-4:] == NOTES_EXTENSION)

def get_title(filename):
    org = orgparse.load(filename)
    if org.get_property("title"):
        return org.get_property("title")
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
file_link_regex = re.compile("\[\[file:(.*)\]\[(.*)\]\]")

def get_new_int_links(lines):
    curr_file = None
    intlinks = []
    for line in lines:
        f = diff_start.regex.match(line)
        if f:
            curr_file = r.group(1)

        m = file_link_regex.match(line)
        if m:
            linked_file = r.group(1)
            alias = r.group(2)
            intlinks.append((curr_file,linked_file,alias))
    return intlinks

def get_notelinks(lines):
    intlinks = get_new_int_links(lines)
    notelinks = [get_title(domain) + " -> " + get_title(target)
                 for (domain,target,_) in intlinks
                 if is_note(domain) & is_note(target)]
    return display_list("NEW NOTE LINKS",notelinks)

if SHOW_NEWNOTES:
    msg += get_newnotes(diff_lines)

if SHOW_NOTELINKS:
    msg += get_notelinks(diff_lines)