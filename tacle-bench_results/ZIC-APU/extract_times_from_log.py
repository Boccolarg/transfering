#!/usr/bin/env python3
import os
import re

# Define the subdirectory where the results will be saved.
results_dir = "open8"

# Create the directory if it doesn't exist.
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

# The name of the log file to process
log_filename = "open8_uart_log2.txt"

# Regular expression to match the benchmark lines.
# It looks for a line like:
# "Benchmark adpcm_dec execution time:  70656 ns"
benchmark_pattern = re.compile(r'Benchmark\s+(\S+)\s+execution time(?:\s+is)?:\s+(\d+)\s+ns')

# Open and process the log file
with open(log_filename, "r") as infile:
    for line in infile:
        # Check if the line matches the benchmark pattern.
        match = benchmark_pattern.search(line)
        if match:
            # Extract the benchmark name and execution time.
            benchmark_name = match.group(1)
            execution_time = match.group(2)
            
            # Create the output filename based on the benchmark name in the subdirectory.
            results_filename = os.path.join(results_dir, f"{benchmark_name}_results.txt")
            
            # Append the result to the file.
            with open(results_filename, "a") as outfile:
                outfile.write(f"{execution_time} ns\n")
