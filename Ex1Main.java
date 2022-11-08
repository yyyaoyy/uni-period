package org.uma.jmetal.algorithm.multiobjective.nsgaii;
import org.uma.jmetal.algorithm.Algorithm;
import org.uma.jmetal.algorithm.multiobjective.nsgaii.NSGAIIBuilder;
import org.uma.jmetal.operator.CrossoverOperator;
import org.uma.jmetal.operator.MutationOperator;
import org.uma.jmetal.operator.SelectionOperator;
import org.uma.jmetal.operator.impl.crossover.SBXCrossover;
import org.uma.jmetal.operator.impl.mutation.SimpleRandomMutation;
import org.uma.jmetal.operator.impl.selection.BinaryTournamentSelection;
import org.uma.jmetal.problem.Problem;
import org.uma.jmetal.problem.multiobjective.zdt.ZDT1;
import org.uma.jmetal.problem.multiobjective.zdt.ZDT2;
import org.uma.jmetal.problem.multiobjective.zdt.ZDT3;
import org.uma.jmetal.solution.DoubleSolution;
import org.uma.jmetal.util.AlgorithmRunner;
import org.uma.jmetal.util.JMetalLogger;
import org.uma.jmetal.util.comparator.RankingAndCrowdingDistanceComparator;

import java.io.FileNotFoundException;
import java.util.List;

import static org.uma.jmetal.util.AbstractAlgorithmRunner.printFinalSolutionSet;
import static org.uma.jmetal.util.AbstractAlgorithmRunner.printQualityIndicators;


/**
 * Solve ZDT2/3 with NSGA-II on jMetal
 */
class ZDT2_jMetal {
  public static void main(String[] args) throws FileNotFoundException {
    Problem<DoubleSolution> problem;
    Algorithm<List<DoubleSolution>> algorithm;
    CrossoverOperator<DoubleSolution> crossover;
    MutationOperator<DoubleSolution> mutation;
    SelectionOperator<List<DoubleSolution>, DoubleSolution> selection;
    String referenceParetoFront = "";
    //set problem type
    problem = new ZDT2();
    //crossover
    double crossoverProbability = 0.9;
    double crossoverDistributionIndex = 20.0;
    crossover = new SBXCrossover(crossoverProbability, crossoverDistributionIndex);
    //mute
    double mutationProbability = 1.0 / problem.getNumberOfVariables();
    //double mutationDistributionIndex = 20.0 ;
    mutation = new SimpleRandomMutation(mutationProbability);
    //selector
    selection = new BinaryTournamentSelection<DoubleSolution>(
            new RankingAndCrowdingDistanceComparator<DoubleSolution>());
    //send to algorithm
    algorithm = new NSGAIIBuilder<DoubleSolution>(problem, crossover, mutation)
            .setSelectionOperator(selection)
            .setMaxEvaluations(25000)
            .setPopulationSize(100)
            .build();

/*       other way
          evaluator = new SequentialSolutionListEvaluator<DoubleSolution>();
          algorithm = new NSGAII<DoubleSolution>(problem, 25000, 100, crossover,
          mutation, selection, evaluator);
*/
    //use AlgorithmRunner
    AlgorithmRunner algorithmRunner = new AlgorithmRunner.Executor(algorithm).execute();
    //get result
    List<DoubleSolution> population = algorithm.getResult();
    long computingTime = algorithmRunner.getComputingTime();

    JMetalLogger.logger.info("Total execution time: " + computingTime + "ms");
    //print
    printFinalSolutionSet(population);
    if (!referenceParetoFront.equals("")) printQualityIndicators(population, referenceParetoFront);
  }
}