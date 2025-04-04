import os
from moviepy.editor import VideoFileClip

def convert_3gp_to_mp4(input_file, output_file):
    try:
        video_clip = VideoFileClip(input_file)
        video_clip.write_videofile(output_file, codec='libx264')
        print(f'Conversion complete: {input_file} -> {output_file}')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    input_dir = "."  # Current directory
    output_dir = "mp4_files"  # Directory to save the MP4 files

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith((".3gp", ".3gP", ".3Gp", ".3GP")):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, os.path.splitext(filename)[0] + ".mp4")

            convert_3gp_to_mp4(input_file, output_file)
