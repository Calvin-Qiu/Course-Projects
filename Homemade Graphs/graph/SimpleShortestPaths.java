package graph;

/* See restrictions in Graph.java. */

import java.util.ArrayList;

/** A partial implementation of ShortestPaths that contains the weights of
 *  the vertices and the predecessor edges.   The client needs to
 *  supply only the two-argument getWeight method.
 *  @author Calvin
 */
public abstract class SimpleShortestPaths extends ShortestPaths {

    /** The shortest paths in G from SOURCE. */
    public SimpleShortestPaths(Graph G, int source) {
        this(G, source, 0);
    }

    /** A shortest path in G from SOURCE to DEST. */
    public SimpleShortestPaths(Graph G, int source, int dest) {
        super(G, source, dest);
        _weights = new ArrayList<>();
        _predecessor = new ArrayList<>();
        for (int i = 0; i <= _G.maxVertex(); i++) {
            _weights.add(i, Double.POSITIVE_INFINITY);
            _predecessor.add(i, 0);
        }
    }

    /** Returns the current weight of edge (U, V) in the graph.  If (U, V) is
     *  not in the graph, returns positive infinity. */
    @Override
    protected abstract double getWeight(int u, int v);

    @Override
    public double getWeight(int v) {
        if (_G.contains(v)) {
            return _weights.get(v);
        }
        return Double.POSITIVE_INFINITY;
    }

    @Override
    protected void setWeight(int v, double w) {
        _weights.set(v, w);
    }

    @Override
    public int getPredecessor(int v) {
        return _predecessor.get(v);
    }

    @Override
    protected void setPredecessor(int v, int u) {
        _predecessor.set(v, u);
    }

    /** A list of weights. */
    private ArrayList<Double> _weights;
    /** A list of predecessors. */
    private ArrayList<Integer> _predecessor;

}
