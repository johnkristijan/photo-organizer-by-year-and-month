import os
import shutil
import exifread
from datetime import datetime, timedelta
import re

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

def move_file(src_path, src_folder, dst_folder, filename):
    # Recursive method that adds a "C" suffix if a file with the same name exists
    try:
        if os.path.exists(dst_folder + filename):
            data = os.path.splitext(filename)
            new_filename = data[0] + "C" + data[1]
            move_file(src_path, src_folder, dst_folder, new_filename)
        else:
            shutil.move(src_path, dst_folder + filename)
            return True
    except FileNotFoundError:
        print(f'File not found: {src_path}')
        return False


input_dir = './input/'
output_dir = './output/'
unknown_dir = './unknown/'

blacklist = ['.DS_Store', 'Icon\r']
accepted_extensions = ['.jpg', '.jpeg', '.png', '.gif']

files_processed = 0
unknown_file_count = 0
number_files = 0

file_list = os.listdir(input_dir) # dir is your directory path
try:
    file_list.remove(blacklist[0])
except ValueError:
    print('')
try:
    file_list.remove(blacklist[1])
except ValueError:
    print('')

for root, subdirectories, files in os.walk(input_dir):
    for file in files:
        if file in blacklist:
            continue
        number_files = number_files + 1

print(f'--- STARTING ---')

for root, subdirectories, files in os.walk(input_dir):
    for file in files:
        if file in blacklist:
            continue

        filepath = os.path.join(root, file)
        extension = os.path.splitext(file)[1].lower()

        if extension in accepted_extensions:
            date_found = False
            files_processed = files_processed + 1
            # print(f'processing file {file}')
            # Open image file for reading (must be in binary mode)
            f = open(filepath, 'rb')

            # Return Exif tags
            tags = exifread.process_file(f)

            for tag in tags.keys():
                # print(f'tag: {tag}')
                if tag == 'EXIF DateTimeOriginal':
                    date_1 = tags[tag]
                    print(f'[{files_processed}/{number_files}] "{file}" DATE FOUND: {date_1}')
                    date_found = True
                    try:
                        exifdate = parse_date_exif(date_1)  # check for poor-formed exif data, but allow continuation
                    except Exception as e:
                        exifdate = None

                    # create folder structure
                    sort_format = '%Y/%m-%b'
                    dir_structure = exifdate.strftime(sort_format)
                    dirs = dir_structure.split('/')
                    dest_file = output_dir
                    for thedir in dirs:
                        dest_file = os.path.join(dest_file, thedir)
                        if not os.path.exists(dest_file):
                            os.makedirs(dest_file)

                    move_file(filepath, root, dest_file + '/', file)
                # if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
                #     print("Key: %s, value %s" % (tag, tags[tag]))

            if not date_found:
                print(f'[{files_processed}/{number_files}] "{file}" DATE NOT FOUND.')
                # for tag in tags.keys():
                #     print(f'tag: {tag} | value: {tags[tag]}')
        else:
            unknown_file_count = unknown_file_count + 1
            if file == 'Icon\r':
                continue
            else:
                move_file(filepath, root, unknown_dir, file)
                # shutil.move(filepath, unknown_dir)

print(f'--- DONE ---')
print(f'{files_processed} files processed.')
print(f'{unknown_file_count} unknown files moved to unknown folder.')
