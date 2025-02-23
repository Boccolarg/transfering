import os
import re
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Define the two solutions and their corresponding base directories.
solutions = {
    "Preempt-RT": "../Preempt-RT-containers",
    "ZIC-APU": "../ZIC-APU"
}

# Configurations tested for each solution.
configurations = ['baseline', 'cpu8', 'fork8', 'memcpy8', 'open8', 'udp8']

# Base directory to save the benchmark comparison plots.
compare_plots_base = os.path.abspath("../compare_plots")

# Create separate directories for each plot type.
plot_types = {
    'standard': os.path.join(compare_plots_base, 'standard_plots'),
    'box': os.path.join(compare_plots_base, 'box_plots'),
    'violin': os.path.join(compare_plots_base, 'violin_plots'),
    'cdf': os.path.join(compare_plots_base, 'cdf_plots'),
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
            # Check if line ends with "ns" (nanoseconds)
            ns_match = re.match(r'^([0-9]*\.?[0-9]+)\s*ns$', line)
            if ns_match:
                try:
                    ns_val = float(ns_match.group(1))
                    ms_val = ns_val / 1e6  # convert ns to ms
                    execution_times.append(ms_val)
                    continue
                except Exception as conv_err:
                    print(f"Error converting line '{line}' in {file_path}: {conv_err}")
            # Otherwise, assume the value is in seconds.
            try:
                sec_val = float(line)
                ms_val = sec_val * 1000  # convert seconds to ms
                execution_times.append(ms_val)
            except Exception as conv_err:
                print(f"Error processing line '{line}' in {file_path}: {conv_err}")
        return execution_times
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def find_benchmark_files(solution_dir, configuration):
    """
    Returns a dictionary mapping benchmark names to file paths for a given
    solution's configuration directory. It looks for files ending with either
    '_results.txt' or '_execution_time.txt'.
    """
    benchmark_files = {}
    config_dir = os.path.join(solution_dir, configuration)
    if not os.path.isdir(config_dir):
        return benchmark_files
    for f in os.listdir(config_dir):
        if f.endswith('_results.txt'):
            benchmark = f[:-len('_results.txt')]
            benchmark_files[benchmark] = os.path.join(config_dir, f)
        elif f.endswith('_execution_time.txt'):
            benchmark = f[:-len('_execution_time.txt')]
            if benchmark not in benchmark_files:
                benchmark_files[benchmark] = os.path.join(config_dir, f)
    return benchmark_files

# ------------------------------------------------------------------
# First, build a data structure organized as:
# data[solution][configuration][benchmark] = execution_times (list)
# ------------------------------------------------------------------
data = {}
for sol_name, sol_dir in solutions.items():
    data[sol_name] = {}
    for config in configurations:
        bench_files = find_benchmark_files(sol_dir, config)
        data[sol_name][config] = {}
        for bench, file_path in bench_files.items():
            exec_times = read_execution_times(file_path)
            if exec_times:
                data[sol_name][config][bench] = exec_times
            else:
                print(f"No valid data in {file_path}")

# ------------------------------------------------------------------
# Rearrange data to be organized by benchmark.
# bench_data[benchmark][configuration][solution] = execution_times
# ------------------------------------------------------------------
bench_data = {}
for sol_name in solutions.keys():
    for config in configurations:
        for bench, exec_times in data[sol_name][config].items():
            bench_data.setdefault(bench, {}).setdefault(config, {})[sol_name] = exec_times

# ------------------------------------------------------------------
# Now define plotting functions for each plot type for a given benchmark.
# In every figure, each row corresponds to one configuration.
# In each subplot the two solutions (if available) are plotted.
# ------------------------------------------------------------------

def plot_standard_benchmark(benchmark, bench_data):
    nrows = len(configurations)
    fig, axes = plt.subplots(nrows, 1, figsize=(10, nrows * 3), sharex=False)
    if nrows == 1:
        axes = [axes]
    for idx, config in enumerate(configurations):
        ax = axes[idx]
        config_data = bench_data.get(benchmark, {}).get(config, {})
        if not config_data:
            ax.text(0.5, 0.5, f"No data for {config}", horizontalalignment='center',
                    verticalalignment='center', transform=ax.transAxes)
            ax.set_title(f"Configuration: {config}")
            continue
        for sol_name in solutions.keys():
            exec_times = config_data.get(sol_name)
            if exec_times:
                ax.plot(range(len(exec_times)), exec_times, marker='o', linestyle='-', label=sol_name)
            else:
                ax.text(0.5, 0.5, f"{sol_name} missing", horizontalalignment='center',
                        verticalalignment='center', transform=ax.transAxes)
        ax.set_title(f"Configuration: {config}")
        ax.set_xlabel("Sample Index")
        ax.set_ylabel("Execution Time (ms)")
        ax.grid(True)
        ax.legend(fontsize='small', loc='best')
    fig.suptitle(f"Standard Plot for Benchmark: {benchmark}", fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save_path = os.path.join(plot_types['standard'], f"{benchmark}_standard.png")
    plt.savefig(save_path)
    plt.close()
    print(f"Standard plot for benchmark '{benchmark}' saved to {save_path}")

def plot_box_benchmark(benchmark, bench_data):
    nrows = len(configurations)
    fig, axes = plt.subplots(nrows, 1, figsize=(10, nrows * 3), sharey=True)
    if nrows == 1:
        axes = [axes]
    for idx, config in enumerate(configurations):
        ax = axes[idx]
        config_data = bench_data.get(benchmark, {}).get(config, {})
        if not config_data:
            ax.text(0.5, 0.5, f"No data for {config}", horizontalalignment='center',
                    verticalalignment='center', transform=ax.transAxes)
            ax.set_title(f"Configuration: {config}")
            continue
        # Prepare data for boxplot: one box for each solution
        box_data = []
        labels = []
        for sol_name in solutions.keys():
            exec_times = config_data.get(sol_name)
            if exec_times:
                box_data.append(exec_times)
                labels.append(sol_name)
        if box_data:
            ax.boxplot(box_data, labels=labels)
        ax.set_title(f"Configuration: {config}")
        ax.set_xlabel("Solution")
        ax.set_ylabel("Execution Time (ms)")
        ax.grid(True)
    fig.suptitle(f"Box Plot for Benchmark: {benchmark}", fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save_path = os.path.join(plot_types['box'], f"{benchmark}_box.png")
    plt.savefig(save_path)
    plt.close()
    print(f"Box plot for benchmark '{benchmark}' saved to {save_path}")

def plot_violin_benchmark(benchmark, bench_data):
    nrows = len(configurations)
    fig, axes = plt.subplots(nrows, 1, figsize=(10, nrows * 3), sharey=True)
    if nrows == 1:
        axes = [axes]
    for idx, config in enumerate(configurations):
        ax = axes[idx]
        config_data = bench_data.get(benchmark, {}).get(config, {})
        if not config_data:
            ax.text(0.5, 0.5, f"No data for {config}", horizontalalignment='center',
                    verticalalignment='center', transform=ax.transAxes)
            ax.set_title(f"Configuration: {config}")
            continue
        # Prepare data for a violin plot: one violin for each solution
        violin_data = []
        positions = []
        labels = []
        pos = 1
        for sol_name in solutions.keys():
            exec_times = config_data.get(sol_name)
            if exec_times:
                violin_data.append(exec_times)
                positions.append(pos)
                labels.append(sol_name)
                pos += 1
        if violin_data:
            parts = ax.violinplot(violin_data, positions=positions, showmeans=False, showmedians=True)
            ax.set_xticks(positions)
            ax.set_xticklabels(labels, rotation=45, fontsize=9)
        ax.set_title(f"Configuration: {config}")
        ax.set_xlabel("Solution")
        ax.set_ylabel("Execution Time (ms)")
        ax.grid(True)
    fig.suptitle(f"Violin Plot for Benchmark: {benchmark}", fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save_path = os.path.join(plot_types['violin'], f"{benchmark}_violin.png")
    plt.savefig(save_path)
    plt.close()
    print(f"Violin plot for benchmark '{benchmark}' saved to {save_path}")

def plot_cdf_benchmark(benchmark, bench_data):
    nrows = len(configurations)
    fig, axes = plt.subplots(nrows, 1, figsize=(10, nrows * 3), sharex=False)
    if nrows == 1:
        axes = [axes]
    for idx, config in enumerate(configurations):
        ax = axes[idx]
        config_data = bench_data.get(benchmark, {}).get(config, {})
        if not config_data:
            ax.text(0.5, 0.5, f"No data for {config}", horizontalalignment='center',
                    verticalalignment='center', transform=ax.transAxes)
            ax.set_title(f"Configuration: {config}")
            continue
        for sol_name in solutions.keys():
            exec_times = config_data.get(sol_name)
            if exec_times:
                sorted_times = np.sort(exec_times)
                cdf = np.arange(1, len(sorted_times) + 1) / len(sorted_times)
                ax.plot(sorted_times, cdf, marker='.', linestyle='-', label=sol_name)
            else:
                ax.text(0.5, 0.5, f"{sol_name} missing", horizontalalignment='center',
                        verticalalignment='center', transform=ax.transAxes)
        ax.set_title(f"Configuration: {config}")
        ax.set_xlabel("Execution Time (ms)")
        ax.set_ylabel("Cumulative Probability")
        ax.grid(True)
        ax.legend(fontsize='small', loc='best')
    fig.suptitle(f"CDF Plot for Benchmark: {benchmark}", fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save_path = os.path.join(plot_types['cdf'], f"{benchmark}_cdf.png")
    plt.savefig(save_path)
    plt.close()
    print(f"CDF plot for benchmark '{benchmark}' saved to {save_path}")

# ------------------------------------------------------------------
# Main loop: For every benchmark in bench_data, create one figure per plot type.
# ------------------------------------------------------------------
def main():
    for benchmark in sorted(bench_data.keys()):
        print(f"Creating plots for benchmark: {benchmark}")
        plot_standard_benchmark(benchmark, bench_data)
        plot_box_benchmark(benchmark, bench_data)
        plot_violin_benchmark(benchmark, bench_data)
        plot_cdf_benchmark(benchmark, bench_data)

if __name__ == "__main__":
    main()
