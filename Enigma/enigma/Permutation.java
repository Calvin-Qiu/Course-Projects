package enigma;

import java.util.HashMap;
import java.util.Map;


/** Represents a permutation of a range of integers starting at 0 corresponding
 *  to the characters of an alphabet.
 *  @author Calvin
 */
class Permutation {

    /** Set this Permutation to that specified by CYCLES, a string in the
     *  form "(cccc) (cc) ..." where the c's are characters in ALPHABET, which
     *  is interpreted as a permutation in cycle notation.  Characters in the
     *  alphabet that are not included in any cycle map to themselves.
     *  Whitespace is ignored. */

    /** Alphabet of this permutation. */
    private Alphabet _alphabet;
    /** Foward map of this permutation. */
    private HashMap<Integer, Integer> _map = new HashMap<>();
    /** Backward map of this permutation. */
    private HashMap<Integer, Integer> _inverse = new HashMap<>();

    /** Construct a permutation from CYCLES and ALPHABET. */
    Permutation(String cycles, Alphabet alphabet) {
        _alphabet = alphabet;
        initMaps(cycles);
    }

    /** Initialize the CYCLES. */
    private void initMaps(String cycles) {
        String cleanCycles = cycles.replaceAll("\\s", "");
        cleanCycles = cleanCycles.replace(")", "@");
        cleanCycles = cleanCycles.replace("(", "@");
        String[] cyclesArray = cleanCycles.split("@");
        for (String cycle: cyclesArray) {
            if (cycle.length() > 0) {
                toMap(cycle);
            }
        }
        makeInverse();
    }

    /** Add the cycle c0->c1->...->cm->c0 to the permutation, where CYCLE is
     *  c0c1...cm. */
    private void toMap(String cycle) {
        for (int i = 0; i < cycle.length() - 1; i++) {
            Integer input = _alphabet.toInt(cycle.charAt(i));
            Integer output = _alphabet.toInt(cycle.charAt(i + 1));
            _map.put(input, output);
        }
        Integer i = _alphabet.toInt(cycle.charAt(cycle.length() - 1));
        Integer o = _alphabet.toInt(cycle.charAt(0));
        _map.put(i, o);
    }

    /** Create the inverse mapping. */
    private void makeInverse() {
        if (_map != null) {
            for (Map.Entry<Integer, Integer> e : _map.entrySet()) {
                _inverse.put(e.getValue(), e.getKey());
            }
        }
    }

    /** Return the value of P modulo the size of this permutation. */
    final int wrap(int p) {
        int r = p % size();
        if (r < 0) {
            r += size();
        }
        return r;
    }

    /** Returns the size of the alphabet I permute. */
    int size() {
        return _alphabet.size();
    }

    /** Return the result of applying this permutation to P modulo the
     *  alphabet size. */
    int permute(int p) {
        int index = wrap(p);
        if (_map != null && _map.containsKey(index)) {
            return _map.get(index);
        } else {
            return index;
        }
    }

    /** Return the result of applying the inverse of this permutation
     *  to  C modulo the alphabet size. */
    int invert(int c) {
        int index = wrap(c);
        if (_inverse != null && _inverse.containsKey(index)) {
            return _inverse.get(index);
        } else {
            return index;
        }
    }

    /** Return the result of applying this permutation to the index of P
     *  in ALPHABET, and converting the result to a character of ALPHABET. */
    char permute(char p) {
        return _alphabet.toChar(permute(_alphabet.toInt(p)));
    }

    /** Return the result of applying the inverse of this permutation to C. */
    int invert(char c) {
        return _alphabet.toChar(invert(_alphabet.toInt(c)));
    }

    /** Return the alphabet used to initialize this Permutation. */
    Alphabet alphabet() {
        return _alphabet;
    }

    /** Return true iff this permutation is a derangement (i.e., a
     *  permutation for which no value maps to itself). */
    boolean derangement() {
        for (Map.Entry<Integer, Integer> e: _map.entrySet()) {
            if (e.getValue().equals(e.getKey())) {
                return false;
            }
        }
        return true;
    }
}
