package enigma;

import static enigma.EnigmaException.*;

/** Superclass that represents a rotor in the enigma machine.
 *  @author Calvin
 */
class Rotor {

    /** My name. */
    private final String _name;
    /** The permutation implemented by this rotor in its 0 position. */
    private Permutation _permutation;
    /** The current setting of this rotor. */
    private int _setting;
    /** My notches. */
    private String _notches;

    /** A rotor named NAME whose permutation is given by PERM. */
    Rotor(String name, Permutation perm) {
        _name = name;
        _permutation = perm;
        set(0);
    }

    /** Return my name. */
    String name() {
        return _name;
    }

    /** Return my alphabet. */
    Alphabet alphabet() {
        return _permutation.alphabet();
    }

    /** Return my permutation. */
    Permutation permutation() {
        return _permutation;
    }

    /** Return the size of my alphabet. */
    int size() {
        return permutation().size();
    }

    /** Return the notches of this rotor. */
    String notches() {
        return _notches;
    }

    /** Return true iff I have a ratchet and can move. */
    boolean rotates() {
        return false;
    }

    /** Return true iff I reflect. */
    boolean reflecting() {
        return false;
    }

    /** Return my current setting. */
    int setting() {
        return _setting;
    }

    /** Set the notches NS of this rotor. */
    void setNotches(String ns) throws EnigmaException {
        for (int i = 0; i < ns.length(); i++) {
            char n = ns.charAt(i);
            if (!alphabet().contains(n)) {
                throw error("Invalid notches for rotor %s.", name());
            }
        }
        _notches = ns;
    }

    /** Set setting() to POSN.  */
    void set(int posn) throws EnigmaException {
        if (posn < 0 || posn >= size()) {
            throw error("Invalid setting for rotor %s.", name());
        }
        _setting = posn;
    }

    /** Set setting() to character CPOSN. */
    void set(char cposn) throws EnigmaException {
        if (!alphabet().contains(cposn)) {
            throw error("Invalid setting for rotor %s.", name());
        }
        set(alphabet().toInt(cposn));
    }

    /** Return the conversion of P (an integer in the range 0..size()-1)
     *  according to my permutation. */
    int convertForward(int p) {
        return permutation().wrap(
                (permutation().permute(p + setting()) - setting())
        );
    }

    /** Return the conversion of E (an integer in the range 0..size()-1)
     *  according to the inverse of my permutation. */
    int convertBackward(int e) {
        return permutation().wrap(
                permutation().invert(e + setting()) - setting()
        );
    }

    /** Returns true iff I am positioned to allow the rotor to my left
     *  to advance. */
    boolean atNotch() {
        return notches().indexOf(alphabet().toChar(setting())) >= 0;
    }

    /** Advance me one position, if possible. By default, does nothing. */
    void advance() { }

    @Override
    public String toString() {
        return "Rotor " + _name;
    }
}
