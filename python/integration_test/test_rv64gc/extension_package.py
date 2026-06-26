# RISC-V target: x86-only Python extension packages must be flagged. Packages
# that ship RISC-V wheels (none configured yet) would be excluded.

# x86-only packages -> flagged.
from mkl import foo # expect: PythonPackageIssue
import daal4py # expect: PythonPackageIssue
from scikit-learn-intelex import bar # expect: PythonPackageIssue
import iced-x86 # expect: PythonPackageIssue

# aarch64-only and common packages are not in the x86 set -> not flagged.
from pycuda-arm-linux import x
import keystone-engine
import numpy
