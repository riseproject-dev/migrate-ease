import cffi

ffi = cffi.FFI()

# x86 inline assembly embedded in a cffi C block must be flagged on a RISC-V
# target. The Arm dispatch branch (the target on the Arm build) is migrated to
# __riscv; the cffi C-block scanner flags incompatible asm line-by-line and does
# not evaluate #if branches.
ffi.cdef("""int add(int a, int b);""")

ffi.set_source('_ext', r"""
int add(int a, int b)
{
__asm__ __volatile__("sfence" : : : "memory"); // expect: PythonInlineAsmIssue
__asm__ __volatile__("crc32l %1, %0" : "+r"(crc) : "rm"(v)); // expect: PythonInlineAsmIssue
}
""")
