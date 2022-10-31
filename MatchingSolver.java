package MinimumVertexCover.Solvers;

import java.util.ArrayList;
import java.util.Random;
import Graph.IGraph;
import Graph.MatrixGraph;
import MinimumVertexCover.ProblemInstanceGenerator;
import Utils.Tuple;


public class MatchingSolver implements IVertexCoverSolver {

    @Override
    public Cover solve(IGraph graph) {
        Cover cover = new Cover(graph);
        int edgeCount = graph.getEdgeCount();
        Random generator = new Random();
        while((edgeCount = graph.getEdgeCount()) > 0) {
            int edgeId = generator.nextInt(edgeCount);
            Tuple<Integer, Integer> edge = graph.getEdge(edgeId);
            cover.addToCover(edge.x);
            cover.addToCover(edge.y);
            graph.removeEdges(edge.x);
            graph.removeEdges(edge.y);
        }
        return cover;
    }

    public Cover solveSorted(IGraph graph) {
        Cover cover = new Cover(graph);
        int edgeCount = graph.getEdgeCount();

        while((edgeCount = graph.getEdgeCount()) > 0) {

            int maxTotalDegree = 0;
            int selectedEdge = 0;

            // Find the edge for which the end-points have the highest total degree
            for (int i = 0; i < edgeCount; i++) {
                Tuple<Integer, Integer> edge = graph.getEdge(i);
                int sumDegree = graph.getVertexDegree(edge.x) + graph.getVertexDegree(edge.y);
                if (sumDegree > maxTotalDegree) {
                    System.out.println("Updating DegreeSum = " + sumDegree);
                    maxTotalDegree = sumDegree;
                    selectedEdge = i;
                }
            }

            Tuple<Integer, Integer> edge = graph.getEdge(selectedEdge);
            cover.addToCover(edge.x);
            cover.addToCover(edge.y);
            graph.removeEdges(edge.x);
            graph.removeEdges(edge.y);

        }
        return cover;
    }

    public void evaluatePerformance () {
        // List of instance sizes (n = number of VERTICES)
        ArrayList<Integer> nVals = new ArrayList<Integer>();
        nVals.add(100);
        nVals.add(100);
        nVals.add(100);

        // List of instance sizes (n = number of EDGES)
        ArrayList<Integer> mVals = new ArrayList<Integer>();
        mVals.add(500);
        mVals.add(750);
        mVals.add(1000);

        for (int i = 0; i < nVals.size(); i++) {
            int n = nVals.get(i);
            int m = mVals.get(i);
            MatrixGraph G = ProblemInstanceGenerator.generate(n, m);

            long t1 = System.nanoTime();

            solve(G); // execute algorithm

            long t2 = System.nanoTime();
            double dt = (t2-t1)/1e6;

            System.out.println("Algorithm took " + dt + "ms");

        }
    }
}
