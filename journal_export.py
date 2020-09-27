import sys, getopt, json, os, shutil, re
from urllib  import parse

class JournalDirectory:
    id = ''
    name = ''
    parent = None
    path = ''

class JournalEntry:
    id = ''
    name = ''
    content = ''
    directory = ''
    path = ''

# Core

def run_export(pathToWorldDirectory):
    print(f'Running Journal Exporter for {pathToWorldDirectory}')
    directories = load_directories_hierarchy(pathToWorldDirectory)
    entries = load_journal_entries(pathToWorldDirectory)
    directories = [d for d in directories if d.id in [e.directory for e in entries] + [d.parent for d in directories]]
    create_journal_folders(directories, entries, pathToWorldDirectory)
    create_journal_files(entries, directories)
    create_index_files(directories, entries, pathToWorldDirectory)
    copy_image_files(entries, pathToWorldDirectory)

# DB file readers.

def load_directories_hierarchy(pathToWorldDirectory):
    print('Loading Journal Directories from `folders.db`...')
    foldersdb_path = pathToWorldDirectory + safe_path('\\data\\folders.db')
    with open(foldersdb_path, 'r', encoding='utf8') as f:
        directories = [parse_folder_entry(line) for line in f if line]
    print('Journal Directories loaded.')
    return [directory for directory in directories if directory]

def load_journal_entries(pathToWorldDirectory):
    print('Loading Journal Entries from `journal.db`.')
    journaldb_path = pathToWorldDirectory + safe_path('\\data\\journal.db')
    with open(journaldb_path, 'r', encoding='utf8') as f:
        entries = [parse_journal_entry(line) for line in f]
    print('Journal Entries loaded.')
    return [entry for entry in  entries if entry]

# DB file parsers.

def parse_folder_entry(line):
    folder_entry = json.loads(line)
    print(f'Parsing directory `{folder_entry["name"]}... `', end='')
    if folder_entry['type'] != 'JournalEntry':
        print('Not a Journal Directory.')
        return None
    directory = JournalDirectory()
    directory.id = folder_entry['_id']
    directory.name = folder_entry['name']
    directory.parent = folder_entry['parent']
    print('Loaded.')
    return directory

def parse_journal_entry(line):
    journal_entry = json.loads(line)
    if journal_entry['permission']['default'] < 2:
        return None
    print(f'Parsing entry `{journal_entry["name"]}... `', end='')
    entry = JournalEntry()
    entry.id = journal_entry['_id']
    entry.name = journal_entry['name']
    entry.directory = journal_entry['folder']
    entry.content = journal_entry['content']
    if 'img' in journal_entry and journal_entry['img'] != '':
        entry.content += '\n<p><img src=\"{}}\"></p>'.format(journal_entry['img'])
    print('Loaded.')
    return entry

# Markdown exporters.

def create_journal_folders(directories, entries, pathToWorldDirectory):
    root_folder_path = '{}{}{}'.format('Journal Export', os.path.sep, pathToWorldDirectory.split(os.path.sep)[-1])
    print(f'Creating root export directory `{root_folder_path}`... ', end='')
    try:
        os.makedirs(root_folder_path, exist_ok=True)
        print('Created')
    except:
        print(f'Failed | {sys.exc_info()}')
        sys.exit(2)
    [create_directory_path(d, directories, root_folder_path) for d in directories]
    for path in [d.path for d in directories]:
        try:
            print(f'Creating directory `{path}`... ', end='')
            os.makedirs(path, exist_ok=True)
            print('Created')
        except:
            print(f'Failed | {sys.exc_info()}')
            continue
    

def create_journal_files(entries, directories):
    for entry in entries:
        directory = [d for d in directories if d.id == entry.directory][0]
        entry.path = '{}{}{}.md'.format(directory.path, os.path.sep, entry.name)
        try:
            print(f'Creating Journal entry `{entry.path}`... ', end='')
            with open(entry.path, 'w', encoding='utf8') as f:
                f.write(entry.content)
            print('Created')
        except:
            print(f'Failed | {sys.exc_info()}')
            continue

