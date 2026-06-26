package main

/*
#include <stdio.h>

// On a RISC-V target, x86 and Arm/NEON intrinsics used inside a cgo C block
// are incompatible and must be flagged. (The leading space before the name is
// required for the intrinsic checkpoint to match.)
void incompatible_intrinsics()
{
    _mm256_add_ps (); // expect: GolangIntrinsicIssue
    _mm512_loadu_si512 (); // expect: GolangIntrinsicIssue
    vaddq_f32 (); // expect: GolangIntrinsicIssue
}

// x86 inline assembly -> GolangInlineAsmIssue.
void incompatible_asm()
{
__asm__ __volatile__("crc32l %1, %0" : "+r"(crc) : "rm"(v)); // expect: GolangInlineAsmIssue
}

// __atomic_* builtins map to C++ memory-order guidance -> GolangCPPStdCodes.
void cpp_std_codes()
{
    __atomic_load_n (); // expect: GolangCPPStdCodes
    __atomic_store_n (); // expect: GolangCPPStdCodes
}

// Arch dispatch inside cgo. NOTE: the cgo C-block scanner flags incompatible
// intrinsics line-by-line and does not evaluate #if branches, so intrinsics in
// every branch are reported regardless of the guard.
#if defined(__x86_64__)
    _mm256_add_ps (); // expect: GolangIntrinsicIssue
#elif defined(__riscv)
    vaddq_f32 (); // expect: GolangIntrinsicIssue
#endif
*/
import "C"

func main() {}
