from cffi import FFI
ffi = FFI()

# cffi embeds C source via ffi.set_source(...). On a RISC-V target the embedded
# x86 and Arm/NEON intrinsics are incompatible and must be flagged. The leading
# space before each intrinsic name is required for the checkpoint to match.
ffi.cdef("""int compute();""")

ffi.set_source("_ext", """
int compute()
{
    _mm256_add_ps (); // expect: PythonIntrinsicIssue
    _mm256_loadu_si256 (); // expect: PythonIntrinsicIssue
    vaddq_f32 (); // expect: PythonIntrinsicIssue
    __atomic_load_n (); // expect: PythonCPPStdCodes
}
""")
