package enigma;

import org.junit.Test;
import static org.junit.Assert.*;

import java.util.ArrayList;

import static enigma.TestUtils.*;

public class MachineTest {

    /** Machine used for test. */
    private Machine m;

    /** Rotors used for test. */
    static Rotor r1 = new Reflector("B",
            new Permutation(NAVALA.get("B"), UPPER));
    static Rotor r2 = new FixedRotor("Beta",
            new Permutation(NAVALA.get("Beta"), UPPER));
    static Rotor r3 = new MovingRotor("III",
            new Permutation(NAVALA.get("III"), UPPER), "V");
    static Rotor r4 = new MovingRotor("IV",
            new Permutation(NAVALA.get("IV"), UPPER), "J");
    static Rotor r5 = new MovingRotor("I",
            new Permutation(NAVALA.get("I"), UPPER), "Q");
    static Permutation plugboard = new Permutation("(YF) (ZH)", UPPER);

    /** Set the test Machine. */
    private void setMachine() {
        ArrayList<Rotor> rotors = new ArrayList<>();
        rotors.add(r1);
        rotors.add(r2);
        rotors.add(r3);
        rotors.add(r4);
        rotors.add(r5);
        r2.set('A');
        r3.set('X');
        r4.set('L');
        r5.set('E');
        m = new Machine(UPPER, 5, 3, rotors);
        m.setPlugboard(plugboard);
    }

    /* Test for converting. */
    @Test
    public void convertTest() {
        setMachine();
        String[] rotorOrder = {"B", "Beta", "III", "IV", "I"};
        m.insertRotors(rotorOrder);
        assertEquals(25, m.convert(24));
        for (int i = 0; i < 12; i++) {
            m.convert("A");
        }
        assertEquals("AXMR", m.displaySetting());
    }
}
