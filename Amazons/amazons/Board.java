package amazons;
import java.util.HashMap;
import java.util.Iterator;
import java.util.HashSet;
import java.util.Stack;
import java.util.Collections;
import static amazons.Piece.*;
import static amazons.Square.exists;
import static amazons.Square.sq;


/** The state of an Amazons Game.
 *  @author Calvin
 */
class Board {

    /** The number of squares on a side of the board. */
    static final int SIZE = 10;

    /** Piece whose turn it is (BLACK or WHITE). */
    private Piece _turn;
    /** Cached value of winner on this board, or EMPTY if it has not been
     *  computed. */
    private Piece _winner;
    /** A map from index to contents. */
    private HashMap<Integer, Piece> _content;
    /** A stack of all the moves made. */
    private Stack<Move> _moves;
    /** A map of all white queens. */
    private HashSet<Square> _whiteQueens;
    /** A map of all black queens. */
    private HashSet<Square> _blackQueens;
    /** A map of all spears. */
    private HashSet<Square> _spears;
    /** Initializes a game board with SIZE squares on a side in the
     *  initial position. */
    Board() {
        init();
    }

    /** Initializes a copy of MODEL. */
    Board(Board model) {
        copy(model);
    }

    /** Copies MODEL into me. */
    void copy(Board model) {
        init();
        _moves.addAll(model._moves);
        _turn = model._turn;
        _winner = model._winner;
        _content.putAll(model._content);
        _whiteQueens = new HashSet<>();
        _blackQueens = new HashSet<>();
        _whiteQueens.addAll(model._whiteQueens);
        _blackQueens.addAll(model._blackQueens);
        _spears.addAll(model._spears);
    }

    /** Clears the board to the initial position. */
    void init() {
        _moves = new Stack<>();
        _turn = WHITE;
        _winner = EMPTY;
        _content = new HashMap<>();
        _whiteQueens = new HashSet<>();
        _blackQueens = new HashSet<>();
        _spears = new HashSet<>();
        initContent();
    }

    /** Initialize the content. */
    private void initContent() {
        for (int i = 0; i <= SIZE * SIZE - 1; i++) {
            _content.put(i, EMPTY);
        }
        _whiteQueens.add(sq("d1"));
        _whiteQueens.add(sq("g1"));
        _whiteQueens.add(sq("a4"));
        _whiteQueens.add(sq("j4"));
        _blackQueens.add(sq("a7"));
        _blackQueens.add(sq("j7"));
        _blackQueens.add(sq("d10"));
        _blackQueens.add(sq("g10"));
        put(WHITE, sq("d1"));
        put(WHITE, sq("g1"));
        put(WHITE, sq("a4"));
        put(WHITE, sq("j4"));
        put(BLACK, sq("a7"));
        put(BLACK, sq("j7"));
        put(BLACK, sq("d10"));
        put(BLACK, sq("g10"));
    }

    /** Return the Piece whose move it is (WHITE or BLACK). */
    Piece turn() {
        return _turn;
    }

    /** Return the number of moves (that have not been undone) for this
     *  board. */
    int numMoves() {
        return _moves.size();
    }

    /** Return the winner in the current position, or null if the game is
     *  not yet finished. */
    Piece winner() {
        Iterator<Move> whiteMoves = new LegalMoveIterator(WHITE),
                blackMoves = new LegalMoveIterator(BLACK);
        if (_turn == WHITE && !whiteMoves.hasNext()) {
            _winner = BLACK;
        } else if (_turn == BLACK && !blackMoves.hasNext()) {
            _winner = WHITE;
        } else {
            _winner = null;
        }
        return  _winner;
    }

    /** Return the contents the square at S. */
    final Piece get(Square s) {
        return _content.get(s.index());
    }

    /** Return the contents of the square at (COL, ROW), where
     *  0 <= COL, ROW <= 9. */
    final Piece get(int col, int row) {
        return _content.get(col + row * 10);
    }

    /** Return the contents of the square at COL ROW. */
    final Piece get(char col, char row) {
        return get(col - 'a', row - 1);
    }

    /** Set square S to P. */
    final void put(Piece p, Square s) {
        _content.put(s.index(), p);
    }

    /** Set square (COL, ROW) to P. */
    final void put(Piece p, int col, int row) {
        _content.put(col + row * 10, p);
    }

    /** Set square COL ROW to P. */
    final void put(Piece p, char col, char row) {
        put(p, col - 'a', row - '0');
    }

