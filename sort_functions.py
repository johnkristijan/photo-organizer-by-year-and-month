import os
import shutil
import exifread
import re
from datetime import datetime, timedelta

def parse_date_exif(date_string):
    """
    extract date info from EXIF data
    YYYY:MM:DD HH:MM:SS
    or YYYY:MM:DD HH:MM:SS+HH:MM
    or YYYY:MM:DD HH:MM:SS-HH:MM
    or YYYY:MM:DD HH:MM:SSZ
    """

    # split into date and time
    elements = str(date_string).strip().split()  # ['YYYY:MM:DD', 'HH:MM:SS']

    if len(elements) < 1:
        return None

    # parse year, month, day
    date_entries = elements[0].split(':')  # ['YYYY', 'MM', 'DD']

    # check if three entries, nonzero data, and no decimal (which occurs for timestamps with only time but no date)
    if len(date_entries) == 3 and date_entries[0] > '0000' and '.' not in ''.join(date_entries):
        year = int(date_entries[0])
        month = int(date_entries[1])
        day = int(date_entries[2])
    else:
        return None

    # parse hour, min, second
    time_zone_adjust = False
    hour = 12  # defaulting to noon if no time data provided
    minute = 0
    second = 0

    if len(elements) > 1:
        time_entries = re.split('(\+|-|Z)', elements[1])  # ['HH:MM:SS', '+', 'HH:MM']
        time = time_entries[0].split(':')  # ['HH', 'MM', 'SS']

        if len(time) == 3:
            hour = int(time[0])
            minute = int(time[1])
            second = int(time[2].split('.')[0])
        elif len(time) == 2:
            hour = int(time[0])
            minute = int(time[1])

        # adjust for time-zone if needed
        if len(time_entries) > 2:
            time_zone = time_entries[2].split(':')  # ['HH', 'MM']

            if len(time_zone) == 2:
                time_zone_hour = int(time_zone[0])
                time_zone_min = int(time_zone[1])

                # check if + or -
                if time_entries[1] == '+':
                    time_zone_hour *= -1

                dateadd = timedelta(hours=time_zone_hour, minutes=time_zone_min)
                time_zone_adjust = True


    # form date object
    try:
        date = datetime(year, month, day, hour, minute, second)
    except ValueError:
        return None  # errors in time format
    # try converting it (some "valid" dates are way before 1900 and cannot be parsed by strtime later)
    try:
        date.strftime('%Y/%m-%b')  # any format with year, month, day, would work here.
    except ValueError:
        return None  # errors in time format
    # adjust for time zone if necessary
    if time_zone_adjust:
        date += dateadd

    return date

def move_file(src_path, src_folder, dst_folder, filename, dryrun, verbose):
    # Recursive method that adds a "C" suffix if a file with the same name exists
    try:
        if os.path.exists(dst_folder + filename):
            data = os.path.splitext(filename)
            new_filename = data[0] + "C" + data[1]
            move_file(src_path, src_folder, dst_folder, new_filename, dryrun, verbose)
        else:
            if dryrun and verbose:
                print(f'[Drydun] From: {src_path} To: {dst_folder + filename}')
            else:
                shutil.move(src_path, dst_folder + filename)
            return True
    except FileNotFoundError:
        if verbose:
            print(f'File not found: {src_path}')
        return False

def get_date_from_tag(key, tags):
    for tag in tags.keys():
        if tag == key:
            the_date = tags[tag]
            try:
                return parse_date_exif(the_date)
            except Exception as e:
                return None

def print_tags(tags):
    for tag in tags.keys():
        if tag == 'JPEGThumbnail':
            print(f'tag: {tag} | val: too long to print')
        else:
            print(f'tag: {tag} | val: {tags[tag]}')

def get_file_birth(path):
    try:
        return datetime.fromtimestamp(os.path.getmtime(path))
    except Exception as e:
        return None

def sort_files(input_dir='./input/', output_dir='./output/', unknown_dir='./unknown/', accepted_extensions=['.jpg', '.jpeg', '.png', '.gif'], dryrun=False, verbose=False):
    # establish paths and accepted extensions
    file_list = os.listdir(input_dir) # dir is your directory path

    sort_format = '%Y/%m-%b'
    files_processed = 0
    unknown_file_count = 0
    number_files = 0
    success_processed = 0

    # file blacklist
    blacklist = ['.DS_Store', 'Icon\r']
    for file_to_ignore in blacklist:
        try:
            file_list.remove(file_to_ignore)
            if verbose:
                print(f'ignoring {file_to_ignore}')
        except ValueError:
            if verbose:
                print(f'no {file_to_ignore} files found')
    
    # find number of files for processing
    for root, subdirectories, files in os.walk(input_dir):
        for file in files:
            if file in blacklist:
                continue
            number_files = number_files + 1

    # starting to loop through input directory and subdirectories
    if verbose:
        print(f'--- STARTING ---')
    for root, subdirectories, files in os.walk(input_dir):
        for file in files:
            if file in blacklist:
                continue

            filepath = os.path.join(root, file)
            extension = os.path.splitext(file)[1].lower().strip()

            # progress
            files_processed = files_processed + 1
            if verbose:
                print(f'[{files_processed}/{number_files}] {filepath}')

            if extension in accepted_extensions:

                # Open image file for reading (must be in binary mode)
                f = open(filepath, 'rb')

                # Return Exif tags
                try:
                    tags = exifread.process_file(f)
                except Exception as e:
                    unknown_file_count = unknown_file_count + 1
                    move_file(filepath, root, unknown_dir, file, dryrun, verbose)
                    continue

                # first prio is to get date from 'DateTimeOriginal'
                valid_date = get_date_from_tag('EXIF DateTimeOriginal', tags)
                if not valid_date:
                    # second prio is the 'DateTimeDigitized'
                    valid_date = get_date_from_tag('EXIF DateTimeDigitized', tags)
                    if not valid_date:
                        # third prio is the 'Image DateTime'
                        valid_date = get_date_from_tag('Image DateTime', tags)
                        if not valid_date:
                            # 4th prio is the filesystem creation date
                            valid_date = get_file_birth(filepath)

                if valid_date is not None:
                    # create folder structure
                    dir_structure = valid_date.strftime(sort_format)
                    dirs = dir_structure.split('/')
                    dest_file = output_dir
                    for thedir in dirs:
                        dest_file = os.path.join(dest_file, thedir)
                        if not os.path.exists(dest_file):
                            os.makedirs(dest_file)

                    # if file with same name exists at destination,
                    # a "C" suffix will be added to the name recursively
                    move_file(filepath, root, dest_file + '/', file, dryrun, verbose)
                    success_processed = success_processed + 1
                else:
                    if verbose:
                        print_tags(tags)

            else:
                if file == 'Icon\r':
                    continue
                else:
                    unknown_file_count = unknown_file_count + 1
                    move_file(filepath, root, unknown_dir, file, dryrun, verbose)

    print(f'--- DONE ---')
    print(f'{files_processed} files processed.')
    print(f'{success_processed} files moved into correct folder.')
    print(f'{unknown_file_count} unknown files moved to unknown folder.')
    if dryrun:
        print(f'--- WARNING: DRYRUN MODE - NO FILES ACTUALLY MOVED --')
