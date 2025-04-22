import os
import subprocess

def optimize_video(input_file, output_file, bitrate='1000k', resolution=None):
    """
    Optimizes and reduces the size of an MP4 video file.
    
    Parameters:
    - input_file (str): Path to the input video file.
    - output_file (str): Path to save the optimized video.
    - bitrate (str): Target bitrate for compression (default: 1000k).
    - resolution (str or None): Desired resolution (e.g., '1280x720'). If None, keeps original resolution.
    """
    if not os.path.exists(input_file):
        print("Error: Input file does not exist.")
        return
    
    # Base ffmpeg command
    command = [
        'ffmpeg', '-i', input_file, '-b:v', bitrate, '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k',
        '-movflags', '+faststart', '-y', output_file
    ]
    
    # Adjust resolution if specified
    if resolution:
        command.insert(-2, '-vf')
        command.insert(-2, f"scale={resolution}")
    
    try:
        subprocess.run(command, check=True)
        print(f"Optimization complete: {output_file}")
    except subprocess.CalledProcessError:
        print("Error during video processing.")

# Example usage
input_video = input("Upload file")
output_video = "optimized_output.mp4"
optimize_video(input_video, output_video, bitrate='800k', resolution='1280x720')
