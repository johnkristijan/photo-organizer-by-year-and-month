# photo-organizer-by-year-and-month
A python script for organizing a set of image files into a folder structure with years and months.

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
2. run script in venv by executing `python sort.py`

# result
All files with file types ['.jpg', '.jpeg', '.png', '.gif']
will be sorted in folders with year/months if Exif Date exists.
All other files will be _moved_ to the `unknown` folder.
