# -*- coding: utf-8 -*-

"""
RaTS: Ransomware Traces Scanner
Copyright (C) 2015, 2016, 2017 Roberto Battistoni (r.battistoni@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

from pathlib import Path

from config import config
from config.config import MIN_LEN_COMPRESSED_CONTENT
from logic.csv_row import CsvRow
from logic.randomness import RandTest
from misc import utils
from misc.utils import norm_percentage
from scanners.scanner import Scanner

IMAGE = "Image"
CRYPTO = "Crypto"


class ScannerForCrypt(Scanner):
    """
    Class managing the encrypted file: in the filename and in the content
    """

    def __init__(self, verbose=False):
        """
        Initialization
        :return:
        """
        super().__init__(verbose)

    def print_config(self):
        print("%s Config elements for '%s' %s" % (Scanner.sep, __name__, Scanner.sep))
        print()
        print(
            "Compression Randomness threshold (strictly greater than): " + str(config.COMPR_RAND_TH))
        print("Entropy Randomness threshold (strictly greater than): " + str(config.ENTR_RAND_TH))
        print("Number of first bytes of the content to elaborate: " + str(config.NUM_BYTES_TO_RAND_CHECK))
        print()

    def search(self, path, recursive=True):
        """
        The main search method

        :param path:
        :param recursive:
        :return:
        """
        if self.verbose:
            self.print_config()
        print(Scanner.sep + " Starting search Crypto content in: " + str(path) + " " + Scanner.sep)
        self._search(path, recursive)

    def _search(self, path, recursive=True):
        """
        Recursive main search method
        :param recursive: recursive flag
        :param path: starting path
        :return:
        """
        p = Path(path)

        try:
            file_list = [x for x in p.iterdir() if not x.is_symlink() and x.is_file()]
            for f in file_list:
                if self.verbose:
                    print("- Searching for crypto content in the file: " + str(f))
                found = self.search_for_crypted_content(f)
                if found:
                    print("=====> Found crypto content in: " + str(f))
                    self.found.append(found)

            if recursive:
                dir_list = [x for x in p.iterdir() if not x.is_symlink() and x.is_dir()]
                for x in dir_list:
                    if self.verbose:
                        print("+ Searching (for crypto) in the path: " + str(x))
                    self._search(x, recursive)

        except PermissionError:
            print("EEE => Permissions error for: " + str(p))
        except OSError as e:
            print("EEE => OSError: " + e.strerror)

    def search_for_crypted_content(self, file):
        """
        Calculate randomness of the crypto content

        :param file:
        :return:
        """
        try:
            with file.open(mode='rb') as handle:
                content = handle.read(config.NUM_BYTES_TO_RAND_CHECK)
                lcontent = len(content)

                # for the empty files
                if lcontent == 0:
                    return None

                if not utils.is_known_file_type(content, verbose=self.verbose):

                    # First test is the Entropy
                    rnd_test_entropy = round(RandTest.calc_entropy_test(content, self.verbose), 2)
                    if rnd_test_entropy > config.ENTR_RAND_TH:

                        # Second test is the Compression factor
                        rnd_test_compr = round(RandTest.calc_compression_test(content, self.verbose), 2)
                        if rnd_test_compr > config.COMPR_RAND_TH and lcontent > MIN_LEN_COMPRESSED_CONTENT:

                            #rnd_test_compr = norm_percentage(rnd_test_compr)
                            adesc = "ent: {0} ==> cmp: {1}".format(str(rnd_test_entropy),rnd_test_compr)
                            return CsvRow(file, CRYPTO, adesc)

        except PermissionError:
            print("EEE => Permissions error for: " + str(file))
        except OSError as e:
            print("EEE => OSError: " + e.strerror)

        return None
