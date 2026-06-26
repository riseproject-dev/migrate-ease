"""
Copyright 2026 Arm ltd.

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


from common.arch_strings import *


# Define mappings for vendors, instance types, and their respective ISAs.
# RISC-V cloud instances -- to be populated as hardware becomes available.
PLATFORM_CONFIG = {}

SUPPORTED_VENDORS = list(PLATFORM_CONFIG.keys())

def get_supported_instance_types(vendor):
    return list(PLATFORM_CONFIG.get(vendor, {}).keys())

def get_isa_for_instance_type(vendor, instance_type):
    return PLATFORM_CONFIG.get(vendor, {}).get(instance_type)
