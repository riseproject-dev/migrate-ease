"""
Copyright 2025 Google LLC

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

import unittest

from common.main import PLATFORM_CONFIG, SUPPORTED_VENDORS, get_supported_instance_types, get_isa_for_instance_type


class TestMain(unittest.TestCase):

    # No RISC-V cloud instances are configured yet, so the vendor/instance map
    # is intentionally empty (see common/instance_strings.py). These tests
    # verify the lookup API still behaves correctly over the empty config; they
    # should be extended once RISC-V instances become available.

    def test_supported_vendors(self):
        self.assertEqual(SUPPORTED_VENDORS, [])
        self.assertEqual(PLATFORM_CONFIG, {})

    def test_get_supported_instance_types(self):
        # Every vendor lookup returns an empty list while no instances exist.
        self.assertEqual(get_supported_instance_types("NonExistentVendor"), [])
        for vendor in SUPPORTED_VENDORS:
            self.assertEqual(get_supported_instance_types(vendor), [])

    def test_get_isa_for_instance_type(self):
        # No instance maps to an ISA yet; lookups return None.
        self.assertIsNone(get_isa_for_instance_type("AWS", "Graviton"))
        self.assertIsNone(get_isa_for_instance_type("NonExistentVendor", "C4A"))


if __name__ == '__main__':
    unittest.main()
