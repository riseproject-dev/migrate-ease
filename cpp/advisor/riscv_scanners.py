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

from common.issue_type_filter import IssueTypeFilter
from .riscv_asm_source_scanner import RiscvAsmSourceScanner
from .riscv_config_guess_scanner import RiscvConfigGuessScanner
from .riscv_makefile_scanner import RiscvMakefileScanner
from .riscv_source_scanner import RiscvSourceScanner
from .target_os_filter import TargetOsFilter


class RiscvScanners:
    """
    Set of scanners that may be used to scan for potential porting issues in
    files from x86 Intel or Arm processors to RISC-V processors.
    """

    def __init__(self, issue_type_config, output_format, march, compiler, warning_level):
        """
        Args:
            issue_type_config (IssueTypeConfig): issue type filter
            configuration.
        """
        self.scanners = [RiscvSourceScanner(output_format=output_format, march=march,
                                            compiler=compiler, warning_level=warning_level),
                         RiscvMakefileScanner(output_format=output_format, march=march),
                         RiscvAsmSourceScanner(output_format=output_format, march=march),
                         RiscvConfigGuessScanner(output_format=output_format, march=march)]

        self.filters = []
        self.filters += [IssueTypeFilter(issue_type_config),
                         TargetOsFilter()]

    def __iter__(self):
        return self.scanners.__iter__()

    def initialize_report(self, report):
        """
        Initializes the given report for scanning.

        Args:
            report (Report): Report to initialize_report.
        """
        for a_filter in self.filters:
            a_filter.initialize_report(report)

        for scanner in self.scanners:
            scanner.initialize_report(report)

    def finalize_report(self, report):
        """
        Finalizes the given report.

        Args:
            report (Report): Report to finalize_report.
        """
        for scanner in self.scanners:
            scanner.finalize_report(report)

        for a_filter in self.filters:
            a_filter.finalize_report(report)
