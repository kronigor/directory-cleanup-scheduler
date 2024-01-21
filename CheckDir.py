import os
import time
import traceback
import argparse
import rarfile
import shutil
import py7zr
import zipfile
import schedule

from datetime import datetime
from glob import glob
from time import sleep
from OpenSSL import crypto


def del_files(file):
    """Deletes a file at the given path."""
    try:
        if os.path.exists(file):
            os.remove(file)
            return True
    except:
        return False


def files_in_path(path, lst=None):
    """Gets a list of files in the specified directory. Returns a list of files."""
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


def lst_compare(lst_new, lst_old):
    """Compares two lists of files. Returns the result of the comparison."""
    return lst_new == lst_old


def check_zip(file, flag):
    """Checks zip archives. If the file is not a zip archive or is not password-protected, it's deleted."""
    try:
        with zipfile.ZipFile(file, 'r') as zf:
            zf.testzip()
        flag = del_files(file)
        return flag
    except:
        return flag


def check_rar(file, flag):
    """Checks rar archives. If the file is not a rar archive or is not password-protected, it's deleted."""
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
    """Checks 7z archives. If the file is not a 7z archive or is not password-protected, it's deleted."""
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
    """Checks encrypted p7m files. If the file is not a p7m file, it's deleted."""
    with open(file, 'rb') as f:
        p7data = f.read()
    try:
        crypto.load_pkcs7_data(crypto.FILETYPE_ASN1, p7data)
    except:
        flag = del_files(file)
    return flag


# Dictionary of functions for each file type
functions = {
    '.zip': check_zip,
    '.rar': check_rar,
    '.7z': check_7z,
    '.p7m': check_p7m
}


def check_files(lst_files, path):
    """Takes a list of file paths as input and checks the files according to their type."""
    flag = True
    for file in lst_files:
        flag = True
        file_extension = os.path.splitext(file)[-1].lower()
        if file_extension in ('.zip', '.rar', '.7z', '.p7m'):
            if os.path.exists(file):
                flag = functions[file_extension](file, flag)
        else:
            flag = del_files(file)
    return files_in_path(path), flag


def cant_del(seconds, path):
    """If the del_files function fails to delete files, cant_del attempts to delete them."""
    flag = False
    while not flag:
        lst_new = files_in_path(path)
        lst_old, flag = check_files(lst_new, path)
        sleep(seconds)
        schedule.run_pending()
        time.sleep(1)
    return lst_old


def daily_cleanup(directory, hours):
    """Completely cleans the directory."""
    path = os.path.abspath(directory) + '\\*'
    path = path.replace('\\', '/')
    now = datetime.now()
    if now.hour >= hours or 0 <= now.hour <= 6:
        files = glob(path)
        if files:
            for file in files:
                if os.path.isfile(file):
                    del_files(file)
                else:
                    try:
                        if os.path.exists(file):
                            shutil.rmtree(file)
                    except:
                        continue
    return


def check_directory(path, seconds):
    """Main function for checking the specified directory. Executes all other functions."""
    try:
        while not os.path.exists(path):
            time.sleep(300)
        lst_old = None
        while True:
            schedule.run_pending()
            time.sleep(1)
            lst_new = files_in_path(path=path)
            result_compare = lst_compare(lst_new=lst_new, lst_old=lst_old)
            if result_compare:
                sleep(seconds)
            else:
                lst_old, flag = check_files(lst_files=lst_new, path=path)
                if not flag:
                    lst_old = cant_del(seconds=seconds, path=path)
                else:
                    sleep(seconds)
    except Exception:
        with open('./errors.log', 'a') as f:
            f.write('[Check]:\n')
            f.write('{}\n'.format(traceback.format_exc()))
        return


# Main
if __name__ == "__main__":
    try:
        def parse_arguments():
            """ Parse command line arguments. """
            parser = argparse.ArgumentParser(description='Script to monitor and clean a directory.')
            parser.add_argument('-p', '--path', required=True, type=str, help='Directory path to monitor and clean.')
            parser.add_argument('-s', '--seconds', type=int, default=15,
                                help='Timeout in seconds after each check (default: '
                                     '15).')
            parser.add_argument('-t', '--time', type=int, default=22,
                                help='Hour after which the directory should be cleaned '
                                     '(24-hour format).')

            return parser.parse_args()


        args = parse_arguments()

        while True:
            schedule.every().hour.do(daily_cleanup, directory=args.path, hours=args.time)
            check_directory(path=args.path, seconds=args.seconds)
    except Exception:
        with open('./errors.log', 'a') as f:
            f.write('[MAIN] :\n')
            f.write('{}\n'.format(traceback.format_exc()))
