package enigma;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Collection;
import static enigma.EnigmaException.*;

/** Class that represents a complete enigma machine.
 *  @author Calvin
 */
class Machine {

    /** Common alphabet of my rotors. */
    private final Alphabet _alphabet;
    /** The collection of my rotors. */
    private HashMap<String, Rotor> _rotors = new HashMap<>();
    /** The number of rotors I have. */
    private int _numRotors;
    /** The number of pawls I have. */
    private int _pawls;
    /** The ordered rotor array. */
    private ArrayList<Rotor> _rotorArray = new ArrayList<>();
    /** The plug board. */
    private Permutation _plugboard;

    /** A new Enigma machine with alphabet ALPHA, 1 < NUMROTORS rotor slots,
     *  and 0 <= PAWLS < NUMROTORS pawls.  ALLROTORS contains all the
     *  available rotors. */
    Machine(Alphabet alpha, int numRotors, int pawls,
            Collection<Rotor> allRotors) {
        if (numRotors > 1
                && (0 <= pawls && pawls < numRotors)
                && allRotors != null) {
            _alphabet = alpha;
            _numRotors = numRotors;
            _pawls = pawls;
            for (Rotor r : allRotors) {
                _rotors.put(r.name(), r);
            }
        } else {
            throw error("Invalid configuration for Enigma Machine.");
        }
    }

    /** Return the number of rotor slots I have. */
    int numRotors() {
        return _numRotors;
    }

    /** Return the number pawls (and thus rotating rotors) I have. */
    int numPawls() {
        return _pawls;
    }

    /** Set my rotor slots to the rotors named ROTORS from my set of
     *  available rotors (ROTORS[0] names the reflector).
     *  Initially, all rotors are set at their 0 setting. */
    void insertRotors(String[] rotors) {
        _rotorArray = new ArrayList<>();
        int n = numPawls();
        for (String rName : rotors) {
            if (_rotors.containsKey(rName)) {
                Rotor r = _rotors.get(rName);
                if (_rotors.isEmpty() && !r.reflecting()) {
                    throw error("First rotor must be a reflector");
                }
                if (_rotorArray.contains(r)) {
                    throw error("Cannot insert one rotor repeatedly");
                }
                if (r.rotates()) {
                    if (n <= 0) {
                        throw error("Unacceptable number of moving rotors");
                    } else {
                        n -= 1;
                    }
                }
                _rotorArray.add(r);
            } else {
                throw error("Inserting a non-existing rotor %s", rName);
            }
        }
    }

    /** Set my rotors according to SETTING, which must be a string of
     *  numRotors()-1 upper-case letters. The first letter refers to the
     *  leftmost rotor setting (not counting the reflector).  */
    void setRotors(String setting) {
        if (setting.length() == numRotors() - 1) {
            for (int i = 0; i < setting.length(); i++) {
                _rotorArray.get(i + 1).set(setting.charAt(i));
            }
        } else {
            throw error("Invalid setting for Enigma Machine");
        }
    }

    /** Set the plugboard to PLUGBOARD. */
    void setPlugboard(Permutation plugboard) {
        _plugboard = plugboard;
    }

    /** Advance the machine. */
    void machineAdvance() {
        ArrayList<Integer> advancePos = new ArrayList<>();
        for (int i = 0; i < numRotors(); i++) {
            Rotor r = _rotorArray.get(i);
            if (r.rotates()) {
                if (i == numRotors() - 1) {
                    advancePos.add(i);
                } else if (_rotorArray.get(i + 1).atNotch()) {
                    advancePos.add(i);
                } else if (r.atNotch() && _rotorArray.get(i - 1).rotates()) {
                    advancePos.add(i);
                }
            }
        }
        for (Integer i : advancePos) {
            _rotorArray.get(i).advance();
        }
    }

    /** Returns the result of converting the input character C (as an
     *  index in the range 0..alphabet size - 1), after first advancing
     *  the machine. */
    int convert(int c) {
        machineAdvance();
        c = _plugboard.permute(c);
        for (int i = numRotors() - 1; i >= 0; i--) {
            Rotor r = _rotorArray.get(i);
            c = r.convertForward(c);
        }
        for (int i = 1; i < numRotors(); i++) {
            Rotor r = _rotorArray.get(i);
            c = r.convertBackward(c);
        }
        return _plugboard.invert(c);
    }

    /** Returns the encoding/decoding of MSG, updating the state of
     *  the rotors accordingly. */
    String convert(String msg) {
        char[] buffer = new char[msg.length()];
        for (int i = 0; i < msg.length(); i++) {
            char in = msg.charAt(i);
            char out = _alphabet.toChar(convert(_alphabet.toInt(in)));
            buffer[i] = out;
        }
        return new String(buffer);
    }

    /** Return current setting of the machine for testing purposes. */
    String displaySetting() {
        String s = "";
        for (Rotor r : _rotorArray) {
            s += _alphabet.toChar(r.setting());
        }
        return s.substring(1);
    }

}
