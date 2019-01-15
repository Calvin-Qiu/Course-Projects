package graph;

import org.junit.Test;

import java.util.Arrays;
import java.util.List;

import static org.junit.Assert.*;

public class TraversalTest {
    /** Set up a simple DIRECTED graph.*/
    private Graph simpleSetUp(boolean directed) {
        Graph g = directed ? new DirectedGraph() : new UndirectedGraph();
        for (int i = 1; i < 10; i++) {
            g.add();
        }
        g.add(1, 2);
        g.add(1, 8);
        g.add(2, 3);
        g.add(2, 6);
        g.add(3, 4);
        g.add(3, 5);
        g.add(6, 5);
        g.add(6, 7);
        g.add(8, 9);
        g.add(9, 6);
        g.add(9, 9);
        return g;
    }

    private Graph circularSetup(boolean directed) {
        Graph g = directed ? new DirectedGraph() : new UndirectedGraph();
        for (int i = 1; i < 4; i++) {
            g.add();
        }
        g.add(1, 2);
        g.add(2, 3);
        g.add(3, 1);
        return g;
    }

    private Graph simpleSetUp2(boolean directed) {
        Graph g = directed ? new DirectedGraph() : new UndirectedGraph();
        for (int i = 1; i < 5; i++) {
            g.add();
        }
        g.add(1, 2);
        g.add(1, 3);
        g.add(1, 4);
        g.add(3, 4);
        return g;
    }

    @Test
    public void directedCircularTest() {
        Graph g = circularSetup(true);
        SimpleDFT t = new SimpleDFT(g);
        t.traverse(1);
        List<Integer> correct = Arrays.asList(3, 2, 1);
        assertEquals(correct, t.getRoute());
    }

    @Test
    public void direcetdDFSTest() {
        Graph g = simpleSetUp(true);
        SimpleDFT t = new SimpleDFT(g);
        t.traverse(1);
    }

    @Test
    public void undirecetdDFSTest() {
        Graph g = simpleSetUp(false);
        SimpleDFT t = new SimpleDFT(g);
        t.traverse(1);
        List<Integer> correct = Arrays.asList(4, 7, 8, 9, 6, 5, 3, 2, 1);
        assertEquals(correct, t.getRoute());
    }

    @Test
    public void direcetdBFSTest() {
        Graph g = simpleSetUp(true);
        SimpleBFT t = new SimpleBFT(g);
        t.traverse(1);
        List<Integer> correct = Arrays.asList(1, 2, 8, 3, 6, 9, 4, 5, 7);
        assertEquals(t.route, correct);
    }

    @Test
    public void undirecetdBFSTest() {
        Graph g = simpleSetUp(false);
        SimpleBFT t = new SimpleBFT(g);
        g.add(8, 7);
        t.traverse(1);
        List<Integer> correct = Arrays.asList(1, 2, 8, 3, 6, 9, 7, 4, 5);
        assertEquals(t.route, correct);
    }
}
