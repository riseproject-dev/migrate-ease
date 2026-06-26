#!/usr/bin/env bash
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Regenerates the predefined-macro JSON files used by the C/C++ scanner to
# evaluate #if/#ifdef branches for each supported RISC-V target.
#
# Each JSON is {"gcc": {...}, "clang": {...}} where every value is the macro's
# expansion as a string, matching the format produced by `<cc> -dM -E`.
#
# Prerequisites:
#   sudo apt-get install -y gcc-riscv64-linux-gnu clang
#
# Usage:
#   cpp/db/generate_macros.sh          # writes macros_rv64gc.json + macros_rva23.json
#
set -euo pipefail

DB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GCC="${RISCV_GCC:-riscv64-linux-gnu-gcc}"
CLANG="${RISCV_CLANG:-clang}"
CLANG_TARGET="riscv64-unknown-linux-gnu"

# rv64gc  -- baseline IMAFDC, no vector, no bit-manip.
RV64GC_ISA="rv64gc"

# rva23  -- RVA23U64 profile. gcc<14 and clang<19 don't accept -march=rva23u64,
# so spell out the equivalent ISA string. Mandates Vector + Zba/Zbb/Zbs.
RVA23_ISA="rv64gcv_zba_zbb_zbs_zicond_zicsr_zifencei_zicntr_zihpm_zfhmin_zvfhmin_zvbb_zvkt_zihintntl_zawrs_zcb_zfa"

# Convert `#define KEY VALUE` lines from `cc -dM -E` into a JSON object whose
# values are strings (KEY with no value -> "1", matching cpp -dM behaviour where
# every -dM macro has an expansion).
dump_to_json() {
    python3 -c '
import json, sys
macros = {}
for line in sys.stdin:
    line = line.rstrip("\n")
    if not line.startswith("#define "):
        continue
    rest = line[len("#define "):]
    parts = rest.split(" ", 1)
    name = parts[0]
    # function-like macros: "#define f(x) ..." -> key is "f(x)"; keep as-is.
    value = parts[1] if len(parts) > 1 else "1"
    macros[name] = value
sys.stdout.write(json.dumps(macros, indent=2, sort_keys=True))
'
}

emit_target() {
    local isa="$1" out="$2"
    echo "Generating ${out} (-march=${isa}) ..." >&2

    local gcc_json clang_json
    gcc_json="$("${GCC}" -march="${isa}" -dM -E -x c /dev/null | dump_to_json)"
    clang_json="$("${CLANG}" --target="${CLANG_TARGET}" -march="${isa}" -dM -E -x c /dev/null | dump_to_json)"

    python3 -c '
import json, sys
gcc = json.loads(sys.argv[1])
clang = json.loads(sys.argv[2])
out = sys.argv[3]
with open(out, "w") as f:
    json.dump({"gcc": gcc, "clang": clang}, f, indent=2, sort_keys=True)
    f.write("\n")
' "${gcc_json}" "${clang_json}" "${out}"
}

emit_target "${RV64GC_ISA}" "${DB_DIR}/macros_rv64gc.json"
emit_target "${RVA23_ISA}"  "${DB_DIR}/macros_rva23.json"

echo "Done. Wrote macros_rv64gc.json and macros_rva23.json into ${DB_DIR}." >&2
