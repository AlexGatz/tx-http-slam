# Progressive HTTP Load Testing with Vegeta

progressive-slam.py is a Python script for HTTP load testing using Vegeta. It automates sending http requests at increasing rates, collects performance data, and generates visualizations.

The repo is simply a modified version of [this](https://github.com/tsenart/vegeta/tree/master/scripts).

## Features

- Customizable Targets: Define HTTP requests, headers, and payloads in a targets.txt file.
- Metrics Collection: Logs latency and success rates at varying request rates.
- Results Visualization: Creates visual performance plots using Gnuplot.
- Organized Outputs: Saves results in timestamped directories.

## Requirements

- Python 3.x
- [Vegeta](https://github.com/tsenart/vegeta)
- [Gnuplot](http://www.gnuplot.info/)

## Usage
1. Prepare the target.txt (provide 1 target at a time for accurate plots)
    ```
    POST http://localhost:8080/
    Content-Type: application/json
    @path/to/body.json
    ```
    *Note: Because of the way the script is currently setup to run leveraging vegeta's target files which will test many targets at once, the result data is aggregated across all targets provided. I've not reviewed the documentation yet to see if you can generate a report per target, if so that would be ideal.*\

2. Run the script
`python3 progressive-slam.py`

3. When the script completes it will call gnuplot and show you the results. The .png will be avaiable in each results file.