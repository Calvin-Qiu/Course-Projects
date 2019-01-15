package graph;

/* See restrictions in Graph.java. */

import java.util.ArrayList;

/** Represents a general unlabeled directed graph whose vertices are denoted by
 *  positive integers. Graphs may have self edges.
 *
 *  @author Calvin
 */
public class DirectedGraph extends GraphObj {

    @Override
    public boolean isDirected() {
        return true;
    }

    @Override
    public int inDegree(int v) {
        int i = 0;
        for (int u : vertices()) {
            if (contains(u, v)) {
                i++;
            }
        }
        return i;
    }

    @Override
    public Iteration<Integer> predecessors(int v) {
        ArrayList<Integer> pre = new ArrayList<>();
        for (int u : vertices()) {
            if (contains(u, v)) {
                pre.add(u);
            }
        }
        return Iteration.iteration(pre);
    }
}
