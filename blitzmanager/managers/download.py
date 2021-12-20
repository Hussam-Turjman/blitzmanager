# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

import sys
import requests
from ..path import Path
from ..logger import logger


# Print iterations progress
# https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
def progress_bar(iteration: int, total: int, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    assert isinstance(iteration, int)
    assert isinstance(total, int)
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print()


def fetch(url: str, output_path: Path):
    """

    :param url:
    :param output_path:
    :return:
    """
    try:
        while True:
            with open(output_path.path, "wb+") as f:
                logger.info("Downloading %s .." % output_path.file_name())
                response = requests.get(url, stream=True)
                total_length = response.headers.get('content-length')

                if total_length is None:  # no content length header
                    logger.error(f"Content-length is invalid. Status code : {response.status_code}")
                    f.close()
                else:
                    dl = 0
                    total_length = int(total_length)
                    for data in response.iter_content(chunk_size=4096):
                        f.write(data)

                        progress_bar(dl,
                                     total_length,
                                     prefix=f"Downloading {output_path.file_name()}",
                                     suffix="Complete")
                        dl += len(data)
                    print()
                    sys.stdout.flush()
                    return True
    except Exception as e:
        logger.error(f"Failed to download {output_path.file_name()} from {url}. Error : {e}")


__all__ = ["fetch"]
