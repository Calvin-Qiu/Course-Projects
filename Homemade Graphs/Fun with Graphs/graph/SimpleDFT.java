package graph;

import java.util.ArrayList;

/** A simple DFT.
 * @author Calvin */
class SimpleDFT extends DepthFirstTraversal {
    /** A simple DFT on G. */
    public SimpleDFT(Graph G) {
        super(G);
        _route = new ArrayList<>();
    }

    @Override
    public boolean postVisit(int v) {
        _route.add(v);
        return true;
    }

    @Override
    protected boolean shouldPostVisit(int v) {
        return true;
    }

    /** The route taken. */
    private ArrayList<Integer> _route;

    /** Return my route. */
    protected ArrayList<Integer> getRoute() {
        return _route;
    }
}
