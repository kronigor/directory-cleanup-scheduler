import os
import sys
import time
import traceback
import argparse
import rarfile
import shutil
import py7zr
import zipfile
import schedule
import logging
import warnings

from datetime import datetime
from glob import glob
from time import sleep
from OpenSSL import crypto


warnings.filterwarnings("ignore")


def resource_path(relative_path):
    """
    The function `resource_path` returns the absolute path of a resource file given its relative path.
    
    :param relative_path: The relative path is the path to a file or directory relative to the current
    working directory. It can be a string representing a file or directory name, or a path containing
    multiple directories separated by slashes ("/") or backslashes ("\")
    :return: The function `resource_path` returns the absolute path of a resource file by joining the
    base path with the relative path.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')

    return os.path.join(base_path, relative_path)


def del_files(file):
    """
    The function `del_files` attempts to delete a file and returns `True` if successful, otherwise it
    returns `False`.
    
    :param file: The parameter "file" is a string that represents the path to a file that you want to
    delete
    :return: a boolean value. If the file exists and is successfully deleted, it will return True. If
    there is an error or the file does not exist, it will return False.
    """
    try:
        if os.path.exists(file):
            os.remove(file)
            return True
    except:
        return False


def files_in_path(path, lst=None):
    """
    The function recursively finds all files in a given directory path.
    
    :param path: The `path` parameter is a string that represents the directory path for which you want
    to retrieve the list of files
    :param lst: The `lst` parameter is an optional parameter that allows you to pass in a pre-existing
    list of files. If `lst` is not provided, it defaults to `None` and a new empty set is created to
    store the list of files
    :return: a set of file paths within the specified directory and its subdirectories.
    """
    if lst is None:
        list_of_files = set()
    else:
        list_of_files = lst
    content = os.listdir(path)
    for i in content:
        if not os.path.isdir(path + '/' + i):
            list_of_files.add(path + '/' + i)
        else:
            files_in_path(path + '/' + i, list_of_files)
    return list_of_files


def check_zip(file, flag):
    """
    The function `check_zip` checks if a given zip file is valid and deletes it if it is not.
    
    :param file: The `file` parameter is the path to the zip file that you want to check
    :param flag: The "flag" parameter is a variable that is used to indicate the success or failure of
    the function. It is passed as an argument to the function and is updated within the function based
    on certain conditions or operations
    :return: the value of the flag variable.
    """
    try:
        with zipfile.ZipFile(file, 'r') as zf:
            zf.testzip()
        flag = del_files(file)
        return flag
    except:
        return flag


def check_rar(file, flag):
    """
    The function `check_rar` checks if a file is a RAR file, and if so, checks if it requires a password
    and deletes the file if it doesn't.
    
    :param file: The `file` parameter is the path to the RAR file that needs to be checked
    :param flag: The "flag" parameter is a boolean variable that is used to keep track of whether the
    file was successfully processed or not. It is initially passed as an argument to the function and
    its value can be either True or False
    :return: The variable `flag` is being returned.
    """
    if rarfile.is_rarfile(file):
        try:
            with rarfile.RarFile(file) as rf:
                if not rf.needs_password():
                    flag = del_files(file)
        except rarfile.NeedFirstVolume:
            part1 = f'{".".join(file.split(".")[:-2])}.part1.rar'
            if os.path.exists(part1):
                with rarfile.RarFile(part1) as rf:
                    if not rf.needs_password():
                        flag = del_files(file)
            else:
                flag = del_files(file)
    else:
        flag = del_files(file)
    return flag


def check_7z(file, flag):
    """
    The function `check_7z` checks if a 7z file requires a password and deletes the file if it does not.
    
    :param file: The `file` parameter is the path to the 7z file that needs to be checked
    :param flag: The "flag" parameter is a boolean variable that is used to keep track of whether the
    file needs to be deleted or not. It is initially set to True
    :return: the value of the `flag` variable.
    """
    try:
        with (py7zr.SevenZipFile(file, mode='r') as z7):
            if not z7.needs_password():
                flag = False
        if not flag:
            flag = del_files(file)
    except py7zr.exceptions.PasswordRequired:
        pass
    except:
        flag = del_files(file)
    return flag


def check_p7m(file, flag):
    """
    The function `check_p7m` checks if a given file is a valid PKCS7 file and returns a flag indicating
    whether the file should be deleted or not.
    
    :param file: The `file` parameter is the path to the file that needs to be checked. It should be a
    string representing the file path
    :param flag: The "flag" parameter is a variable that is used to keep track of whether any errors
    occurred during the execution of the function. It is initially passed as an argument to the function
    and its value can be modified within the function.
    :return: the variable "flag" is being returned.
    """
    with open(file, 'rb') as f:
        p7data = f.read()
    try:
        crypto.load_pkcs7_data(crypto.FILETYPE_ASN1, p7data)
    except Exception as e:
        print(e)
        flag = del_files(file)
    return flag


# Dictionary of functions for each file type
functions = {
    '.zip': check_zip,
    '.rar': check_rar,
    '.7z': check_7z,
    '.p7m': check_p7m
}


def check_files(lst_files, path, log, exclude):
    """
    The function `check_files` takes a list of files, a path, a log flag, a cleanup flag, and a list of
    file extensions to exclude, and performs various operations on the files based on their extensions.
    
    :param lst_files: A list of file names to be checked
    :param path: The `path` parameter is a string that represents the directory path where the files are
    located
    :param log: The "log" parameter is a boolean value that determines whether or not to log information
    about each file being checked. If set to True, the function will log information such as the
    filename and file extension. If set to False, no logging will occur
    :param exclude: The `exclude` parameter is a list of file extensions that should be excluded from
    the file checking process. If a file has an extension that matches any of the extensions in the
    `exclude` list, it will be skipped and not processed further
    :return: the result of two operations:
    """
    flag = True
    for file in lst_files:
        flag = True
        file_extension = os.path.splitext(file)[-1].lower()
        if log:
            logging.info(f'filename: {file}; ext: {file_extension}')
        if exclude and file_extension in exclude:
            continue
        elif file_extension in ('.zip', '.rar', '.7z', '.p7m'):
            if os.path.exists(file):
                flag = functions[file_extension](file, flag)
        else:
            flag = del_files(file)
    return files_in_path(path), flag


def cant_del(seconds, path, log, cleanup, exclude):
    """
    The function `cant_del` continuously checks for files in a given path and returns a list of old
    files that meet certain criteria.
    
    :param seconds: The number of seconds to wait between each iteration of the while loop
    :param path: The `path` parameter is a string that represents the directory path where the files are
    located
    :param log: The "log" parameter is a boolean value that determines whether or not to log the files
    that are checked. If set to True, the function will log the files that are checked. If set to False,
    no logging will occur
    :param cleanup: The "cleanup" parameter is a boolean value that determines whether or not to perform
    cleanup operations on the files in the specified path. If cleanup is set to True, the code will
    execute the cleanup operations. If cleanup is set to False, the code will not perform any cleanup
    operations
    :param exclude: The "exclude" parameter is a list of file names or patterns that should be excluded
    from the file checking process. These files will not be considered when determining if any files
    have been added or deleted in the specified path
    :return: the variable "lst_old".
    """
    flag = False
    while not flag:
        lst_new = files_in_path(path)
        lst_old, flag = check_files(lst_new, path, log, exclude)
        sleep(seconds)
        if cleanup:
            schedule.run_pending()
            time.sleep(1)
    return lst_old


def daily_cleanup(directory, hours, log):
    """
    The `daily_cleanup` function performs a cleanup of files and directories in a specified directory
    based on a given hour and logs the actions if specified.
    
    :param directory: The directory parameter is the path to the directory that you want to perform the
    cleanup on
    :param hours: The "hours" parameter is the hour of the day (in 24-hour format) after which the
    cleanup should be performed. If the current hour is greater than or equal to the specified hour, or
    if the current hour is between 0 and 6 (inclusive), the cleanup will be executed
    :param log: The "log" parameter is a boolean value that determines whether or not to log the actions
    performed during the cleanup process. If set to True, it will log the filenames and directories that
    are deleted. If set to False, it will not log anything
    :return: nothing (None).
    """
    path = os.path.abspath(directory) + '\\*'
    path = path.replace('\\', '/')
    now = datetime.now()
    if now.hour >= hours or 0 <= now.hour <= 6:
        files = glob(path)
        print(files)
        if files:
            for file in files:
                if os.path.isfile(file):
                    if log:
                        logging.info(f'filename: {file};')
                    del_files(file)
                else:
                    try:
                        if log:
                            logging.info(f'directory: {file};')
                        if os.path.exists(file):
                            shutil.rmtree(file)
                        else:
                            continue
                    except:
                        continue
    return


def check_directory(path, seconds, log, cleanup, exclude):
    """
    The function `check_directory` continuously checks a specified directory for changes in its files,
    logs any errors encountered, and performs cleanup operations if specified.
    
    :param path: The `path` parameter is the directory path that you want to check for changes
    :param seconds: The "seconds" parameter specifies the number of seconds to wait between each check
    of the directory
    :param log: The "log" parameter is a boolean value that determines whether or not to log the actions
    performed by the function. If set to True, the function will log the actions in a log file. If set
    to False, no logging will be done
    :param cleanup: The "cleanup" parameter is a boolean value that determines whether or not to perform
    cleanup operations on the directory. If set to True, the code will execute cleanup operations using
    the "schedule" module. If set to False, no cleanup operations will be performed
    :param exclude: The "exclude" parameter is used to specify a list of file names or patterns that
    should be excluded from the directory check. These files will not be considered when comparing the
    new and old file lists, and will not trigger any actions or logging
    :return: nothing.
    """
    try:
        while not os.path.exists(path):
            time.sleep(300)
        lst_old = None
        while True:
            if cleanup:
                schedule.run_pending()
                time.sleep(1)
            lst_new = files_in_path(path=path)
            if lst_new == lst_old:
                sleep(seconds)
            else:
                lst_old, flag = check_files(lst_files=lst_new, path=path, log=log, exclude=exclude)
                if not flag:
                    lst_old = cant_del(seconds=seconds, path=path, log=log, cleanup=cleanup, exclude=exclude)
                else:
                    sleep(seconds)
    except Exception:
        with open(resource_path('./errors.log'), 'a') as f:
            f.write('[Check]:\n')
            f.write('{}\n'.format(traceback.format_exc()))
        return


# Main
# The above code is a Python script that monitors and cleans a directory. It takes command line
# arguments to specify the directory path, timeout in seconds, hour after which the directory should
# be cleaned, whether to enable logging, whether to perform directory cleanup, and specific file
# extensions to exclude from processing.
if __name__ == "__main__":
    try:
        def parse_arguments():
            parser = argparse.ArgumentParser(description='Script to monitor and clean a directory.')
            parser.add_argument('-p', '--path', required=True, type=str, help='Directory path to monitor and clean.')
            parser.add_argument('-s', '--seconds', type=int, default=15,
                                help='Timeout in seconds after each check (default: '
                                     '15).')
            parser.add_argument('-t', '--time', type=int, default=22,
                                help='Hour after which the directory should be cleaned '
                                     '(24-hour format).')
            parser.add_argument('-l', '--log', action='store_true', default=False,
                                help='Enable logging during script execution. If set, the script logs the names and '
                                     'extensions of files located in the specified directory to the log.txt file.')

            parser.add_argument('-c', '--cleanup', action='store_true', default=False,
                                help='Perform directory cleanup at the specified time. If set, the script completely '
                                     'clears the specified directory.')

            parser.add_argument('-e', '--exclude', type=lambda x: [f".{str.strip(i)}" for i in x.split(',')],
                                help='Exclude specific file extensions from processing. If set, the script does not '
                                     'check files with extensions specified in this argument. The extensions should '
                                     'be provided as a comma-separated list without spaces.')
            return parser.parse_args()


        args = parse_arguments()

        while True:
            if args.cleanup:
                schedule.every().minute.do(daily_cleanup, directory=args.path, hours=args.time, log=args.log)
            if args.log:
                logging.basicConfig(level=logging.INFO, filename='log.txt', filemode='a')
                logging.info(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}]")
            check_directory(path=args.path, seconds=args.seconds, log=args.log, cleanup=args.cleanup, exclude=args.exclude)
    except Exception:
        with open(resource_path('./errors.log'), 'a') as f:
            f.write('[MAIN] :\n')
            f.write('{}\n'.format(traceback.format_exc()))
