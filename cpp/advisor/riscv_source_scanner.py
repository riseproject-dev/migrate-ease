"""
Copyright 2020-2023 Alibaba Inc.
Copyright 2017-2020 Arm Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from .clang_source_scanner import ClangSourceScanner


class RiscvSourceScanner(ClangSourceScanner):

    """
    Scanner that scans C, C++ and Fortran source files for RISC-V potential
    porting issues.

    The incompatible-intrinsic set and macro-JSON selection live in the base
    ClangSourceScanner, so this subclass only needs to forward the constructor.
    Keeping the logic in the base class lets Go cgo detection -- which
    instantiates ClangSourceScanner directly -- pick up RISC-V behaviour for
    free.
    """

    def __init__(self, output_format, march, compiler, warning_level):

        super().__init__(output_format=output_format,
                         march=march,
                         compiler=compiler,
                         warning_level=warning_level)
