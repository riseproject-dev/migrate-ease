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

import json
import os
import unittest

from advisor.naive_cpp import *


def _load_macros(march):
    db = os.path.join(os.path.dirname(__file__), 'db', 'macros_%s.json' % march)
    with open(db) as f:
        return json.load(f)['gcc']


class TestNaiveCpp(unittest.TestCase):
    def setUp(self):
        self.march = 'rv64gc'
        self.macros = _load_macros(self.march)

    def tearDown(self):
        pass

    def _naive_cpp(self, warning_level='L1'):
        return NaiveCpp(march=self.march, macros=self.macros, warning_level=warning_level)

    def test_unknown_march_raises(self):
        with self.assertRaises(RuntimeError):
            NaiveCpp(march="unknown_arch", macros=self.macros)

    def test_support_state_target_vs_foreign(self):
        # On a RISC-V target, branches guarded by a RISC-V macro are supported
        # (live) while x86/Arm branches are unsupported (dead). The #else of a
        # foreign-arch #if becomes the live branch.
        naive_cpp = self._naive_cpp()

        # #if defined(__riscv) -> live; #elif defined(__aarch64__) and #else
        # are not taken because the #if branch already supports the target.
        self.assertTrue(naive_cpp.parse_line('#if defined(__riscv)').is_support)
        self.assertFalse(naive_cpp.parse_line('#elif defined(__aarch64__)').is_support)
        self.assertFalse(naive_cpp.parse_line('#else').is_support)
        naive_cpp.parse_line('#endif')

        # #if defined(__x86_64__) -> dead; its #else is the live RISC-V path.
        self.assertFalse(naive_cpp.parse_line('#if defined(__x86_64__)').is_support)
        self.assertTrue(naive_cpp.parse_line('#else').is_support)
        naive_cpp.parse_line('#endif')

        # #if defined(__aarch64__) -> dead (Arm is a foreign arch on RISC-V).
        self.assertFalse(naive_cpp.parse_line('#if defined(__aarch64__)').is_support)
        naive_cpp.parse_line('#endif')

    def test_support_state_negation(self):
        naive_cpp = self._naive_cpp()

        # !defined(__riscv) is dead on a RISC-V target; its #else is live.
        self.assertFalse(naive_cpp.parse_line('#if !defined(__riscv)').is_support)
        self.assertTrue(naive_cpp.parse_line('#else').is_support)
        naive_cpp.parse_line('#endif')

        # !defined(__x86_64__) holds on RISC-V -> the #if branch is live.
        self.assertTrue(naive_cpp.parse_line('#if !defined(__x86_64__)').is_support)
        naive_cpp.parse_line('#endif')

    def test_support_state_ifdef_ifndef(self):
        naive_cpp = self._naive_cpp()

        self.assertTrue(naive_cpp.parse_line('#ifdef __riscv').is_support)
        naive_cpp.parse_line('#endif')

        self.assertFalse(naive_cpp.parse_line('#ifdef __aarch64__').is_support)
        naive_cpp.parse_line('#endif')

        # #ifndef of a defined target macro -> dead branch.
        self.assertFalse(naive_cpp.parse_line('#ifndef __riscv').is_support)
        naive_cpp.parse_line('#endif')

        # #ifndef of an undefined foreign macro -> live branch.
        self.assertTrue(naive_cpp.parse_line('#ifndef __aarch64__').is_support)
        naive_cpp.parse_line('#endif')

    def test_support_state_unknown_macro_warning_level(self):
        # __riscv_vector is NOT defined on rv64gc, so the branch is UNKNOWN:
        # suppressed at L1, reported at L2.
        l1 = self._naive_cpp('L1')
        self.assertFalse(l1.parse_line('#if defined(__riscv_vector)').is_support)
        l1.parse_line('#endif')

        l2 = self._naive_cpp('L2')
        self.assertTrue(l2.parse_line('#if defined(__riscv_vector)').is_support)
        l2.parse_line('#endif')

    def test_support_state_rva23_vector(self):
        # On rva23 the Vector extension is mandated, so __riscv_vector IS
        # defined -> the branch is supported at both L1 and L2.
        macros = _load_macros('rva23')
        for level in ('L1', 'L2'):
            naive_cpp = NaiveCpp(march='rva23', macros=macros, warning_level=level)
            self.assertTrue(naive_cpp.parse_line('#if defined(__riscv_vector)').is_support)
            naive_cpp.parse_line('#endif')

    def test_support_state_nested(self):
        naive_cpp = self._naive_cpp()

        # An unknown macro nested inside a live RISC-V branch stays non-support
        # at L1, and the enclosing branch resumes support after the inner #endif.
        self.assertTrue(naive_cpp.parse_line('#ifdef __riscv').is_support)
        self.assertFalse(naive_cpp.parse_line('#ifdef foo').is_support)
        naive_cpp.parse_line('#endif')
        self.assertTrue(naive_cpp.parse_line('#ifdef __riscv').is_support)
        naive_cpp.parse_line('#endif')
        naive_cpp.parse_line('#endif')

    def test_in_compiler_specific_code(self):
        # Compiler macros are recognised as supported (gcc/clang are supported
        # compilers), independent of the target arch.
        naive_cpp = self._naive_cpp()
        self.assertTrue(naive_cpp.parse_line('#ifdef __GNUC__').is_support)
        naive_cpp.parse_line('#endif')

    def test_parse_line_pragma(self):
        naive_cpp = self._naive_cpp()
        result = naive_cpp.parse_line('#pragma simd foo')
        self.assertEqual(result.directive_type,
                         PreprocessorDirective.TYPE_PRAGMA)

    def test_parse_line_error(self):
        naive_cpp = self._naive_cpp()
        result = naive_cpp.parse_line('#error foo')
        self.assertEqual(result.directive_type,
                         PreprocessorDirective.TYPE_ERROR)

    def test_riscv_re(self):
        # RISC-V detection-token regex matches RISC-V arch names.
        match = NaiveCpp.RISCV_UNSUPPORTED_MACROS_RE.match('aarch64')
        self.assertIsNotNone(match)

        match = NaiveCpp.RISCV_UNSUPPORTED_MACROS_RE.match('__x86_64__')
        self.assertIsNotNone(match)

        # A RISC-V token is not in the *unsupported* set.
        match = NaiveCpp.RISCV_UNSUPPORTED_MACROS_RE.match('riscv64')
        self.assertIsNone(match)

    def test_aarch64_re(self):
        # The AArch64 detection-token regex is retained for source scanning.
        match = NaiveCpp.AARCH64_MACROS_RE.match('aarch64')
        self.assertIsNotNone(match)

        match = NaiveCpp.AARCH64_MACROS_RE.match('__aarch64__')
        self.assertIsNotNone(match)

        match = NaiveCpp.AARCH64_MACROS_RE.match('foo')
        self.assertIsNone(match)

    def test_compiler_re(self):
        match = NaiveCpp.ALL_COMPILER_MACROS_RE.match('GNUC')
        self.assertIsNotNone(match)

        match = NaiveCpp.ALL_COMPILER_MACROS_RE.match('__GNUC__')
        self.assertIsNotNone(match)

        match = NaiveCpp.ALL_COMPILER_MACROS_RE.match('foo')
        self.assertIsNone(match)

    def test_macro_body(self):
        naive_cpp = self._naive_cpp()

        result = naive_cpp.parse_line('#define MACRO BODY')
        self.assertEqual(result.directive_type,
                         PreprocessorDirective.TYPE_DEFINE)
        self.assertEqual(result.macro_name, 'MACRO')
        self.assertEqual(result.body, 'BODY')

        result = naive_cpp.parse_line('#define MACRO(a,b,c) BODY')
        self.assertEqual(result.directive_type,
                         PreprocessorDirective.TYPE_DEFINE)
        self.assertEqual(result.macro_name, 'MACRO(a,b,c)')
        self.assertEqual(result.body, 'BODY')

    def test_parse_line_if_else(self):
        # A foreign-arch #if/#else: the #if (x86) branch is dead, the #else is
        # the live RISC-V path.
        naive_cpp = self._naive_cpp()
        self.assertFalse(naive_cpp.parse_line('#if defined(__x86_64__)').is_support)
        self.assertTrue(naive_cpp.parse_line('#else').is_support)
        naive_cpp.parse_line('#endif')

    def test_parse_line_if_elif_else(self):
        # x86 dead, RISC-V #elif live, #else not taken.
        naive_cpp = self._naive_cpp()
        self.assertFalse(naive_cpp.parse_line('#if defined(__x86_64__)').is_support)
        self.assertTrue(naive_cpp.parse_line('#elif defined(__riscv)').is_support)
        self.assertFalse(naive_cpp.parse_line('#else').is_support)
        naive_cpp.parse_line('#endif')

    def test_parse_line_if_elif_elif_else(self):
        # x86 dead, Arm dead, RISC-V #elif live, #else not taken.
        naive_cpp = self._naive_cpp()
        self.assertFalse(naive_cpp.parse_line('#if defined(__x86_64__)').is_support)
        self.assertFalse(naive_cpp.parse_line('#elif defined(__aarch64__)').is_support)
        self.assertTrue(naive_cpp.parse_line('#elif defined(__riscv)').is_support)
        self.assertFalse(naive_cpp.parse_line('#else').is_support)
        naive_cpp.parse_line('#endif')


if __name__ == '__main__':
    unittest.main()
