package graph;

import org.junit.Test;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static org.junit.Assert.*;

/** Unit tests for the Graph class.
 *  @author Calvin
 */
public class GraphTest {

    @Test
    public void emptyGraph() {
        DirectedGraph g = new DirectedGraph();
        assertEquals("Initial graph has vertices", 0, g.vertexSize());
        assertEquals("Initial graph has edges", 0, g.edgeSize());
    }

    /** Set up a simple DIRECTED graph.*/
    private Graph simpleSetup(boolean directed) {
        Graph g = directed ? new DirectedGraph() : new UndirectedGraph();
        for (int i = 0; i < 5; i++) {
            g.add();
        }
        return g;
    }

    /** Set up a DIRECTED graph.*/
    private Graph edgeSetup(boolean directed) {
        Graph g = directed ? new DirectedGraph() : new UndirectedGraph();
        for (int i = 0; i < 6; i++) {
            g.add();
        }
        g.add(2, 3);
        g.add(3, 3);
        g.add(2, 6);
        g.add(3, 4);
        g.add(4, 3);
        g.add(3, 5);
        g.add(3, 1);
        return g;
    }

    @Test
    public void simpleTest() {
        Graph g = simpleSetup(true);
        g.remove(3);
        g.remove(3);
        g.add();
        assertEquals(g.maxVertex(), 5);
        assertEquals(g.vertexSize(), 5);
    }

    @Test
    public void edgeTest1() {
        Graph g = edgeSetup(false);
        g.remove(3, 4);
        List<Integer> sucs = new ArrayList<>();
        List<Integer> correct = Arrays.asList(2, 3, 5, 1);
        for (int e : g.successors(3)) {
            sucs.add(e);
        }
        assertEquals(correct, sucs);
    }

    @Test
    public void edgeTest2() {
        Graph g = edgeSetup(true);
        g.remove(2);
        int s = 0;
        for (int e : g.successors(3)) {
            s++;
        }
        assertEquals(s, 4);
    }

    @Test
    public void edgeTest3() {
        Graph g = edgeSetup(false);
        List<Integer> sucs = new ArrayList<>();
        List<Integer> correct = Arrays.asList(2, 3, 4, 5, 1);
        for (int e : g.successors(3)) {
            sucs.add(e);
        }
        assertEquals(correct, sucs);
    }

    @Test
    public void predecessorTest() {
        Graph g = edgeSetup(true);
        List<Integer> pre = new ArrayList<>();
        List<Integer> correct = Arrays.asList(2, 3, 4);
        for (int p : g.predecessors(3)) {
            pre.add(p);
        }
        assertEquals(correct, pre);
    }

    @Test
    public void indegreeTest() {
        Graph g = edgeSetup(false);
        g.remove(4);
        assertEquals(4, g.inDegree(3));
    }

    @Test
    public void removeTest() {
        Graph g = edgeSetup(true);
        g.remove(3);
        g.remove(2);
        g.remove(1);
        g.add();
        List<Integer> correct = Arrays.asList(1, 4, 5, 6);
        for (int v : g.vertices()) {
            assert (correct.contains(v));
        }
        g.add();
        g.remove(5);
        g.add();
        correct = Arrays.asList(1, 2, 3, 4, 6);
        for (int v : g.vertices()) {
            assert (correct.contains(v));
        }
        assertEquals(g.add(), 5);
    }
}