    /** Return true iff FROM - TO is an unblocked queen move on the current
     *  board, ignoring the contents of ASEMPTY, if it is encountered.
     *  For this to be true, FROM-TO must be a queen move and the
     *  squares along it, other than FROM and ASEMPTY, must be
     *  empty. ASEMPTY may be null, in which case it has no effect. */
    boolean isUnblockedMove(Square from, Square to, Square asEmpty) {
        if (isLegal(from)) {
            if (from.isQueenMove(to)) {
                int dir = from.direction(to);
                Square s = from.queenMove(dir, 1);
                while (s != null && s != to) {
                    if (s != asEmpty) {
                        if (get(s) != EMPTY) {
                            return false;
                        }
                    }
                    s = s.queenMove(dir, 1);
                }
                if (s == null || (s != asEmpty && get(s) != EMPTY)) {
                    return false;
                }
                return true;
            }
        }
        return false;
    }

    /** Return true iff FROM is a valid starting square for a move. */
    boolean isLegal(Square from) {
        return exists(from.row(), from.col());
    }

    /** Return true iff FROM-TO is a valid first part of move, ignoring
     *  spear throwing. */
    boolean isLegal(Square from, Square to) {
        return isUnblockedMove(from, to, null);
    }

    /** Return true iff FROM-TO(SPEAR) is a legal move in the current
     *  position. */
    boolean isLegal(Square from, Square to, Square spear) {
        if (isLegal(from, to)) {
            if (to.isQueenMove(spear)) {
                return isUnblockedMove(to, spear, from);
            }
        }
        return false;
    }

    /** Return true iff MOVE is a legal move in the current
     *  position. */
    boolean isLegal(Move move) {
        if (move != null) {
            Square f = move.from();
            Square t = move.to();
            Square s = move.spear();
            if (f != null && t != null && s != null) {
                return isLegal(f, t, s);
            }
        }
        return false;

    }

    /** Move FROM-TO(SPEAR), assuming this is a legal move. */
    void makeMove(Square from, Square to, Square spear) {
        Piece moved = get(from);
        if (moved == WHITE) {
            _whiteQueens.add(to);
            _whiteQueens.remove(from);
        } else {
            _blackQueens.add(to);
            _blackQueens.remove(from);
        }
        put(moved, to);
        put(EMPTY, from);
        put(SPEAR, spear);
        _spears.add(spear);
    }

    /** Move according to MOVE, assuming it is a legal move. */
    void makeMove(Move move) {
        makeMove(move.from(), move.to(), move.spear());
        _moves.push(move);
        _turn = (_turn == WHITE) ? BLACK : WHITE;
    }

    /** Undo one move.  Has no effect on the initial board. */
    void undo() {
        if (!_moves.empty()) {
            Move lastMove = _moves.pop();
            Square from = lastMove.from(), to = lastMove.to(),
                    spear = lastMove.spear();
            Piece moved = get(to);
            put(moved, from);
            put(EMPTY, to);
            if (moved == WHITE) {
                _whiteQueens.remove(to);
                _whiteQueens.add(from);
            } else {
                _blackQueens.remove(to);
                _blackQueens.add(from);
            }
            _spears.remove(spear);
            if (get(spear) == SPEAR) {
                put(EMPTY, spear);
            }
            _turn = (_turn == WHITE) ? BLACK : WHITE;
        }
    }

    /**  Return the queens of SIDE. */
    HashSet<Square> queens(Piece side) {
        if (side == WHITE) {
            return _whiteQueens;
        } else if (side == BLACK) {
            return _blackQueens;
        }
        return null;
    }

    /** Return the spears. */
    HashSet<Square> spears() {
        return _spears;
    }

    /** Return an Iterator over the Squares that are reachable by an
     *  unblocked queen move from FROM. Does not pay attention to what
     *  piece (if any) is on FROM, nor to whether the game is finished.
     *  Treats square ASEMPTY (if non-null) as if it were EMPTY.  (This
     *  feature is useful when looking for Moves, because after moving a
     *  piece, one wants to treat the Square it came from as empty for
     *  purposes of spear throwing.) */
    Iterator<Square> reachableFrom(Square from, Square asEmpty) {
        return new ReachableFromIterator(from, asEmpty);
    }

    /** Return an Iterator over all legal moves on the current board. */
    Iterator<Move> legalMoves() {
        return new LegalMoveIterator(_turn);
    }

