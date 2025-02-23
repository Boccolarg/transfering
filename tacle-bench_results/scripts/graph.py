import os
import re
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Directory containing the extracted files
base_dir = '../Preempt-RT-containers'
configurations = ['baseline', 'cpu8', 'fork8', 'memcpy8', 'open8', 'udp8']

# Base directory to save the plots
plots_base_dir = os.path.join(base_dir, 'plots')

# Create subdirectories for each plot type
plot_types = {
    'standard': os.path.join(plots_base_dir, 'standard_plots'),
    'box': os.path.join(plots_base_dir, 'box_plots'),
    'violin': os.path.join(plots_base_dir, 'violin_plots'),
    'cdf': os.path.join(plots_base_dir, 'cdf_plots'),
}

for folder in plot_types.values():
    os.makedirs(folder, exist_ok=True)

def read_execution_times(file_path):
    """
    Reads the execution times from a file.
    Expected formats:
      - "1854131 ns"  -> interpreted as nanoseconds and converted to milliseconds.
      - "1.853"       -> interpreted as seconds and converted to milliseconds.
    Lines starting with "Statistics -" are skipped.
    """
    execution_times = []
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith("Statistics -"):
                continue
            # Check for a line ending with "ns" (nanoseconds)
            ns_match = re.match(r'^([0-9]*\.?[0-9]+)\s*ns$', line)
            if ns_match:
                try:
                    ns_val = float(ns_match.group(1))
                    # Convert nanoseconds to milliseconds
                    ms_val = ns_val / 1e6
                    execution_times.append(ms_val)
                    continue
                except Exception as conv_err:
                    print(f"Error converting line '{line}' in {file_path}: {conv_err}")
            # Fallback: assume the line is a plain number in seconds.
            try:
                sec_val = float(line)
                # Convert seconds to milliseconds
                ms_val = sec_val * 1000
                execution_times.append(ms_val)
            except Exception as conv_err:
                print(f"Error processing line '{line}' in {file_path}: {conv_err}")
        return execution_times
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def gather_benchmark_data(benchmark):
    """
    For a given benchmark name, checks for files in each configuration.
    It first looks for <benchmark>_results.txt, and if not found, for <benchmark>_execution_time.txt.
    """
    data = []
    labels = []
    for config in configurations:
        file_path = os.path.join(base_dir, config, f"{benchmark}_results.txt")
        if not os.path.exists(file_path):
            file_path = os.path.join(base_dir, config, f"{benchmark}_execution_time.txt")
        if os.path.exists(file_path):
            execution_times = read_execution_times(file_path)
            if execution_times:  # Only add if data is non-empty
                data.append(execution_times)
                labels.append(config)
            else:
                print(f"No valid data in file: {file_path}")
        else:
            print(f"File not found for configuration '{config}' and benchmark '{benchmark}'")
    return data, labels

def plot_standard(benchmark, data, labels):
    """Creates a standard (line) plot of execution times for each configuration."""
    plt.figure(figsize=(10, 6))
    for exec_times, label in zip(data, labels):
        plt.plot(range(len(exec_times)), exec_times, marker='o', linestyle='-', label=label)
    plt.title(f"Standard Plot of Execution Times for {benchmark}")
    plt.xlabel("Sample Index")
    plt.ylabel("Execution Time (ms)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    save_path = os.path.join(plot_types['standard'], f"{benchmark}_standard.png")
    plt.savefig(save_path)
    plt.close()
    print(f"Standard plot saved to {save_path}")

def plot_box(benchmark, data, labels):
    """Creates a box plot of execution times for each configuration."""
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=data)
    plt.xticks(ticks=range(len(labels)), labels=labels)
    plt.title(f"Box Plot of Execution Times for {benchmark}")
    plt.xlabel("Configuration")
    plt.ylabel("Execution Time (ms)")
    plt.grid(True)
    plt.tight_layout()
    save_path = os.path.join(plot_types['box'], f"{benchmark}_box.png")
    plt.savefig(save_path)
    plt.close()
    print(f"Box plot saved to {save_path}")

def plot_violin(benchmark, data, labels):
    """Creates a violin plot of execution times for each configuration."""
    plt.figure(figsize=(10, 6))
    sns.violinplot(data=data)
    plt.xticks(ticks=range(len(labels)), labels=labels)
    plt.title(f"Violin Plot of Execution Times for {benchmark}")
    plt.xlabel("Configuration")
    plt.ylabel("Execution Time (ms)")
    plt.grid(True)
    plt.tight_layout()
    save_path = os.path.join(plot_types['violin'], f"{benchmark}_violin.png")
    plt.savefig(save_path)
    plt.close()
    print(f"Violin plot saved to {save_path}")

def plot_cdf(benchmark, data, labels):
    """Creates a cumulative distribution function (CDF) plot for each configuration."""
    plt.figure(figsize=(10, 6))
    for exec_times, label in zip(data, labels):
        sorted_times = np.sort(exec_times)
        cdf = np.arange(1, len(sorted_times) + 1) / len(sorted_times)
        plt.plot(sorted_times, cdf, marker='.', linestyle='-', label=label)
    plt.title(f"CDF Plot of Execution Times for {benchmark}")
    plt.xlabel("Execution Time (ms)")
    plt.ylabel("Cumulative Probability")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    save_path = os.path.join(plot_types['cdf'], f"{benchmark}_cdf.png")
    plt.savefig(save_path)
    plt.close()
    print(f"CDF plot saved to {save_path}")

def main():
    # Discover benchmarks from the baseline directory.
    baseline_dir = os.path.join(base_dir, 'baseline')
    benchmarks_set = set()
    for f in os.listdir(baseline_dir):
        if f.endswith('_results.txt'):
            benchmarks_set.add(f[:-len("_results.txt")])
        elif f.endswith('_execution_time.txt'):
            benchmarks_set.add(f[:-len("_execution_time.txt")])
    benchmarks = sorted(list(benchmarks_set))
    
    if not benchmarks:
        print("No benchmark files found in the baseline directory.")
        return

    for benchmark in benchmarks:
        print(f"Processing benchmark: {benchmark}")
        data, labels = gather_benchmark_data(benchmark)
        if not data:
            print(f"No data available for benchmark: {benchmark}")
            continue
        plot_standard(benchmark, data, labels)
        plot_box(benchmark, data, labels)
        plot_violin(benchmark, data, labels)
        plot_cdf(benchmark, data, labels)

if __name__ == "__main__":
    main()
