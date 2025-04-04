import sort_functions

is_dryrun = False
is_verbose = True

input_folder = r'/Users/jk/Min disk/Bilder og video/Bilder/input/'
output_folder = r'/Users/jk/Min disk/Bilder og video/Bilder/sortert/year_month/'
unknown_folder = r'/Users/jk/Min disk/Bilder og video/Bilder/sortert/unknown/'
extensions_to_process = ['.jpg', '.jpeg', '.png', '.gif']
sort_functions.sort_files(input_folder, output_folder, unknown_folder, extensions_to_process, is_dryrun, is_verbose)
