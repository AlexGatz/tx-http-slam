#!/usr/bin/env python3

import json
import os
import subprocess
import sys
import time
from datetime import datetime
import socket

if '-h' in sys.argv or '--help' in sys.argv:
    print('usage:', file=sys.stderr)
    print('python3 progressive-slam.py (Use a body.json file as well as a targets.txt with this format: POST http://localhost:8080/)', file=sys.stderr)
    sys.exit(1)

# Check for necessary files
targets_file = "targets.txt"

if not os.path.exists(targets_file):
    print(f"Error: {targets_file} is missing.", file=sys.stderr)
    sys.exit(1)

# Create output directory
hostname = socket.gethostname()
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_dir = f"results_{timestamp}"
os.makedirs(output_dir, exist_ok=True)

# Log-spaced rates (each ca. +25% (+1dB) of the previous, covering 1/sec to 100k/sec)
rates = [10.0 ** (i / 10.0) for i in range(50)]

# Log-spaced buckets (each ca. +25% (+1dB) of the previous, covering <1us to >10s)
buckets = [0] + [1e3 * 10.0 ** (i / 10.0) for i in range(71)]

# Run vegeta attack
for rate in rates:
    filename = f"results_{int(1000*rate)}.bin"
    filepath = os.path.join(output_dir, filename)
    if not os.path.exists(filepath):
        cmd = f"vegeta attack -duration 5s -rate {int(1000*rate)}/1000s -targets {targets_file} -output {filepath}"
        print(cmd, file=sys.stderr)
        subprocess.run(cmd, shell=True)
        time.sleep(5)

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
cmd = f"gnuplot -e \"set term png size 1280, 800\" progressive-slam.plt > {png_output}"
print(cmd, file=sys.stderr)
subprocess.run(cmd, shell=True)

# Visualize with gnuplot (default, likely a UI)
cmd = "gnuplot -persist ramp-requests.plt"
print(cmd, file=sys.stderr)
subprocess.run(cmd, shell=True)

print(f"All files are saved in {output_dir}", file=sys.stderr)
