import os

def merge_chunks_from_folder(folder_path, output_file_path):
    """Merges all chunk files from the specified folder into the original file."""
    # List all the chunk files in the folder and sort them by their names
    chunk_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.zip')])
    
    # Ensure the chunk files are sorted in order
    chunk_files = sorted(chunk_files, key=lambda x: int(x.split('_part_')[1].split('.zip')[0]))

    with open(output_file_path, 'wb') as output_file:
        for chunk_file in chunk_files:
            chunk_path = os.path.join(folder_path, chunk_file)
            with open(chunk_path, 'rb') as f:
                output_file.write(f.read())
            print(f"Merged {chunk_file} into {output_file_path}")

# Example usage:
folder_path = "/path/to/chunks"  # Path to the folder containing the chunk files
merge_chunks_from_folder(folder_path, "merged_backup.zip")
