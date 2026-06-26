// RISC-V target: x86 inline assembly via asm!/global_asm!/llvm_asm! must be
// flagged. These are x86 memory-barrier / instruction patterns that need
// porting away from x86.

#[cfg(any(target_arch = "x86", target_arch = "x86_64"))]
fn x86_inline_asm()
{
    unsafe {
        asm!("" : : : "memory"); // expect: RustInlineAsmIssue
        asm!("" : : : "sfence"); // expect: RustInlineAsmIssue
        asm!("crc32b %1, %0" : "+r"(crc) : "rm"(v)); // expect: RustInlineAsmIssue
        global_asm!("" : : : "mfence"); // expect: RustInlineAsmIssue
    }
}
