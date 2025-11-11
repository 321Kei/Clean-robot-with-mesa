"""
Cleaning Robot Simulation Runner
This script runs experiments with different numbers of agents and analyzes the results.

Author(s): Ximena Silva Bárcena A01785518
            Ana Keila Martínez Moreno A01666624
Date: 2025-11-11
"""

import random
import pandas as pd
import matplotlib.pyplot as plt

import seaborn as sns
from cleaning_model import CleaningModel


def runSingleSimulation(width, height, numAgents, dirtyPercentage, maxTime, seed=None):
    """
    Run a single simulation with the given parameters.

    Args:
        width: Grid width
        height: Grid height
        numAgents: Number of cleaning agents
        dirtyPercentage: Initial percentage of dirty cells
        maxTime: Maximum simulation time
        seed: Random seed for reproducibility

    Returns:
        Dictionary with simulation results
    """
    if seed is not None:
        random.seed(seed)

    # Create and run model
    model = CleaningModel(width, height, numAgents, dirtyPercentage, maxTime)

    # Run until completion or max time
    while model.running:
        model.step()

    # Get results
    results = model.getResults()
    results['numAgents'] = numAgents

    return results


def runExperiments(width=10, height=10, dirtyPercentage=50, maxTime=1000,
                   agentCounts=[1, 2, 3, 5, 10, 15, 20], numRepetitions=10):
    """
    Run multiple experiments with different numbers of agents.

    Args:
        width: Grid width
        height: Grid height
        dirtyPercentage: Initial percentage of dirty cells
        maxTime: Maximum simulation time
        agentCounts: List of agent counts to test
        numRepetitions: Number of repetitions per configuration

    Returns:
        DataFrame with all experiment results
    """
    allResults = []

    print(f"Running experiments on {width}x{height} grid with {dirtyPercentage}% dirty cells")
    print(f"Agent counts to test: {agentCounts}")
    print(f"Repetitions per configuration: {numRepetitions}\n")

    for numAgents in agentCounts:
        print(f"Testing with {numAgents} agent(s)...")

        for rep in range(numRepetitions):
            # Run simulation with different seed for each repetition
            results = runSingleSimulation(
                width, height, numAgents, dirtyPercentage, maxTime,
                seed=numAgents * 1000 + rep
            )
            results['repetition'] = rep
            allResults.append(results)

        print(f"  Completed {numRepetitions} repetitions")

    # Create DataFrame
    df = pd.DataFrame(allResults)
    return df


def analyzeResults(df):
    """
    Analyze and print summary statistics from experiment results.

    Args:
        df: DataFrame with experiment results
    """
    print("EXPERIMENT RESULTS SUMMARY")

    # Group by number of agents
    grouped = df.groupby('numAgents')

    # Calculate summary statistics
    summary = grouped.agg({
        'stepsToClean': ['mean', 'std', 'min', 'max'],
        'totalMovements': ['mean', 'std', 'min', 'max'],
        'cleanPercentage': ['mean', 'std']
    }).round(2)

    print("AVERAGE RESULTS BY NUMBER OF AGENTS")
    print(summary)


    # Check which configurations achieved 100% cleaning
    completeCleaning = grouped.apply(
        lambda x: (x['cleanPercentage'] == 100).sum() / len(x) * 100,
        include_groups=False
    )

    print("PERCENTAGE OF RUNS THAT ACHIEVED 100% CLEAN:")
    for agents, pct in completeCleaning.items():
        print(f"{agents} agent(s): {pct:.1f}%")

    print("\n")


def createVisualizations(df, outputPrefix='cleaning_simulation'):
    """
    Create visualization plots from experiment results.

    Args:
        df: DataFrame with experiment results
        outputPrefix: Prefix for output file names
    """
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (15, 10)

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # 1. Steps to clean vs Number of agents
    ax1 = axes[0, 0]
    dfClean = df[df['stepsToClean'].notna()]
    sns.boxplot(data=dfClean, x='numAgents', y='stepsToClean', ax=ax1)
    ax1.set_xlabel('Number of Agents', fontsize=12)
    ax1.set_ylabel('Steps to Clean All Cells', fontsize=12)
    ax1.set_title('Time Required to Clean All Cells', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # 2. Total movements vs Number of agents
    ax2 = axes[0, 1]
    sns.boxplot(data=df, x='numAgents', y='totalMovements', ax=ax2)
    ax2.set_xlabel('Number of Agents', fontsize=12)
    ax2.set_ylabel('Total Movements', fontsize=12)
    ax2.set_title('Total Movements by All Agents', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # 3. Average steps to clean (line plot)
    ax3 = axes[1, 0]
    avgSteps = dfClean.groupby('numAgents')['stepsToClean'].mean()
    stdSteps = dfClean.groupby('numAgents')['stepsToClean'].std()
    ax3.plot(avgSteps.index, avgSteps.values, marker='o', linewidth=2, markersize=8)
    ax3.fill_between(avgSteps.index,
                     avgSteps.values - stdSteps.values,
                     avgSteps.values + stdSteps.values,
                     alpha=0.3)
    ax3.set_xlabel('Number of Agents', fontsize=12)
    ax3.set_ylabel('Average Steps to Clean', fontsize=12)
    ax3.set_title('Average Time to Complete Cleaning', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)

    # 4. Average movements per agent
    ax4 = axes[1, 1]
    df['movementsPerAgent'] = df['totalMovements'] / df['numAgents']
    avgMovementsPerAgent = df.groupby('numAgents')['movementsPerAgent'].mean()
    ax4.bar(avgMovementsPerAgent.index, avgMovementsPerAgent.values)
    ax4.set_xlabel('Number of Agents', fontsize=12)
    ax4.set_ylabel('Average Movements per Agent', fontsize=12)
    ax4.set_title('Efficiency: Movements per Agent', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    # Save figure
    outputFile = f'{outputPrefix}_analysis.png'
    plt.savefig(outputFile, dpi=300, bbox_inches='tight')
    print(f"\nVisualization saved to: {outputFile}")

    return fig


def saveResultsToCsv(df, filename='cleaning_simulation_results.csv'):
    """
    Save experiment results to CSV file.

    Args:
        df: DataFrame with experiment results
        filename: Output CSV filename
    """
    df.to_csv(filename, index=False)
    print(f"Results saved to: {filename}")


def main():
    """
    Main function to run experiments and generate analysis.
    """

    # Experiment parameters
    GRID_WIDTH = 10
    GRID_HEIGHT = 10
    DIRTY_PERCENTAGE = 50
    MAX_TIME = 1000
    AGENT_COUNTS = [1, 2, 3, 5, 10, 15, 20]
    NUM_REPETITIONS = 10

    # Run experiments
    resultsDf = runExperiments(
        width=GRID_WIDTH,
        height=GRID_HEIGHT,
        dirtyPercentage=DIRTY_PERCENTAGE,
        maxTime=MAX_TIME,
        agentCounts=AGENT_COUNTS,
        numRepetitions=NUM_REPETITIONS
    )

    # Analyze results
    analyzeResults(resultsDf)

    # Create visualizations
    createVisualizations(resultsDf)

    # Save results
    saveResultsToCsv(resultsDf)


if __name__ == "__main__":
    main()