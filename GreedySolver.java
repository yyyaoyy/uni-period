package MinimumVertexCover.Solvers;

import java.util.Comparator;

import Graph.IGraph;
import Utils.Tuple;


public class GreedySolver implements IVertexCoverSolver {

    @Override
    public Cover solve(IGraph graph) {
        Cover cover = new Cover(graph);
        while (graph.getEdgeCount() > 0) {
            int vertexToAdd = getMinCostVertex(graph);
            cover.addToCover(vertexToAdd);
            graph.removeEdges(vertexToAdd);
        }
        return cover;
    }


    private int getMinCostVertex(IGraph graph) {
        int bestVertex = -1;
        double minCost = Double.MAX_VALUE;
        for (Integer vertex : graph.getVertices()) {
            double cost = (double)graph.getWeight(vertex) / (double)graph.getEdgeCount(vertex);
            if (cost < minCost) {
                bestVertex = vertex;
                minCost = cost;
            }
        }
        return bestVertex;
    }

    public class TupleYComparer implements Comparator<Tuple<Integer, Integer>> {
        @Override
        public int compare(Tuple<Integer, Integer> t1, Tuple<Integer, Integer> t2) {
            return - t1.y.compareTo(t2.y);
        }
    }
}
