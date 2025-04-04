# photo-organizer-by-year-and-month
A python script for organizing a set of image files into a folder structure with years and months.

# this is the one to use!
the images and videos are sorted directly on the google drive "Bilder og video" folder

# requirements
python3

# setup example (for mac os x with fish terminal)
`python3 -m venv venv`
`source venv/bin/activate.fish`
`pip install exifread`

create the following folders in the root dir (where sort.py is)
- input
- output
- unknown

# example how to use this script
1. copy/paste files and folders into the `input` dir
2. run script in venv by executing `python sort_images.py` or `python sort_videos.py`

# result
All files with file types ['.jpg', '.jpeg', '.png', '.gif']
will be sorted in folders with year/months if Exif Date exists.
All other files will be _moved_ to the `unknown` folder.

# convert .3gp to .mp4
1. place all .3gp files in this folder
2. run `python convert_3gp_to_mp4.py`
3. output converted files will be in /mp4_files/

# convert .heic to .jpg
1. place all .heic files in this folder
2. run `heic2jpg -s ./`
3. files will be placed in this folder as well
