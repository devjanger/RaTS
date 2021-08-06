# -*- coding: utf-8 -*-

import gzip
from collections import Counter

import math

from colorama import Fore


class RandTest:
    """
    Class for randomness tests
    """

    @staticmethod
    def calc_entropy_test(content: bytes, verbose: bool) -> float:
        """
        Entropy randomness test

        Binary Entropy from: http://rosettacode.org/wiki/Entropy#Python:_More_succinct_version

        For every byte we have 8 bits, so 256 different characters. Maximum entropy is for a string
        that contains an equal distribution on every character:

        H(X) = 256 * 1/256 * -log2(1/256) = 1 * log2(256) = 8

        :param content:
        :param verbose:
        :return:
        """

        p, lns = Counter(content), float(len(content))
        H = -sum(count / lns * math.log(count / lns, 2) for count in p.values())

        if verbose:
            print(f"{Fore.LIGHTBLUE_EX}-> [Entropy Test]{Fore.RESET} crypto values: H: {H}")

        return H

    @staticmethod
    def calc_max_entropy(content: bytes):
        """
        Calculate the max entropy for the content
        """

        card_X = len(set(content))
        max_H = math.log(card_X, 2)

        print(f"{Fore.LIGHTBLUE_EX}-> [Entropy Test]{Fore.RESET} max H: {max_H}")

    @staticmethod
    def _compress(data) -> bytes:
        return gzip.compress(data, 9)

    def __init__(self):
        self._compression_footprint_length = len(RandTest._compress(bytes([0x0])))

    def calc_compression_test(self, bcontent: bytes, verbose: bool) -> float:
        """
        Calculates the randomness of the content using the Kolmogorov complexity

        - more is the compression/randomness, lesser the randomness/compression is
        - def: ratio = len(zipped_content)/len(content)
        -   ratio close to 1 means high randomness and low compression
        -   ratio close to 0 means high compression and low randomness

        :param bcontent: byte content
        :param verbose:
        :return: r in [0,1]
        """

        # if print_path:
        #    print("The content is: %s" % content)
        len_bcontent = len(bcontent)
        if len_bcontent == 0:
            if verbose:
                print("Empty string, nothing to do!")
            return 0

        len_compr_cnt = (len(self._compress(bcontent)) - self._compression_footprint_length) * 1.0
        ct = len_compr_cnt / len_bcontent

        if verbose:
            print(f"{Fore.LIGHTBLUE_EX}-> [Compression Test]{Fore.RESET} compression values: n: {len_compr_cnt}, d: {len_bcontent}, l0: {self._compression_footprint_length}, compr. test: {ct} ")

        return ct
