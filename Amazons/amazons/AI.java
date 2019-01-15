package amazons;

import java.util.Iterator;

import static java.lang.Math.*;

import static amazons.Piece.*;

/** A Player that automatically generates moves.
 *  @author Calvin
 */
class AI extends Player {

    /** A position magnitude indicating a win (for white if positive, black
     *  if negative). */
    private static final int WINNING_VALUE = Integer.MAX_VALUE - 1;
    /** A magnitude greater than a normal value. */
    private static final int INFTY = Integer.MAX_VALUE;
    /** A constant. */
    private static final int START = 2;
    /** A constant. */
    private static final int BEGINING = 10;
    /** A constant. */
    private static final int MIDDLE  = 30;
    /** A constant. */
    private static final int HALF = 60;
    /** A constant. */
    private static final int FINAL = 70;
    /** A new AI with no piece or controller (intended to produce
     *  a template). */
    AI() {
        this(null, null);
    }

    /** A new AI playing PIECE under control of CONTROLLER. */
    AI(Piece piece, Controller controller) {
        super(piece, controller);
    }

    @Override
    Player create(Piece piece, Controller controller) {
        return new AI(piece, controller);
    }

    @Override
    String myMove() {
        Move move = findMove();
        _controller.reportMove(move);
        return move.toString();
    }

    /** Return a move for me from the current position, assuming there
     *  is a move. */
    private Move findMove() {
        Board b = new Board(board());
        if (_myPiece == WHITE) {
            findMove(b, maxDepth(b), true, 1, -INFTY, INFTY);
        } else {
            findMove(b, maxDepth(b), true, -1, -INFTY, INFTY);
        }
        return _lastFoundMove;
    }

    /** The move found by the last call to one of the ...FindMove methods
     *  below. */
    private Move _lastFoundMove;

    /** Find a move from position BOARD and return its value, recording
     *  the move found in _lastFoundMove iff SAVEMOVE. The move
     *  should have maximal value or have value > BETA if SENSE==1,
     *  and minimal value or value < ALPHA if SENSE==-1. Searches up to
     *  DEPTH levels.  Searching at level 0 simply returns a static estimate
     *  of the board value and does not set _lastMoveFound. */
    private int findMove(Board board, int depth, boolean saveMove, int sense,
                         int alpha, int beta) {
        if (depth == 0 || board.winner() != null) {
            return staticScore(board);
        }
        Iterator<Move> moves = board.legalMoves((sense == 1) ? WHITE : BLACK);
        Move bestMove = null;
        int bestVal = INFTY * sense * -1;
        while (moves.hasNext()) {
            Move m = moves.next();
            board.makeMove(m);
            int val = findMove(board, depth - 1, false,
                    sense * -1, alpha, beta);
            board.undo();
            if (sense == 1) {
                if (val > bestVal) {
                    bestMove = m;
                    bestVal = val;
                    alpha = max(alpha, bestVal);
                    if (alpha >= beta) {
                        break;
                    }
                }
            } else {
                if (val < bestVal) {
                    bestMove = m;
                    bestVal = val;
                    beta = min(beta, bestVal);
                    if (beta <= alpha) {
                        break;
                    }
                }
            }
        }
        if (saveMove) {
            _lastFoundMove = bestMove;
        }
        return bestVal;
    }

    /** A constant. */
    private static final double DENOM = 1200.0;

    /** Return a heuristically determined maximum search depth
     *  based on characteristics of BOARD. */
    private int maxDepth(Board board) {
        int N = board.numMoves();
        return 1 + (int) (N * N / DENOM);
    }

    /** Weight. */
    private static final int WEIGHT1 = 2;
    /** Weight. */
    private static final int WEIGHT2 = 3;
    /** Weight. */
    private static final int WEIGHT3 = 5;

    /** Return a heuristic value for BOARD. */
    private int staticScore(Board board) {
        Piece winner = board.winner();
        if (winner == BLACK) {
            return -WINNING_VALUE;
        } else if (winner == WHITE) {
            return WINNING_VALUE;
        } else {
            int n = board.numMoves();
            if (n <= START) {
                return reachableDifference(board);
            }
            if (n < BEGINING) {
                int e = enclosedDifference(board);
                int s = sparsenessDifference(board) * WEIGHT1;
                int r = reachableDifference(board) * WEIGHT2;
                return  e + s + r;
            }
            if (n < MIDDLE) {
                int r = reachableDifference(board) * WEIGHT2;
                int s = sparsenessDifference(board);
                return r + s;
            }
            if (n < HALF) {
                int r = reachableDifference(board) * WEIGHT3;
                int s = sparsenessDifference(board);
                return r + s;
            } else {
                return legalMovesDifference(board);
            }
        }
    }

