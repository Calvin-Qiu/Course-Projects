package graph;

import java.util.ArrayList;

/** A simple BFT.
 * @author Calvin */
public class SimpleBFT extends BreadthFirstTraversal {
    /** A simple BFT on G. */
    SimpleBFT(Graph G) {
        super(G);
        route = new ArrayList<>();
    }

    @Override
    protected boolean visit(int u) {
        route.add(u);
        return true;
    }

    /** The route taken. */
    protected ArrayList<Integer> route;
}
