// RISC-V target: x86 and Arm/NEON intrinsics are both incompatible and must be
// flagged. The intrinsic checkpoint requires a leading space before the name,
// so calls are indented. The Rust scanner does not evaluate #[cfg] attributes;
// it scans every line, so the cfg guards below are documentation only.

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
fn x86_intrinsics()
{
    unsafe {
        _mm256_add_ps(); // expect: RustIntrinsicIssue
        _mm256_loadu_si256(); // expect: RustIntrinsicIssue
    }
}

// On the Arm build this branch was the target and its NEON intrinsics were not
// flagged. On a RISC-V target they are incompatible and must be flagged.
#[cfg(all(target_arch = "aarch64", target_feature = "neon"))]
fn neon_intrinsics()
{
    unsafe {
        vaddq_f32(); // expect: RustIntrinsicIssue
        vmaxvq_s32(); // expect: RustIntrinsicIssue
    }
}
