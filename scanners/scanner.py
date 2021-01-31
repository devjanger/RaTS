# -*- coding: utf-8 -*-

import abc
import os
from pathlib import Path
from colorama import Fore

from logic.csv_row import CsvRow


class Scanner(metaclass=abc.ABCMeta):
    """
    The search abstract main class
    """

    sep = '---***---'

    def __init__(self, verbose=False):
        """
        Initialization of the fields
        :return:
        """
        self.found = []
        self.verbose = verbose

    @abc.abstractmethod
    def print_config(self):
        """
        Print the values of the configuration
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def file(self, path: str):
        """
        The main search method: process a file

        :param path:
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _process_a_file(self, file: os.DirEntry):
        raise NotImplementedError

    @abc.abstractmethod
    def search(self, path, recursive=True):
        """
        The main search method: process a directory

        :param path:
        :param recursive:
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _search(self, path, recursive=True):
        """
        The main recursive Search method
        :param path:
        :param recursive:
        :return:
        """
        raise NotImplementedError

    def _internal_file(self, full_file_path):
        dir = Path(full_file_path)
        if dir.is_file():
            with os.scandir(dir.parent) as it:
                for f in it:
                    try:
                        if f.is_file() and f.name == dir.name:
                            self._process_a_file(f)
                            return
                    except PermissionError as e:
                        print(f'EEE => Permissions error: {e}')
                    except OSError as e:
                        print(f'EEE => OSError {e.errno}-{e}')

        print(f"{Fore.MAGENTA}-> No file processed '{Fore.RESET}{full_file_path}'")

    def print_found_list(self):
        """
        Print the list of found items
        :return:
        """
        print()
        print(f'{Fore.LIGHTCYAN_EX}{Scanner.sep} Found items {Scanner.sep}{Fore.RESET}')
        print(self.found)

    def print_found_csv(self, file_name):
        """
        Print the list of found items in the form of CSV file
        :param file_name:
        :return:
        """

        if self.found:

            if file_name:
                with open(file_name, "w", encoding="UTF8", errors='ignore') as handle:
                    handle.write(f"{CsvRow.get_header()}\n")
                    for x in self.found:
                        handle.write(f"{x}\n")

                with open(file_name, "r", encoding="UTF8", errors='ignore') as handle:
                    return handle.read()

        return None
