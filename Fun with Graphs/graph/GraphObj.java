package graph;

/* See restrictions in Graph.java. */

import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;

/** A partial implementation of Graph containing elements common to
 *  directed and undirected graphs.
 *
 *  @author Calvin
 */
abstract class GraphObj extends Graph {

    /** A new, empty Graph. */
    GraphObj() {
        _vertices = new ArrayList<>();
        _vertices.add(new ArrayList<>());
        _edges = new ArrayList<>();
        _edges.add(null);
        _edgeSize = 0;
    }

    @Override
    public int vertexSize() {
        return _vertices.get(0).size();
    }

    @Override
    public int maxVertex() {
        return Collections.max(_vertices.get(0));
    }

    @Override
    public int edgeSize() {
        return _edgeSize;
    }

    @Override
    public abstract boolean isDirected();

    @Override
    public int outDegree(int v) {
        if (!contains(v)) {
            return 0;
        }
        int i = 0;
        Iterator<Integer> s = successors(v);
        while (s.hasNext()) {
            s.next();
            i++;
        }
        return i;
    }

    @Override
    public abstract int inDegree(int v);

    @Override
    public boolean contains(int u) {
        return _vertices.get(0).contains(u);
    }

    @Override
    public boolean contains(int u, int v) {
        if (contains(u) && contains(v)) {
            ArrayList<Integer> es = _vertices.get(u);
            for (int e : es) {
                if (isDirected()) {
                    if (_edges.get(e)[1] == v) {
                        return true;
                    }
                } else {
                    int in = _edges.get(e)[0];
                    int out = _edges.get(e)[1];
                    if (in == u && out == v) {
                        return true;
                    } else if (in == v && out == u) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    @Override
    public int add() {
        for (int i = 1; i < _vertices.size(); i++) {
            if (_vertices.get(i) == null) {
                _vertices.set(i, new ArrayList<>());
                _vertices.get(0).add(i);
                return i;
            }
        }
        _vertices.add(new ArrayList<>());
        int j = _vertices.size() - 1;
        _vertices.get(0).add(j);
        return j;
    }

    @Override
    public int add(int u, int v) {
        if (contains(u, v)) {
            return edgeId(u, v);
        }
        _edges.add(new int[]{u, v});
        int newId = _edges.size() - 1;
        ArrayList<Integer> es = _vertices.get(u);
        es.add(newId);
        if (!isDirected()) {
            es = _vertices.get(v);
            if (!es.contains(newId)) {
                es.add(newId);
            }
        }
        _edgeSize += 1;
        return _edges.size() - 1;
    }

    @Override
    public void remove(int v) {
        if (contains(v)) {
            for (int u : vertices()) {
                if (contains(u, v) || contains(v, u)) {
                    remove(u, v);
                    remove(v, u);
                }
            }
            _vertices.set(v, null);
            _vertices.get(0).remove(Integer.valueOf(v));
        }
    }

    @Override
    public void remove(int u, int v) {
        if (contains(u, v)) {
            int id = edgeId(u, v);
            _vertices.get(u).remove(Integer.valueOf(id));
            if (!isDirected()) {
                _vertices.get(v).remove(Integer.valueOf(id));
            }
            _edges.set(id, null);
            _edgeSize -= 1;
        }
    }

    @Override
    public Iteration<Integer> vertices() {
        return Iteration.iteration(_vertices.get(0));
    }

    @Override
    public Iteration<Integer> successors(int v) {
        ArrayList<Integer> l = new ArrayList<>();
        if (!contains(v)) {
            return Iteration.iteration(l);
        }
        for (int id : _vertices.get(v)) {
            int [] e = _edges.get(id);
            l.add(e[0] == v ? e[1] : e[0]);
        }
        return Iteration.iteration(l);
    }

    @Override
    public abstract Iteration<Integer> predecessors(int v);

    @Override
    public Iteration<int[]> edges() {
        ArrayList<int[]> es = new ArrayList<>();
        for (int[] e : _edges) {
            if (e != null) {
                es.add(e);
            }
        }
        return Iteration.iteration(es);
    }

    @Override
    protected void checkMyVertex(int v) {
        if (!contains(v)) {
            throw new IllegalArgumentException("vertex not from Graph");
        }
    }

    @Override
    protected int edgeId(int u, int v) {
        if (contains(u, v)) {
            ArrayList<Integer> es = _vertices.get(u);
            for (int id : es) {
                if (isDirected()) {
                    if (_edges.get(id)[1] == v) {
                        return id;
                    }
                } else {
                    int in = _edges.get(id)[0];
                    int out = _edges.get(id)[1];
                    if (in == u && out == v) {
                        return id;
                    } else if (in == v && out == u) {
                        return id;
                    }
                }
            }
        }
        return 0;
    }

    /** A list of my vertices.
     * The first element contains the indices of all existing vertices.
     * Following elements contain indices of the vertex's edges,
     * or null if it's not my vertex. */
    private ArrayList<ArrayList<Integer>> _vertices;
    /** A list of my edges. Containing destination of each edge. */
    private ArrayList<int[]> _edges;
    /** The number of edges I have. */
    private int _edgeSize;


}