    /** Magnitude bound. */
    private static final int MAGNITUDE = 100;

    /** Return how much black is more enclosed than white on BOARD. */
    private int enclosedDifference(Board board) {
        int e = 0;
        for (Square b : board.queens(BLACK)) {
            e += enclose(b, board);
        }
        for (Square w : board.queens(WHITE)) {
            e -= enclose(w, board);
        }
        while (abs(e) > MAGNITUDE) {
            e /= 10;
        }
        return e;
    }

    /** Return difference between how many squares can be reached on BOARD. */
    private int reachableDifference(Board board) {
        int r = 0;
        for (Square s : board.queens(WHITE)) {
            Iterator<Square> whiteReach = board.reachableFrom(s, null);
            int j = 0;
            while (whiteReach.hasNext()) {
                r++;
                j++;
            }
            if (j == 0) {
                r -= 10;
            }
        }
        for (Square s : board.queens(BLACK)) {
            Iterator<Square> blackReach = board.reachableFrom(s, null);
            int j = 0;
            while (blackReach.hasNext()) {
                r--;
                j++;
            }
            if (j == 0) {
                r += 10;
            }
        }
        return r;
    }

    /** Return the number of legal white moves
     * - the number of legal blackmoves on BOARD. */
    private int legalMovesDifference(Board board) {
        int d = 0;
        Iterator<Move> whiteMoves = board.legalMoves(WHITE);
        Iterator<Move> blackMoves = board.legalMoves(BLACK);
        while (whiteMoves.hasNext()) {
            d++;
        }
        while (blackMoves.hasNext()) {
            d--;
        }
        return d;
    }

    /** The weight for sparseness. */
    private static final int SPARSE_WEIGHT = 5;
    /** Return the white sparseness - black sparseness on BOARD. */
    private int sparsenessDifference(Board board) {
        int[] sumWhitePos = {0, 0};
        int[] sumBlackPos = {0, 0};
        int whiteSparseness = 0;
        int blackSparseness = 0;
        for (Square s : board.queens(WHITE)) {
            sumWhitePos[0] += s.col();
            sumWhitePos[1] += s.row();
        }
        for (Square s : board.queens(BLACK)) {
            sumBlackPos[0] += s.col();
            sumBlackPos[1] += s.row();
        }
        Square whiteC = Square.sq(sumWhitePos[0] / 4, sumWhitePos[1] / 4);
        Square blackC = Square.sq(sumBlackPos[0] / 4, sumBlackPos[1] / 4);
        for (Square w : board.queens(WHITE)) {
            whiteSparseness += distance(w, whiteC);
        }
        for (Square b : board.queens(BLACK)) {
            blackSparseness += distance(b, blackC);
        }
        int s = (whiteSparseness - blackSparseness);
        return s * SPARSE_WEIGHT;
    }

    /** A constant for computation. */
    private static final int ENCLOSE_WEIGHT = 200;

    /** Return how much a queen S is bounded on BOARD. */
    private double enclose(Square s, Board board) {
        double whiteWeight, blackWeight, spearWeight, enclosed;
        enclosed = 0;
        spearWeight = 15;
        whiteWeight = (board.get(s) == WHITE) ? 2 : 6;
        blackWeight = (board.get(s) == BLACK) ? 2 : 6;
        for (Square w : board.queens(WHITE)) {
            if (s != w) {
                enclosed += whiteWeight
                        / (distance(s, w) * distance(s, w));
            }
        }
        for (Square b : board.queens(BLACK)) {
            if (s != b) {
                enclosed += blackWeight
                        / (distance(s, b) * distance(s, b));
            }
        }
        for (Square sp : board.spears()) {
            if (s != sp) {
                enclosed += spearWeight
                        / (distance(s, sp) * distance(s, sp));
            }
        }
        return enclosed;
    }

    /** Return distance between two squares S1, S2. */
    private double distance(Square s1, Square s2) {
        return sqrt((s1.col() - s2.col()) * (s1.col() - s2.col())
                + (s1.row() - s2.row()) * (s1.row() - s2.row()));
    }

}
