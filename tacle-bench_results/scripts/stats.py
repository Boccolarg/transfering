import os
import re
import numpy as np

# Directory containing the extracted files
base_dir = '../ZIC-APU'

# Function to append statistics to an execution_time.txt file
def append_statistics_to_file(file_path):
    try:
        # Read the execution times from the file
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Filter out existing statistics lines and parse execution times
        execution_times = []
        for line in lines:
            line = line.strip()
            if line.startswith("Statistics -"):
                continue

            # First try to parse the line directly as a float
            try:
                execution_times.append(float(line))
                continue  # parsed successfully, go to next line
            except ValueError:
                pass

            # If direct conversion fails, try to extract a value from a line ending with 'ns'
            ns_match = re.match(r'^([0-9]*\.?[0-9]+)\s*ns$', line)
            if ns_match:
                value = float(ns_match.group(1))
                # If needed, convert nanoseconds to seconds (uncomment the next line)
                # value = value * 1e-9
                execution_times.append(value)
            else:
                # If the line does not match either format, ignore it.
                continue

        if not execution_times:
            print(f"No valid execution times found in {file_path}.")
            return

        # Calculate statistics
        mean = np.mean(execution_times)
        median = np.median(execution_times)
        std_dev = np.std(execution_times)
        min_val = np.min(execution_times)
        max_val = np.max(execution_times)

        # Prepare the statistics line
        stats_line = (f"Statistics - Mean: {mean:.6f}, Median: {median:.6f}, "
                      f"Std Dev: {std_dev:.6f}, Min: {min_val:.6f}, Max: {max_val:.6f}\n")

        # Append the statistics line to the file
        with open(file_path, 'a') as f:
            f.write(stats_line)

        print(f"Statistics appended to {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# Walk through the directory and find all files ending with '_results.txt'
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('_results.txt'):
            file_path = os.path.join(root, file)
            append_statistics_to_file(file_path)
