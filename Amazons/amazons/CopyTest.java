package amazons;
import org.junit.Test;
import static org.junit.Assert.*;

/** Undo Test.*/
public class CopyTest {
    @Test
    public void copyTest() {
        Board b = new Board();
        b.makeMove(Move.mv("a7 c9 e9"));
        b.makeMove(Move.mv("c9 d8 e8"));
        b.makeMove(Move.mv("d8 e7 h4"));
        Board copy = new Board(b);
        assertEquals(copy.winner(), null);
        assertEquals(copy.numMoves(), 3);
        assertEquals(copy.get(Square.sq("e7")), Piece.BLACK);
    }

    @Test
    public void copycopyTest() {
        Board b = new Board();
        b.makeMove(Move.mv("a7 c9 e9"));
        b.makeMove(Move.mv("c9 d8 e8"));
        b.makeMove(Move.mv("d8 e7 h4"));
        Board copy = new Board(b);
        Board copycopy = new Board(copy);
        assertEquals(copycopy.winner(), null);
        assertEquals(copycopy.numMoves(), 3);
        assertEquals(copycopy.get(Square.sq("e7")), Piece.BLACK);
    }
}
