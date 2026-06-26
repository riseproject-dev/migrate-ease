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

import io
import json
import tempfile
import unittest

from common.issue_type_config import IssueTypeConfig
from common.json_report import JsonReport
from common.report_factory import ReportOutputFormat
from common.report import Report
from common.issue import BaseReportItem

from advisor.riscv_config_guess_scanner import RiscvConfigGuessScanner
from advisor.riscv_source_scanner import RiscvSourceScanner
from advisor.report_item import CPP_REPORT_TYPES


class TestJsonReport(unittest.TestCase):

    def test_output(self):
        config_guess_scanner = RiscvConfigGuessScanner(ReportOutputFormat.JSON, march='rv64gc')
        source_scanner = RiscvSourceScanner(ReportOutputFormat.JSON, march='rv64gc', compiler='gcc', warning_level='L1')

        # issue_type_config is the raw --issue-types string (or None) in
        # production; passing the IssueTypeConfig object is not JSON
        # serializable. Use the default filter string here.
        Report.REPORT_ITEM = BaseReportItem
        # Extend the shared global type registry idempotently: both test
        # methods run this, and a plain += would duplicate CPP_REPORT_TYPES,
        # causing Report.write() to emit each issue once per duplicate type.
        Report.REPORT_ITEM.TYPES += [
            t for t in CPP_REPORT_TYPES if t not in Report.REPORT_ITEM.TYPES]
        report = JsonReport('/root', target_os='linux', issue_type_config=IssueTypeConfig.DEFAULT_FILTER)

        report.add_source_file('/root/src/test_inline_asm.c')
        io_object = io.StringIO('__asm__ __volatile__( "pause" : : : "memory" )')
        source_scanner.scan_file_object('test_inline_asm.c',
                                        io_object,
                                        report)

        report.add_source_file('/root/src/test_pragma_simd.c')
        io_object = io.StringIO('#pragma simd foo')
        source_scanner.scan_file_object('test_pragma_simd.c',
                                        io_object,
                                        report)

        report.add_source_file('/root/src/config.guess')
        io_object = io.StringIO('xxx')
        config_guess_scanner.scan_file_object('config.guess',
                                              io_object,
                                              report)

        self.assertEqual(len(report.issues), 3)

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as ofp:
            report.write(ofp)
            fname = ofp.name
            ofp.close()

            with open(fname) as ifp:
                json_top = json.load(ifp)

            self.assertIn('errors', json_top)
            self.assertEqual(len(json_top['errors']), 0)
            self.assertIn('issues', json_top)
            self.assertEqual(len(json_top['issues']), 3)
            self.assertIn('remarks', json_top)
            self.assertEqual(len(json_top['remarks']), 0)
            self.assertIn('issue_type_config', json_top)
            self.assertEqual(json_top['issue_type_config'], IssueTypeConfig.DEFAULT_FILTER)
            self.assertIn('target_os', json_top)
            self.assertIn(json_top['target_os'], ['linux', 'windows'])
            self.assertIn('root_directory', json_top)
            self.assertEqual(json_top['root_directory'], '/root')
            self.assertIn('source_dirs', json_top)
            self.assertEqual(len(json_top['source_dirs']), 1)
            self.assertEqual(json_top['source_dirs'][0], '/root/src')
            self.assertIn('source_files', json_top)
            self.assertEqual(len(json_top['source_files']), 3)
            seen_inline_asm = False
            seen_pragma = False
            seen_config_guess = False

            for fname in json_top['source_files']:

                if 'test_inline_asm.c' in fname:
                    seen_inline_asm = True
                elif 'test_pragma_simd.c' in fname:
                    seen_pragma = True
                elif 'config.guess' in fname:
                    seen_config_guess = True
                else:
                    self.fail('Unexpected source file name in JSON output')
            self.assertTrue(seen_inline_asm)
            self.assertTrue(seen_pragma)
            self.assertTrue(seen_config_guess)

    def test_issue_count_equals_zero(self):

        source_scanner = RiscvSourceScanner(ReportOutputFormat.JSON, march='rv64gc', compiler='gcc', warning_level='L1')

        Report.REPORT_ITEM = BaseReportItem
        # Extend the shared global type registry idempotently: both test
        # methods run this, and a plain += would duplicate CPP_REPORT_TYPES,
        # causing Report.write() to emit each issue once per duplicate type.
        Report.REPORT_ITEM.TYPES += [
            t for t in CPP_REPORT_TYPES if t not in Report.REPORT_ITEM.TYPES]
        JsonReport.lang = 'cpp'
        report = JsonReport('/root', issue_type_config=IssueTypeConfig.DEFAULT_FILTER)

        report.add_source_file('/root/src/test.c')
        io_object = io.StringIO('xxx" )')
        source_scanner.scan_file_object('test.c',
                                        io_object,
                                        report)

        self.assertEqual(len(report.issues), 0)

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as ofp:
            report.write(ofp)
            fname = ofp.name
            ofp.close()

        with open(fname) as ifp:
            json_top = json.load(ifp)

        self.assertEqual(json_top['total_issue_count'], 0)


if __name__ == '__main__':
    unittest.main()