def create_index_files(directories, entries, pathToWorldDirectory):
    print('Creating navigation files.')
    created_readme_files = []
    root_folder_path = '{}{}{}'.format('Journal Export', os.path.sep, pathToWorldDirectory.split(os.path.sep)[-1])
    file_paths = [d.path.replace(root_folder_path, '') for d in directories] + [e.path.replace(root_folder_path, '') for e in entries]
    for file_path in file_paths:
        path_fragments = file_path.split(os.path.sep)
        file_path_without_name = os.path.sep.join(path_fragments[:-1])
        readme_path = '{}{}{}README.md'.format(root_folder_path, file_path_without_name, os.path.sep)
        print(f'Creating link for `{file_path_without_name}`... ', end='')
        if readme_path not in created_readme_files:
            with open(readme_path, 'w', encoding='utf8') as f:
                f.write(f'Journal Entries for `{pathToWorldDirectory.split(os.path.sep)[-1]}{file_path_without_name}`:\n')
            created_readme_files.append(readme_path)
        with open(readme_path, 'a', encoding='utf8') as f:
            file_name = path_fragments[-1]
            f.write(f'- [{file_name.replace(".md", "")}]({parse.quote(file_name)})\n')
        print('Created')

def copy_image_files(entries, pathToWorldDirectory):
    path_to_data = re.search(r'(.*Data).*', pathToWorldDirectory).groups()[0]
    for entry in entries:
        try:
            print(f'Extracting asset paths from `{entry.name}`... ', end='')
            asset_paths = re.findall(r'.*src=\"(.*?)\".*', entry.content)
            print(f'Extracted {len(asset_paths)}')
            for path in [safe_path(p) for p in [parse.unquote(path.replace('/', '\\'), encoding='utf-8') for path in asset_paths]]:
                try:
                    path_to_asset = '{}{}{}'.format(path_to_data, os.path.sep, path)
                    entry_directory = re.findall(r'.*\{}'.format(os.path.sep), entry.path)[0]
                    path_to_copy =  '{}{}{}'.format(entry_directory, os.path.sep, path)
                    print('Copying image asset `{}` ... '.format(path_to_asset), end='')
                    os.makedirs(re.findall(r'.*\{}'.format(os.path.sep), path_to_copy)[0], exist_ok=True)
                    shutil.copyfile('{}{}{}'.format(path_to_data, os.path.sep, path), path_to_copy)
                    print('Copied')
                except:
                    print(f'Failed | {sys.exc_info()}')
                    continue
        except:
            print(f'Failed | {sys.exc_info()}')
            continue

# Helpers

def create_directory_path(directory, directories, root_folder_path):
    path = directory.name
    if directory.parent != None:
        parent_directory = [d for d in directories if d.id == directory.parent][0]
        path = '{}{}{}'.format(parent_directory.name, os.path.sep, path)
    directory.path = '{}{}{}'.format(root_folder_path, os.path.sep, path)
    return directory.path

def safe_path(path):
    for separator in ['\\', '/']:
        path = path.replace(separator, os.path.sep)
    return path

# Main

def main():
    print('Journal Export by Thandulfan')
    pathToWorldDirectory = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:] ,'help:h', ['world=',])
    except:
        print(f'Unable to parse arguments  | {sys.exc_info()}')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ['-h', '-help']:
            print('python journal_export.py -world PATH_TO_WORLD_DIRECTORY')
            sys.exit()
        if opt == '--world':
            pathToWorldDirectory = safe_path(arg)
    if pathToWorldDirectory == '':
        print('ERROR: No world directory provided.')
        sys.exit(2)
    run_export(pathToWorldDirectory)

if __name__ == '__main__' :
    main()  