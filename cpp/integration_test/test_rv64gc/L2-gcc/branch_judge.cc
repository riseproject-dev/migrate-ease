// Branch evaluation with RISC-V predefined macros, warning level L2.
// At L2 the tool flags issues in SUPPORTED branches AND in UNKNOWN branches
// (macros it cannot resolve on the target). UNSUPPORTED (x86/Arm) branches
// stay suppressed.

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

// __riscv_vector is NOT defined on rv64gc -> UNKNOWN branch, flagged at L2.
#if defined(__riscv_vector)
    _mm256_add_ps (); // expect: IntrinsicIssue
#endif