    /** Return an Iterator over all legal moves on the current board for
     *  SIDE (regardless of whose turn it is). */
    Iterator<Move> legalMoves(Piece side) {
        return new LegalMoveIterator(side);
    }

    /** An iterator used by reachableFrom. */
    private class ReachableFromIterator implements Iterator<Square> {

        /** Iterator of all squares reachable by queen move from FROM,
         *  treating ASEMPTY as empty. */
        ReachableFromIterator(Square from, Square asEmpty) {
            _from = from;
            _dir = 0;
            _steps = 0;
            _asEmpty = asEmpty;
        }

        @Override
        public boolean hasNext() {
            toNext();
            return _dir < 8;
        }

        @Override
        public Square next() {
            return _from.queenMove(_dir, _steps);
        }

        /** Advance _dir and _steps, so that the next valid Square is
         *  _steps steps in direction _dir from _from. */
        private void toNext() {
            _steps++;
            while (_dir < 8 && _from.queenMove(_dir, _steps) == null) {
                _steps = 1;
                _dir += 1;
            }
            if (_dir < 8 && _from.queenMove(_dir, _steps) != null) {
                Square to = _from.queenMove(_dir, _steps);
                if (!isUnblockedMove(_from, to, _asEmpty)) {
                    _steps = 0;
                    _dir++;
                    toNext();
                }
            }
        }

        /** Starting square. */
        private Square _from;
        /** Current direction. */
        private int _dir;
        /** Current distance. */
        private int _steps;
        /** Square treated as empty. */
        private Square _asEmpty;
    }

    /** An iterator used by legalMoves. */
    private class LegalMoveIterator implements Iterator<Move> {

        /** All legal moves for SIDE (WHITE or BLACK). */
        LegalMoveIterator(Piece side) {
            if (side == WHITE) {
                _startingSquares = _whiteQueens.toArray();
            } else {
                _startingSquares = _blackQueens.toArray();
            }
            _spearThrows = NO_SQUARES;
            _pieceMoves = NO_SQUARES;
            _fromPiece = side;
        }

        @Override
        public boolean hasNext() {
            toNext();
            return _hasNext;
        }

        @Override
        public Move next() {
            return Move.mv(_start, _nextSquare, _nextSpear);
        }

        /** Advance so that the next valid Move is
         *  _start-_nextSquare(sp), where sp is the next value of
         *  _spearThrows. */
        private void toNext() {
            if (_spearThrows.hasNext()) {
                _nextSpear = _spearThrows.next();
                if (!isLegal(_start, _nextSquare, _nextSpear)) {
                    toNext();
                }
            } else if (_pieceMoves.hasNext()) {
                _nextSquare = _pieceMoves.next();
                _spearThrows = new ReachableFromIterator(_nextSquare, _start);
                toNext();
            } else if (index < _startingSquares.length) {
                _start = (Square) _startingSquares[index];
                _pieceMoves = new ReachableFromIterator(_start, null);
                index++;
                toNext();
            } else {
                _hasNext = false;
            }
        }

        /** Whether hasNext. */
        private boolean _hasNext = true;
        /** Color of side whose moves we are iterating. */
        private Piece _fromPiece;
        /** Current starting square. */
        private Square _start;
        /** Remaining starting squares to consider. */
        private Object[] _startingSquares;
        /** Index in the array. */
        private int index = 0;
        /** Current piece's new position. */
        private Square _nextSquare;
        /** Current spear position. */
        private Square _nextSpear;
        /** Remaining moves from _start to consider. */
        private Iterator<Square> _pieceMoves;
        /** Remaining spear throws from _piece to consider. */
        private Iterator<Square> _spearThrows;
    }

    /** String size needed. */
    private static final int STR_SIZE = 140;

    @Override
    public String toString() {
        StringBuilder result = new StringBuilder(STR_SIZE);
        for (int row = SIZE - 1; row >= 0; row--) {
            int col = 0;
            result.append("  ");
            for (; col < SIZE; col++) {
                result.append(" ");
                Piece p = get(col, row);
                switch (p) {
                case EMPTY:
                    result.append("-");
                    break;
                case BLACK:
                    result.append("B");
                    break;
                case WHITE:
                    result.append("W");
                    break;
                case SPEAR:
                    result.append("S");
                    break;
                default:
                    break;
                }
                if (col == SIZE - 1) {
                    result.append("\n");
                }
            }
        }
        return result.toString();
    }

    /** An empty iterator for initialization. */
    private static final Iterator<Square> NO_SQUARES =
        Collections.emptyIterator();

}
