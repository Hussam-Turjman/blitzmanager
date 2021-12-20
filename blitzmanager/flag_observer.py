# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.
import abc


class FlagObserver(abc.ABC):
    @abc.abstractmethod
    def flag_set(self, flag: str, value: object):
        """

        :param flag:
        :param value:
        :return:
        """


__all__ = ["FlagObserver"]
