package graph;

/* See restrictions in Graph.java. */

import java.util.ArrayDeque;


/** Implements a depth-first traversal of a graph.  Generally, the
 *  client will extend this class, overriding the visit and
 *  postVisit methods, as desired (by default, they do nothing).
 *  @author Calvin
 */
public class DepthFirstTraversal extends Traversal {

    /** A depth-first Traversal of G. */
    protected DepthFirstTraversal(Graph G) {
        super(G, new QueueStack<>());
    }

    @Override
    protected boolean visit(int v) {
        return super.visit(v);
    }

    @Override
    protected boolean postVisit(int v) {
        return super.postVisit(v);
    }

    @Override
    protected boolean reverseSuccessors(int v) {
        return true;
    }

    /** A stack built on ArrayDeque. */
    private static class QueueStack<T> extends ArrayDeque<T> {
        @Override
        public boolean add(T e) {
            this.addFirst(e);
            return true;
        }
        @Override
        public T remove() {
            return this.peek();
        }
    }
}
