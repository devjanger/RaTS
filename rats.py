
import getopt
import random
import re
import string
import sys

from colorama import init, Fore, Style, deinit

from config import config
from config.config import HELP
from config.config_utils import read_config_file
from misc import utils
from misc.notify import MailSender
from misc.utils import check_compile_sigs, load_ransomware_exts
from scanners.scanner import Scanner
from scanners.scanner_for_crypt import ScannerForCrypt
from scanners.scanner_for_file import ScannerForFile


def main(argv):
    """
    The main method
    :param argv:
    :return:
    """

    inputdir = ""
    input_file = ""
    extfilesxd = ""
    dirs_exclude = ""
    files_exclude = ""
    dirs_include = ""
    outputcsv_prefix = ""
    dst_email = ""
    config_file_path = None
    ana_type = "all"  # default is to do Manifest and Crypto checks
    recursive = False
    verbose = False
    crypto_type = 'all'
    anonymize = False

    init()

    output_start = Fore.RED + config.RATS_LOGO + \
                   "\n" + Fore.BLUE + config.RATS_NAME + ' - v. ' + config.RATS_VERSION
    usage_sample = Fore.CYAN + HELP

    print(Style.RESET_ALL)
    print(output_start + Fore.YELLOW + "\nHere we are!\n")

    try:
        opts, args = getopt.getopt(argv, "hkmrvai:x:o:e:l:c:f:t:z:q:")
    except getopt.GetoptError as error:
        print('************ arguments error ************', end='\n')
        print(f'error: {str(error)}')
        print(usage_sample)
        sys.exit(2)

    print(Fore.LIGHTCYAN_EX + "---***--- Cmd line args ---***---" + Fore.RESET)

    # TODO check the existence of the argument
    for opt, arg in opts:
        if opt == '-h':
            print('************ help ************', end='\n')
            print(usage_sample)
            sys.exit()
        elif opt == '-k':
            ana_type = 'k'
            print(Fore.LIGHTCYAN_EX + "-k" + Fore.RESET)
        elif opt == '-t':
            crypto_type = arg
            print(Fore.LIGHTCYAN_EX + f"-t {arg}" + Fore.RESET)
        elif opt == '-m':
            ana_type = 'm'
            print(Fore.LIGHTCYAN_EX + "-m" + Fore.RESET)
        elif opt == '-v':
            verbose = True
            print(Fore.LIGHTCYAN_EX + "-v" + Fore.RESET)
        elif opt == '-r':
            recursive = True
            print(Fore.LIGHTCYAN_EX + "-r" + Fore.RESET)
        elif opt == "-a":
            anonymize = True
            print(Fore.LIGHTCYAN_EX + f"-a" + Fore.RESET)
        elif opt == "-i":
            inputdir = arg
            print(Fore.LIGHTCYAN_EX + f"-i {arg}" + Fore.RESET)
        elif opt == "-f":
            input_file = arg
            print(Fore.LIGHTCYAN_EX + f"-f {arg}" + Fore.RESET)
        elif opt == "-x":
            extfilesxd = arg
            print(Fore.LIGHTCYAN_EX + f"-x {arg}" + Fore.RESET)
        elif opt == "-z":
            dirs_exclude = arg
            print(Fore.LIGHTCYAN_EX + f"-z {arg}" + Fore.RESET)
        elif opt == "-q":
            files_exclude = arg
            print(Fore.LIGHTCYAN_EX + f"-q {arg}" + Fore.RESET)
        elif opt == "-l":
            dirs_include = arg
            print(Fore.LIGHTCYAN_EX + f"-l {arg}" + Fore.RESET)
        elif opt == "-o":
            outputcsv_prefix = arg
            print(Fore.LIGHTCYAN_EX + f"-o {arg}" + Fore.RESET)
        elif opt == "-e":
            dst_email = arg
            print(Fore.LIGHTCYAN_EX + f"-e {arg}" + Fore.RESET)
        elif opt == "-c":
            config_file_path = arg
            print(Fore.LIGHTCYAN_EX + f"-c {arg}" + Fore.RESET)

    d = {'k': 'crypto', 'm': 'manifest'}

    if (inputdir or dirs_include or files_exclude) and ana_type:

        # read the config file if it was specified
        if config_file_path is not None:
            read_config_file(config_file_path)

        # some cmd line parameters are passed to config to better manage them
        config.EXT_FILES_LIST_TO_EXCLUDE = set([x.strip() for x in extfilesxd.lower().split(sep=',')])

        # organize the directories to process: main dir or list of dirs
        dirs_to_process = list()
        if dirs_include:
            dirs_to_process = process_dir_file(dirs_include)
        elif inputdir:
            dirs_to_process.append(inputdir)

        # read the list of dirs to exclude
        dirs_to_exclude = list()
        if dirs_exclude:
            dirs_to_exclude = process_dir_file(dirs_exclude)  

        # read the list of files to exclude
        files_to_exclude_list=list()
        if files_exclude:
            files_to_exclude_list = exclude_files(files_exclude)

        # load the signatures for file magic byte
        config.signatures = check_compile_sigs()
        # load the extension for ransomware files
        load_ransomware_exts()

        try:
            if ana_type == "all":
                process_dirs(dirs_to_process,
                             dirs_to_exclude,
                             files_to_exclude_list,
                             outputcsv_prefix + "-manifest@", 'm',
                             crypto_type=crypto_type,
                             email=dst_email,
                             verbose=verbose,
                             recursive=recursive,
                             anonymize=anonymize)
                process_dirs(dirs_to_process,
                             dirs_to_exclude,
                             files_to_exclude_list,
                             outputcsv_prefix + "-crypto@", 'k',
                             crypto_type=crypto_type,
                             email=dst_email,
                             verbose=verbose,
                             recursive=recursive,
                             anonymize=anonymize)
            else:
                process_dirs(dirs_to_process,
                             dirs_to_exclude,
                             files_to_exclude_list,
                             outputcsv_prefix + "-" + d[ana_type] + "@", ana_type,
                             crypto_type=crypto_type,
                             email=dst_email,
                             verbose=verbose,
                             recursive=recursive,
                             anonymize=anonymize)
        except FileNotFoundError as e:
            msg = f'EEE (MainScanDir) => FileNotFound error: {e}'
            print(msg)

    elif input_file and ana_type:
        print(output_start + Fore.YELLOW + "\nHere we are!\n")

        # read the config file if it was specified
        if config_file_path is not None:
            read_config_file(config_file_path)

        # load the signatures for file magic byte
        config.signatures = check_compile_sigs()
        # load the extension for ransomware files
        load_ransomware_exts()

        if ana_type == "all":
            process_file(input_file, 'm', crypto_type=crypto_type, verbose=verbose)
            process_file(input_file, 'k', crypto_type=crypto_type, verbose=verbose)
        else:
            process_file(input_file, ana_type, crypto_type=crypto_type, verbose=verbose)

    else:
        print(usage_sample)

    deinit()


