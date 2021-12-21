# Copyright (c) 2021-2022 The BlitzManager project Authors. All rights reserved. Use of this
# source code is governed by a BSD-style license that can be found in the LICENSE file.


from enum import Enum


class SupportedManagers(Enum):
    NONE = -1
    VCPKG = 0


__all__ = ["SupportedManagers"]
