# Directory Cleanup Scheduler

## Description
`CheckDir` is a Python script designed for automated cleaning and managing files in a specified directory. It facilitates flexible file management, automatically deleting inappropriate files based on set parameters.

### Key Features
- Command-line Argument Parsing for Flexible Configuration.
- Operating System Level Operations.
- Support for Various Archive Formats (.zip, .7z, .rar).
- Support .p7m files.
- Scheduled Tasks for Periodic Execution.

## Installation
Ensure you have Python version 3.x installed. To install necessary dependencies, use the provided `requirements.txt`:
```
pip install -r requirements.txt
```

## Usage

### Using with Python
To run the script with Python, use the following command:
```
python CheckDir.py -p <path to directory> [--additional parameters]
```

Example usage:
```
python CheckDir.py -p /path/to/directory 

python CheckDir.py -p /path/to/directory -s 30 -t 10

python CheckDir.py --path /path/to/directory --seconds 30 --time 10
```

### Using as an Executable
If you have a compiled `.exe` version of the script, you can run it directly from the command line without needing Python installed:
```
./CheckDir.exe -p <path to directory> [--additional parameters]
```

Example usage:
```
./CheckDir.exe -p /path/to/directory

./CheckDir.exe -p /path/to/directory -s 30 -t 10

./CheckDir.exe --path /path/to/directory --seconds 30 --time 10
```

## License
This project is licensed under the GNU General Public License (GPL).
