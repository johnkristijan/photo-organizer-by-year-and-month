import sort_functions

is_dryrun = False
is_verbose = True

input_folder = r'/Users/jk/Min disk/Bilder og video/Video/input/'
output_folder = r'/Users/jk/Min disk/Bilder og video/Video/sortert/year_month/'
unknown_folder = r'/Users/jk/Min disk/Bilder og video/Video/sortert/unknown/'
extensions_to_process = ['.mp4', '.mov', '.avi', '.mpg', '.mts', '.m4v', '.vob', '.dv', '.wmv']
sort_functions.sort_files(input_folder, output_folder, unknown_folder, extensions_to_process, is_dryrun, is_verbose)
