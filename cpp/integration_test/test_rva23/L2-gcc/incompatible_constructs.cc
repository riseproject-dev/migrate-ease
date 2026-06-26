// RISC-V target: x86 and Arm/NEON constructs must all be flagged.
// These constructs are NOT wrapped in any #if, so they are always scanned
// regardless of warning level or target compiler.

// x86 intrinsic -> IntrinsicIssue
    _mm256_add_ps (); // expect: IntrinsicIssue

// Arm/NEON intrinsic -> IntrinsicIssue (key new check: RISC-V flags Arm too)
    vaddq_f32 (); // expect: IntrinsicIssue

// x86 SIMD header -> IncompatibleHeaderFileIssue
#include <immintrin.h> // expect: IncompatibleHeaderFileIssue

// x86 inline assembly -> InlineAsmIssue
__asm__ __volatile__("crc32l %1, %0" : "+r"(crc) : "rm"(v)); // expect: InlineAsmIssue
