package amazons;
import org.junit.Test;
import static org.junit.Assert.*;

/** Undo Test.*/
public class UndoTest {
    @Test
    public void undoTest() {
        Board b = new Board();
        b.makeMove(Move.mv("a7 c9 e9"));
        b.makeMove(Move.mv("c9 d8 e8"));
        b.makeMove(Move.mv("d8 e7 h4"));
        b.undo();
        b.undo();
        b.undo();
        assertEquals(Piece.EMPTY, b.get(Square.sq("e7")));
        assertEquals(Piece.EMPTY, b.get(Square.sq("h4")));
        assertEquals(Piece.BLACK, b.get(Square.sq("a7")));
    }
}
