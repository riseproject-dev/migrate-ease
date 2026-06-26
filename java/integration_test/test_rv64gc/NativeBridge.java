// RISC-V target: Java source that uses JNI / native libraries is flagged so it
// can be reviewed for RISC-V native-library availability.
public class NativeBridge {
    static {
        System.loadLibrary("foo"); // expect: JavaSourceIssue
    }

    public native int compute(int x); // expect: JavaSourceIssue
}
