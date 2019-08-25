package graph;

/* See restrictions in Graph.java. */

import java.util.TreeSet;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Comparator;

/** The shortest paths through an edge-weighted graph.
 *  By overriding methods getWeight, setWeight, getPredecessor, and
 *  setPredecessor, the client can determine how to represent the weighting
 *  and the search results.  By overriding estimatedDistance, clients
 *  can search for paths to specific destinations using A* search.
 *  @author Calvin
 */
public abstract class ShortestPaths {

    /** The shortest paths in G from SOURCE. */
    public ShortestPaths(Graph G, int source) {
        this(G, source, 0);
    }

    /** A shortest path in G from SOURCE to DEST. */
    public ShortestPaths(Graph G, int source, int dest) {
        _G = G;
        _source = source;
        _dest = dest;
        _fringe = new TreeSet<>(new DistanceComparator());
        _visited = new ArrayList<>();
    }



    /** Initialize the shortest paths.  Must be called before using
     *  getWeight, getPredecessor, and pathTo. */
    public void setPaths() {
        _fringe.add(_source);
        setWeight(_source, 0);
    }

    /** Returns the starting vertex. */
    public int getSource() {
        return _source;
    }

    /** Returns the target vertex, or 0 if there is none. */
    public int getDest() {
        return _dest;
    }

    /** Returns the current weight of vertex V in the graph.  If V is
     *  not in the graph, returns positive infinity. */
    public abstract double getWeight(int v);

    /** Set getWeight(V) to W. Assumes V is in the graph. */
    protected abstract void setWeight(int v, double w);

    /** Returns the current predecessor vertex of vertex V in the graph, or 0 if
     *  V is not in the graph or has no predecessor. */
    public abstract int getPredecessor(int v);

    /** Set getPredecessor(V) to U. */
    protected abstract void setPredecessor(int v, int u);

    /** Returns an estimated heuristic weight of the shortest path from vertex
     *  V to the destination vertex (if any).  This is assumed to be less
     *  than the actual weight, and is 0 by default. */
    protected double estimatedDistance(int v) {
        return 0.0;
    }

    /** Returns the current weight of edge (U, V) in the graph.  If (U, V) is
     *  not in the graph, returns positive infinity. */
    protected abstract double getWeight(int u, int v);

    /** Returns a list of vertices starting at _source and ending
     *  at V that represents a shortest path to V.  Invalid if there is a
     *  destination vertex other than V. */
    public List<Integer> pathTo(int v) {
        if (_dest != v) {
            return null;
        }
        ArrayList<Integer> path = new ArrayList<>();
        setPaths();
        while (true) {
            int u = _fringe.pollFirst();
            if (!_visited.contains(u)) {
                _visited.add(u);
                if (u == getDest()) {
                    break;
                }
                for (int s : _G.successors(u)) {
                    if (_visited.contains(s)) {
                        continue;
                    }
                    double d = getWeight(u) + getWeight(u, s);
                    if (getWeight(s) > d) {
                        setWeight(s, d);
                        setPredecessor(s, u);
                        _fringe.remove(s);
                    }
                    _fringe.add(s);
                }
            }
            if (_fringe.isEmpty()) {
                return null;
            }
        }
        for (int u = getDest(); u != getSource(); u = getPredecessor(u)) {
            path.add(u);
        }
        path.add(getSource());
        Collections.reverse(path);
        return path;
    }

    /** Returns a list of vertices starting at the source and ending at the
     *  destination vertex. Invalid if the destination is not specified. */
    public List<Integer> pathTo() {
        return pathTo(getDest());
    }

    /** The comparator. */
    private class DistanceComparator implements Comparator<Integer>  {
        /** Compare vertices X and Y.
         *  Returns an integer indicating desired sequence. */
        public int compare(Integer x, Integer y) {
            double d = ShortestPaths.this.getWeight(x)
                    - ShortestPaths.this.getWeight(y)
                    + ShortestPaths.this.estimatedDistance(x)
                    - ShortestPaths.this.estimatedDistance(y);
            return d > 0 ? 1 : d == 0 ? 0 : -1;
        }
    }

    /** The graph being searched. */
    protected final Graph _G;
    /** The starting vertex. */
    private final int _source;
    /** The target vertex. */
    private final int _dest;
    /** The fringe. */
    private final TreeSet<Integer> _fringe;
    /** A list of visited vertices. */
    private ArrayList<Integer> _visited;
}
