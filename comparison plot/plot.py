import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib as mpl

# Increase global font size for better legibility
mpl.rcParams.update({'font.size': 14})

def process_file(filename):
    # Read the file using whitespace as delimiter and skip the header line
    df = pd.read_csv(filename, delim_whitespace=True, skiprows=1, header=None, 
                     names=['Index', 'Time', 'ImageSize'])
    # Group by image size and compute the average boot time
    grouped = df.groupby('ImageSize')['Time'].mean().reset_index()
    return grouped

def process_file_stats(filename):
    # Read the file using whitespace as delimiter and skip the header line
    df = pd.read_csv(filename, delim_whitespace=True, skiprows=1, header=None, 
                     names=['Index', 'Time', 'ImageSize'])
    # Group by image size and compute both the average boot time and its standard deviation
    grouped = df.groupby('ImageSize')['Time'].agg(['mean', 'std']).reset_index()
    return grouped

# ---------------------------
# First Plot: Averages Only
# ---------------------------
apu_data = process_file("useful_APU_times.txt")
rpu_data = process_file("useful_RPU_times.txt")

plt.figure(figsize=(10, 6))
plt.plot(apu_data['ImageSize'], apu_data['Time'], marker='o', linestyle='-', color='blue', label='APU')
plt.plot(rpu_data['ImageSize'], rpu_data['Time'], marker='s', linestyle='-', color='orange', label='RPU')

plt.xlabel('Image Size (MB)')
plt.ylabel('Average Boot Time (ms)')
plt.title('Jailhouse Partition Creation Times Comparison: APU vs RPU')
plt.legend()
plt.grid(True)

# Set x-axis limits and ticks
plt.xlim(left=0, right=91)
plt.xticks([1, 10, 20, 30, 40, 50, 60, 70, 80, 90])

# Set y-axis ticks every 20 ms
ax = plt.gca()
ax.yaxis.set_major_locator(ticker.MultipleLocator(20))

plt.tight_layout()
plt.savefig("boot_times_comparison.png")
plt.close()

# ------------------------------------------------------------
# Second Plot: Averages with Confidence Intervals (Std Dev)
# ------------------------------------------------------------
apu_stats = process_file_stats("useful_APU_times.txt")
rpu_stats = process_file_stats("useful_RPU_times.txt")

plt.figure(figsize=(10, 6))
plt.errorbar(apu_stats['ImageSize'], apu_stats['mean'], yerr=apu_stats['std'],
             fmt='o-', color='blue', capsize=5, label='APU')
plt.errorbar(rpu_stats['ImageSize'], rpu_stats['mean'], yerr=rpu_stats['std'],
             fmt='s-', color='orange', capsize=5, label='RPU')

plt.xlabel('Image Size (MB)')
plt.ylabel('Boot Time (ms)')
plt.title('Jailhouse Partition Creation Times: APU vs RPU')
plt.legend()
plt.grid(True)

# Set x-axis limits and ticks
plt.xlim(left=0, right=91)
plt.xticks([1, 10, 20, 30, 40, 50, 60, 70, 80, 90])

# Use y-axis ticks every 20 ms (adjust as needed for your data range)
ax = plt.gca()
ax.yaxis.set_major_locator(ticker.MultipleLocator(20))

plt.tight_layout()
plt.savefig("boot_times_comparison_with_confidence.png")
plt.close()
