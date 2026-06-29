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

#  Verifies the JS scanner report against the fixtures in a test_<arch> dir.
#
#  package.json / package-lock.json files are strict JSON and cannot host
#  inline "// expect:" markers, so the expected issues are listed below as
#  (filename, package_name, file_line_1based) tuples. The JS scanner reports
#  0-indexed line numbers, so the expected `lineno` is file_line - 1.

import argparse
import json
import os

parser = argparse.ArgumentParser()
parser.description = 'please enter the Issue_type:'
parser.add_argument("--src-dir", metavar="src_dir", default=None)
parser.add_argument("--json-report", metavar="json_report", default=None)
args = parser.parse_args()

with open(args.json_report) as f2:
    report = json.load(f2)
issues = report['issues']
for i in issues:
    i['_seen'] = False

# Expected issues: (relative path from --src-dir, file line number 1-indexed,
# substring expected to appear in the snippet on that line).
EXPECTED = [
    ('package.json',          6,  'fsevents'),
    ('package.json',          10, 'node-sass'),
    ('sub/package-lock.json', 11, 'hiredis'),
]

tag_error = 0
for rel, file_line, needle in EXPECTED:
    expected_lineno = file_line - 1  # JS scanner reports 0-indexed line numbers
    full_path = os.path.join(args.src_dir, rel)
    matches = 0
    for i in issues:
        if i.get('_seen'):
            continue
        if i['filename'] == full_path and \
                i['lineno'] == expected_lineno and \
                i['issue_type']['type'] == 'ArchSpecificLibraryIssue' and \
                needle in i.get('snippet', ''):
            i['_seen'] = True
            matches += 1
    if matches == 0:
        tag_error = 1
        print("\033[1;31;40mError: issue ArchSpecificLibraryIssue for %s in %s:%s is expected but not detected.\033[0m" %
              (needle, full_path, file_line))
    elif matches > 1:
        tag_error = 1
        print("\033[1;31;40mError: issue ArchSpecificLibraryIssue for %s in %s:%s is detected more than once.\033[0m" %
              (needle, full_path, file_line))

for i in issues:
    if not i.get('_seen'):
        tag_error = 1
        print("\033[1;31;40mError: issue from file %s:%s is detected but was not expected.\033[0m" %
              (i['filename'], i['lineno']))

if tag_error == 0:
    print("\033[1;32;40mpass\033[0m")
