# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.

import sys
import requests
from ..path import Path
from ..logger import logger, progress_bar


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
                    logger.critical(f"Content-length is invalid. Status code : {response.status_code}")
                    f.close()
                    output_path.remove(ignore_errors=True)
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
        logger.critical(f"Failed to download {output_path.file_name()} from {url}. Error : {e}")


__all__ = ["fetch"]
