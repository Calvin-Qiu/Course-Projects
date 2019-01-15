package enigma;
import static enigma.EnigmaException.*;

/** An Alphabet consisting of an order set of characters.
 * @author Calvin
 */
public class CharacterSet extends Alphabet {

    /** The string of characters allowed in order. */
    private String _cstr;

    /** Constructing a CharacterSet with S. */
    CharacterSet(String s) {
        _cstr = s;
    }

    @Override
    int size() {
        return _cstr.length();
    }

    @Override
    boolean contains(char ch) {
        return _cstr.indexOf(ch) >= 0;
    }

    @Override
    char toChar(int index) {
        if (index >= size()) {
            throw error("character index out of range");
        }
        return _cstr.charAt(index);
    }

    @Override
    int toInt(char ch) {
        if (!contains(ch)) {
            throw error("character not in set");
        }
        return _cstr.indexOf(ch);
    }
}
