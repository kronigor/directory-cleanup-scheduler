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

### Command-Line Arguments
- `-p`, `--path` (required): Path to the directory you want to monitor and clean.
- `-s`, `--seconds` (optional): Timeout in seconds after each directory check. Default is 15 seconds.
- `-t`,`--time` (optional): Hour after which the directory should be cleaned (24-hour format). This argument sets the time for the daily cleanup schedule. Default is 22:00.
- `-l`,`--log` (optional): Enable logging during script execution. If set, the script logs the names and extensions of files located in the specified directory to the log.txt file.
- `-c`,`--cleanup` (optional): Perform directory cleanup at the specified time. If set, the script completely clears the specified directory.
- `-e`,`--exclude` (optional): Exclude specific file extensions from processing. If set, the script does not check files with extensions specified in this argument. The extensions should be provided as a comma-separated list without spaces.
### Calling the Help Menu
To see all available command-line options and get general information about the script, use the `-h` or `--help` argument:
```
python CheckDir.py -h

python CheckDir.py --help
```

### Using with Python
To run the script with Python, use the following command:
```
python CheckDir.py -p <path to directory> [--additional parameters]
```

Example usage:
```
python CheckDir.py -p /path/to/directory 

python CheckDir.py -p /path/to/directory -s 30 -t 10 -c -l -e "pdf,docx"

python CheckDir.py --path /path/to/directory --seconds 30 --time 10 --exclude "pdf,docx" --cleanup --log 
```

### Using as an Executable
If you have a compiled `.exe` version of the script, you can run it directly from the command line without needing Python installed:
```
./CheckDir.exe -p <path to directory> [--additional parameters]
```

Example usage:
```
./CheckDir.exe -p /path/to/directory

./CheckDir.exe -p /path/to/directory -s 30 -t 10 -c -l -e "pdf,docx"

./CheckDir.exe --path /path/to/directory --seconds 30 --time 10 --exclude "pdf,docx" --cleanup --log
```

## License
This project is licensed under the GNU General Public License (GPL).
