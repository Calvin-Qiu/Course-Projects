package enigma;

import org.junit.Test;
import ucb.junit.textui;

/** The suite of all JUnit tests for the enigma package.
 *  @author Calvin
 */
public class UnitTest {

    /** Run the JUnit tests in this package. Add xxxTest.class entries to
     *  the arguments of runClasses to run other JUnit tests. */
    @Test
    public static void main(String[] ignored) {
        textui.runClasses(PermutationTest.class,
                MovingRotorTest.class,
                MachineTest.class,
                MainTest.class);
    }
}
