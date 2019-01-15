package enigma;

import org.junit.Test;

public class MainTest {

    @Test
    public void mainCorrect() {
        Main.main("../testing/correct/default.conf",
                "../testing/correct/trivial.inp");
    }

    @Test
    public void mainCorrect1() {
        Main.main("../testing/correct/default.conf",
                "../testing/correct/trivial1.inp");
    }

    @Test
    public void mainPoet() {
        Main.main("../testing/correct/default.conf",
                "../testing/correct/poet.inp");
    }
}
