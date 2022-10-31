package MinimumVertexCover.Solvers;
import java.util.Map;
import java.util.Random;

import Graph.IGraph;
import Utils.Tuple;


public class PrimalDualSolver implements IVertexCoverSolver {
    private static Random generator;

    @Override
    public Cover solve(IGraph graph) {

        Cover cover = new Cover(graph);

        if (generator == null)
            generator = new Random();

        // Clone weight map to keep track of which vertices are tight
        Map<Integer, Integer> wRemaining = graph.cloneWeightMap();

        while (graph.getEdgeCount() != 0) {
            // Choose a random edge e = {u, v}
            Tuple<Integer, Integer> e = getRandomUntightEdge(graph, wRemaining);

            if (wRemaining.get(e.x) == 0 || wRemaining.get(e.y) == 0) {
                // One of the end-point vertices is tight: skip
                continue;
            }

            // Minimum of the two remaining vertex weights.
            // This is the maximum p_e can be increased without violating fairness
            int wMinimum = Math.min(wRemaining.get(e.x), wRemaining.get(e.y));

            // Add the vertices that have become tight to the cover and remove them from the graph
            if (wMinimum == wRemaining.get(e.x))
                addToCover(graph, cover, e.x);

            if (wMinimum == wRemaining.get(e.y))
                addToCover(graph, cover, e.y);

            // Decrease weights remaining for both vertices
            // Now at least one should be zero!
            wRemaining.put(e.x, wRemaining.get(e.x) - wMinimum);
            wRemaining.put(e.y, wRemaining.get(e.y) - wMinimum);
        }
        return cover;
    }

    private void addToCover(IGraph graph, Cover cover, Integer vertex) {
        cover.addToCover(vertex);
        graph.removeEdges(vertex);
    }

    private Tuple<Integer, Integer> getRandomUntightEdge(IGraph graph, Map<Integer, Integer> wRemaining) {
        Tuple<Integer, Integer> edge = graph.getEdge(generator.nextInt(graph.getEdgeCount()));
        if (wRemaining.get(edge.x) == 0 || wRemaining.get(edge.y) == 0) {
            System.out.println("Warning: tight edge found outside cover: {" + edge.x + "," + edge.y +"}. "
                    + "Could indicate mistake in solver.");
            return getRandomUntightEdge(graph, wRemaining);
        }
        return edge;
    }
}