package enigma;

import java.io.File;
import java.io.IOException;
import java.io.PrintStream;

import java.util.ArrayList;
import java.util.NoSuchElementException;
import java.util.Scanner;

import static enigma.EnigmaException.*;

/** Enigma simulator.
 *  @author Calvin
 */
public final class Main {

    /** Process a sequence of encryptions and decryptions, as
     *  specified by ARGS, where 1 <= ARGS.length <= 3.
     *  ARGS[0] is the name of a configuration file.
     *  ARGS[1] is optional; when present, it names an input file
     *  containing messages.  Otherwise, input comes from the standard
     *  input.  ARGS[2] is optional; when present, it names an output
     *  file for processed messages.  Otherwise, output goes to the
     *  standard output. Exits normally if there are no errors in the input;
     *  otherwise with code 1. */
    public static void main(String... args) {
        try {
            new Main(args).process();
            return;
        } catch (EnigmaException excp) {
            System.err.printf("Error: %s%n", excp.getMessage());
        }
        System.exit(1);
    }

    /** Check ARGS and open the necessary files (see comment on main). */
    Main(String[] args) {
        if (args.length < 1 || args.length > 3) {
            throw error("Only 1, 2, or 3 command-line arguments allowed");
        }

        _config = getInput(args[0]);

        if (args.length > 1) {
            _input = getInput(args[1]);
        } else {
            _input = new Scanner(System.in);
        }

        if (args.length > 2) {
            _output = getOutput(args[2]);
        } else {
            _output = System.out;
        }
    }

    /** Return a Scanner reading from the file named NAME. */
    private Scanner getInput(String name) {
        try {
            return new Scanner(new File(name));
        } catch (IOException excp) {
            throw error("could not open %s", name);
        }
    }

    /** Return a PrintStream writing to the file named NAME. */
    private PrintStream getOutput(String name) {
        try {
            return new PrintStream(new File(name));
        } catch (IOException excp) {
            throw error("could not open %s", name);
        }
    }

    /** Configure an Enigma machine from the contents of configuration
     *  file _config and apply it to the messages in _input, sending the
     *  results to _output. */
    private void process() {
        Machine enigma = readConfig();
        String s = _input.nextLine();
        int n = enigma.numRotors();
        checksetting(s, n);
        while (_input.hasNext()) {
            checksetting(s, n);
            setUp(enigma, s);
            while (_input.hasNextLine()) {
                s = _input.nextLine();
                if (!s.startsWith("*")) {
                    String buffer = "";
                    String line = s.toUpperCase();
                    String l = line.replaceAll("\\s", "");
                    buffer += enigma.convert(l);
                    printMessageLine(buffer);
                } else {
                    break;
                }
            }
        }
    }

    /** Return an Enigma machine configured from the contents of configuration
     *  file _config. */
    private Machine readConfig() {
        try {
            if (!_config.hasNext("(([^()*-])+|([^()*-][-][^()*-]))")) {
                throw error("invalid alphabet description");
            }
            String alpha = _config.next();
            if (alpha.indexOf('-') >= 0) {
                char c1 = alpha.charAt(0);
                char c2 = alpha.charAt(2);
                if (c1 > c2) {
                    throw error("invalid character range");
                }
                _alphabet = new CharacterRange(c1, c2);
            } else {
                _alphabet = new CharacterSet(alpha);
            }
            int slots = _config.nextInt();
            int pawls = _config.nextInt();
            ArrayList<Rotor> rotorList = new ArrayList<>();
            while (_config.hasNext()) {
                Rotor r = readRotor();
                rotorList.add(r);
            }
            return new Machine(_alphabet, slots, pawls, rotorList);
        } catch (NoSuchElementException excp) {
            throw error("configuration file truncated");
        }
    }

    /** Return a rotor, reading its description from _config. */
    private Rotor readRotor() {
        try {
            String name = _config.next("[^()]+").toUpperCase();
            String typeAndNotches = _config.next("([^()*-]|[^()*-]+)");
            int type = typeAndNotches.charAt(0);
            String notches = typeAndNotches.substring(1);
            String perm = "";
            while (_config.hasNext("([(]([^()*-])+[)])+")) {
                perm = perm + _config.next();
            }
            Permutation p = new Permutation(perm, _alphabet);
            Rotor r;
            if (type == 'R') {
                r = new Reflector(name, p);
            } else if (type == 'M') {
                r = new MovingRotor(name, p, notches);
            } else if (type == 'N') {
                r = new FixedRotor(name, p);
            } else {
                throw error("Invalid rotor type for %s", name);
            }
            r.setNotches(notches);
            return  r;
        } catch (NoSuchElementException excp) {
            throw error("bad rotor description");
        }
    }

    /** Set M according to the specification given on SETTINGS,
     *  which must have the format specified in the assignment. */
    private void setUp(Machine M, String settings) {
        Scanner s = new Scanner(settings);
        String rotorSetting = "";
        int n = M.numRotors();
        String[] rotors = new String[n];
        s.next("[*]");
        for (int i = 0; i < n; i++) {
            String rName = s.next("[^()]+");
            rotors[i] = rName;
        }
        if (s.hasNext("([^()*-])+")) {
            rotorSetting = s.next();
        }
        String plugboard = "";
        while (s.hasNext("([(]([^()*-])+[)])+")) {
            plugboard = plugboard + s.next();
        }
        M.insertRotors(rotors);
        if (!rotorSetting.equals("")) {
            M.setRotors(rotorSetting);
        }
        M.setPlugboard(new Permutation(plugboard, _alphabet));
    }

    /** Print MSG in groups of five (except that the last group may
     *  have fewer letters). */
    private void printMessageLine(String msg) {
        int len = msg.length();
        for (int i = 0; i < len; i++) {
            _output.print(msg.charAt(i));
            if ((i + 1) % 5 == 0 && i != len - 1) {
                _output.print(' ');
            }
        }
        _output.println();
    }

    /** Check the setting line S for format,
     * which must contain N rotor descriptions. */
    private void checksetting(String s, int n) {
        String p;
        p = String.format("([*]((\\s)+[^()]+){%s}?(\\s)+([^()*-]){%s}"
                        + "((\\s)*([(]([^()*-])+[)])+)*(\\s)*)",
                Integer.toString(n), Integer.toString(n - 1));
        if (!s.matches(p)) {
            throw error("Invalid setting for Enigma %s", s);
        }
    }



    /** Alphabet used in this machine. */
    private Alphabet _alphabet;

    /** Source of input messages. */
    private Scanner _input;

    /** Source of machine configuration. */
    private Scanner _config;

    /** File for encoded/decoded messages. */
    private PrintStream _output;
}
