# This is really just useful if the test fails for some reason, you have to know which rate the previous test stopped at (count them)
# and then plugin in output_dir...
import os
import subprocess
import sys
import json

# Update this line based on file output of progressive-slam.py
output_dir="results_20250114_094019"

# Count the total results*.bin using: ls <output_dir> | grep -c 'results*.bin' and replace the range(<count>).
# Log-spaced rates (each ca. +25% (+1dB) of the previous, covering 1/sec to 100k/sec)
rates = [10.0 ** (i / 10.0) for i in range(30)]

# Log-spaced buckets (each ca. +25% (+1dB) of the previous, covering <1us to >10s)
buckets = [0] + [1e3 * 10.0 ** (i / 10.0) for i in range(71)]

# Run vegeta report, and extract data for gnuplot
latency_path = os.path.join(output_dir, 'results_latency.txt')
success_path = os.path.join(output_dir, 'results_success.txt')

with open(latency_path, 'w') as out_latency, open(success_path, 'w') as out_success:
    for rate in rates:
        cmd = f"vegeta report -type=json -buckets '[%s]' {os.path.join(output_dir, f'results_{int(1000*rate)}.bin')}" \
              % ",".join(f"{int(bucket)}ns" for bucket in buckets)
        print(cmd, file=sys.stderr)
        result = json.loads(subprocess.check_output(cmd, shell=True))

        # (Request rate, Response latency) -> (Fraction of responses)
        for latency, count in result['buckets'].items():
            latency_nsec = float(latency)
            fraction = count / sum(result['buckets'].values()) * result['success']
            print(rate, latency_nsec, fraction, file=out_latency)
        print(file=out_latency)

        # (Request rate) -> (Success rate)
        print(rate, result['success'], file=out_success)

print(f"# wrote {latency_path} and {success_path}", file=sys.stderr)

# Visualize with gnuplot (PNG)
png_output = os.path.join(output_dir, 'result.png')
plot_cmd = f'gnuplot -e "set term png size 1280, 800; DIR=\'{output_dir}\'" progressive-slam.plt > {png_output}'
print(plot_cmd, file=sys.stderr)
subprocess.run(plot_cmd, shell=True)

# Visualize with gnuplot (default, likely a UI)
persist_cmd = f"gnuplot -e \"DIR='{output_dir}'\" -persist progressive-slam.plt"
print(persist_cmd, file=sys.stderr)
subprocess.run(persist_cmd, shell=True)

print(f"All files are saved in {output_dir}", file=sys.stderr)