def process_dir_file(dirlistfile):
    """
    Processes a file that contains a list of directories

    :param dirlistfile:
    :return:
    """
    with open(dirlistfile, 'r') as handle:
        content = handle.read()
        dirs_to_process = content.split(sep='\n')
        dirs_to_process = [dir.strip() for dir in dirs_to_process if dir and dir.strip()[0] != '#']
    return dirs_to_process


def exclude_files(files_to_exclude_file):

    """
    Processes a file that contains a list of files

    :param files_to_exclude_file:
    :return:
    """
    with open(files_to_exclude_file, 'r') as handle:
        content = handle.read()
        files_to_exclude_list = content.split(sep='\n')
        files_to_exclude_list =  [file.strip() for file in files_to_exclude_list if file and file.strip()[0] != '#'] 
    return files_to_exclude_list

def process_file(file, ana_type, crypto_type, verbose=False):
    """
    Process a file
    """
    s = None
    if ana_type == 'm':
        s = ScannerForFile(verbose=verbose)
    if ana_type == 'k':
        s = ScannerForCrypt(rand_test=crypto_type, verbose=verbose)

    print()
    print(f'{Fore.LIGHTCYAN_EX}{Scanner.sep} Found items {Scanner.sep}{Fore.RESET}')
    print(s.file(file))


def process_dirs(dirs_to_process, dirs_to_exclude, files_to_exclude_list, prefix_output_file, ana_type, crypto_type, email, verbose=False,
                 recursive=False, anonymize=False):
    def rand_str(n):
        return ''.join([random.choice(string.ascii_lowercase) for _ in range(n)])

    path = re.sub(r"\W+", '_', dirs_to_process[0][0:64], flags=re.IGNORECASE)
    # filename = f'{path}.t_{round(t.secs)}s.rnd_{rand_str(4)}.csv'
    filename = f'{path}.rnd_{rand_str(4)}.csv'
    output_file = f'{prefix_output_file}{filename}'

    print(f'{Fore.LIGHTCYAN_EX}Open CSV file for write outcome: {output_file}{Fore.RESET}')

    scanner = None
    if ana_type == 'm':
        scanner = ScannerForFile(output_file, verbose, anonymize=anonymize)
    if ana_type == 'k':
        scanner = ScannerForCrypt(csv_path=output_file, rand_test=crypto_type, verbose=verbose, anonymize=anonymize)

    with utils.Timer(verbose=True):
        if scanner:
            for inputdir in dirs_to_process:
                # TODO: is it possible to insert here multiprocessing?
                scanner.search(inputdir, dirs_to_exclude, files_to_exclude_list, recursive=recursive)
            scanner.close_csv_handle()
            print(f'{Fore.LIGHTCYAN_EX}Closed CSV file for write outcome: {output_file}{Fore.RESET}')

    if email:
        from_part = config.CFG_SMTP_USER
        to_part = email
        ms = MailSender()
        subject = config.RATS_NAME + f": notify for {'manifest' if ana_type == 'm' else 'crypto'} processing: {filename}"
        print(f"{subject}, sent to: '{to_part}'")
        ms.send_email(from_part, to_part, subject, scanner.read_csv_content(), filename)


if __name__ == "__main__":
    main(sys.argv[1:])
