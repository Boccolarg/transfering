import os
import numpy as np

# Directory containing the extracted files
base_dir = '../ZIC-APU'
configurations = ['baseline', 'cpu8', 'fork8', 'memcpy8', 'open8', 'udp8']

# Directory to save the stats files
stats_dir = '../ZIC-APU/stats'
if not os.path.exists(stats_dir):
    os.makedirs(stats_dir)

# Function to read execution times from a file
def read_execution_times(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        execution_times = [float(line.strip()) for line in lines if not line.startswith("Statistics -")]
        return execution_times
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

# Function to calculate statistics
def calculate_statistics(execution_times):
    return {
        'mean': np.mean(execution_times),
        'median': np.median(execution_times),
        'std_dev': np.std(execution_times),
        'min': np.min(execution_times),
        'max': np.max(execution_times)
    }

# Function to create a stats file for a specific benchmark
def create_stats_file(benchmark):
    stats_file_path = os.path.join(stats_dir, f"{benchmark}_stats.txt")
    
    with open(stats_file_path, 'w') as stats_file:
        for config in configurations:
            file_path = os.path.join(base_dir, config, f"{benchmark}_execution_time.txt")
            if os.path.exists(file_path):
                execution_times = read_execution_times(file_path)
                if execution_times:
                    stats = calculate_statistics(execution_times)
                    stats_file.write(f"Configuration: {config}\n")
                    stats_file.write(f"  Mean: {stats['mean']:.6f}\n")
                    stats_file.write(f"  Median: {stats['median']:.6f}\n")
                    stats_file.write(f"  Std Dev: {stats['std_dev']:.6f}\n")
                    stats_file.write(f"  Min: {stats['min']:.6f}\n")
                    stats_file.write(f"  Max: {stats['max']:.6f}\n\n")
            else:
                print(f"File not found: {file_path}")

# Main function to process all benchmarks
def main():
    # Find all benchmarks in the baseline directory
    baseline_dir = os.path.join(base_dir, 'baseline')
    benchmarks = [f[:-19] for f in os.listdir(baseline_dir) if f.endswith('_execution_time.txt')]

    for benchmark in benchmarks:
        print(f"Creating stats file for {benchmark}...")
        create_stats_file(benchmark)

if __name__ == "__main__":
    main()
