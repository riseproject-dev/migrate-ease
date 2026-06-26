"""
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

#  Verifies the Java scanner report against the fixtures in a test_<arch> dir.
#
#  Two kinds of fixtures are checked:
#    * .jar / .war packages -- matched by filename against the expected lists
#      below (JarIssue is reported per-package with no line number, so a text
#      "// expect:" marker is not possible).
#    * .java sources -- matched by "// expect: <IssueType>" markers. NOTE the
#      Java source scanner reports 0-indexed line numbers, so a marker on source
#      line N corresponds to a reported lineno of N-1.

import argparse
import json
import os
import re

parser = argparse.ArgumentParser()
parser.description = 'please enter the Issue_type:'
parser.add_argument("--src-dir", metavar="src_dir", default=None)
parser.add_argument("--json-report", metavar="json_report", default=None)
args = parser.parse_args()

with open(args.json_report) as f2:
    report = json.load(f2)
    nof_issues = len(report['issues'])

for i in range(nof_issues):
    report['issues'][i]['tig_of_first_traversal'] = 'false'

tag_error = 0

# Packages whose only native libraries are non-RISC-V -> expect a JarIssue.
# Packages that ship a riscv64 native lib -> no issue expected.
jar_files = ['foo-foreign-1.0.jar']
issue_jar_files = ['foo-foreign-1.0.jar']

SOURCE_EXTENSIONS = ['.java']

for filename in os.listdir(args.src_dir):
    ext = os.path.splitext(filename)[1]

    if ext in ['.jar', '.war']:
        if filename in jar_files:
            issue = 'JarIssue' if filename in issue_jar_files else ''
            if issue:
                file_detect = False
                for i in range(nof_issues):
                    if report['issues'][i]['filename'] == os.path.join(args.src_dir, filename) and \
                            report['issues'][i]["issue_type"]['type'] == issue:
                        file_detect = True
                        report['issues'][i]['tig_of_first_traversal'] = 'true'
                if not file_detect:
                    tag_error = 1
                    print("\033[1;31;40mError: issue %s from file %s is expected but was not detected\033[0m" %
                          (issue, os.path.join(args.src_dir, filename)))

    elif ext in SOURCE_EXTENSIONS:
        with open(os.path.join(args.src_dir, filename)) as f1:
            lno = 0
            for l in f1.readlines():
                lno += 1
                if "expect:" in l:
                    issue = re.search("expect:.*", l)[0].replace('expect:', '').replace(' ', '')
                    # Java source scanner reports 0-indexed line numbers.
                    expected_lineno = lno - 1
                    num_lno = 0
                    for i in range(nof_issues):
                        if report['issues'][i]['lineno'] == expected_lineno and \
                                report['issues'][i]["filename"] == os.path.join(args.src_dir, filename) and \
                                report['issues'][i]["issue_type"]['type'] == issue:
                            num_lno += 1
                            report['issues'][i]['tig_of_first_traversal'] = "true"
                    if num_lno > 1:
                        tag_error = 1
                        print("\033[1;31;40mError: issue %s from file %s:%s is detected more than once.\033[0m" %
                              (issue, os.path.join(args.src_dir, filename), lno))
                    elif num_lno == 0:
                        tag_error = 1
                        print("\033[1;31;40mError: issue %s from file %s:%s is expected but not detected.\033[0m" %
                              (issue, os.path.join(args.src_dir, filename), lno))

for i in range(nof_issues):
    if report['issues'][i]['tig_of_first_traversal'] != 'true':
        tag_error = 1
        print("\033[1;31;40mError: issue from file %s:%s is detected but was not expected.\033[0m" %
              (os.path.abspath(os.path.join(args.src_dir, report['issues'][i]["filename"])), report['issues'][i]['lineno']))

if tag_error == 0:
    print("\033[1;32;40mpass\033[0m")
