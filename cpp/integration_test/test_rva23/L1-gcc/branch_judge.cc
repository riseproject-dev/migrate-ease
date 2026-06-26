// Branch evaluation with RISC-V predefined macros, rva23 target.
// On rva23 the RVA23U64 profile mandates Vector, so __riscv_vector IS defined
// -> that branch is SUPPORTED (live) and flagged at both L1 and L2. This is the
// key difference from rv64gc, where __riscv_vector is an UNKNOWN (dead) branch.

// x86 branch: dead on a RISC-V target -> contents suppressed.
#if defined(__x86_64__)
#include <immintrin.h>
    _mm256_add_ps ();
#endif

// Arm branch: this was the target on the Arm build; on RISC-V it is a foreign
// arch and dead, so its NEON intrinsic is suppressed.
#if defined(__aarch64__)
    vaddq_f32 ();
#endif

// RISC-V branch: live. x86 and Arm/NEON constructs ported into RISC-V code are
// all incompatible and flagged -- the key check that RISC-V flags Arm too.
#if defined(__riscv)
#include <immintrin.h> // expect: IncompatibleHeaderFileIssue
    _mm256_add_ps (); // expect: IntrinsicIssue
    vaddq_f32 (); // expect: IntrinsicIssue
#endif

// __riscv_vector IS defined on rva23 -> SUPPORTED branch, flagged at L1 and L2.
#if defined(__riscv_vector)
    _mm256_add_ps (); // expect: IntrinsicIssue
#endif
