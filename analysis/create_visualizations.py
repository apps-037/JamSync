# analysis/create_visualizations.py
"""
Generate visualizations for paper
"""
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from backend.csp_solver import BasicCSPSolver

def run_all_algorithms():
    """Run all three approaches and collect data"""
    
    results = {}
    
    # Algorithm 1: Greedy
    print("Running Greedy CSP...")
    solver1 = BasicCSPSolver(use_adversarial_prediction=False, use_astar=False)
    musicians = solver1.load_musicians()
    sessions1 = solver1.solve(musicians)
    
    results['Greedy CSP'] = {
        'sessions': sessions1,
        'num_sessions': len(sessions1),
        'match_rate': (len(solver1.assigned_musicians) / len(musicians)) * 100,
        'avg_quality': sum(s.quality_score for s in sessions1) / len(sessions1),
        'quality_scores': [s.quality_score for s in sessions1]
    }
    
    # Algorithm 2: A*
    print("\nRunning CSP + A*...")
    solver2 = BasicCSPSolver(use_adversarial_prediction=False, use_astar=True)
    musicians = solver2.load_musicians()
    sessions2 = solver2.solve(musicians)
    
    results['CSP + A*'] = {
        'sessions': sessions2,
        'num_sessions': len(sessions2),
        'match_rate': (len(solver2.assigned_musicians) / len(musicians)) * 100,
        'avg_quality': sum(s.quality_score for s in sessions2) / len(sessions2),
        'quality_scores': [s.quality_score for s in sessions2]
    }
    
    # Algorithm 3: Hybrid
    print("\nRunning Hybrid (A* + Adversarial)...")
    solver3 = BasicCSPSolver(use_adversarial_prediction=True, use_astar=True)
    musicians = solver3.load_musicians()
    sessions3 = solver3.solve(musicians)
    
    results['Hybrid'] = {
        'sessions': sessions3,
        'num_sessions': len(sessions3),
        'match_rate': (len(solver3.assigned_musicians) / len(musicians)) * 100,
        'avg_quality': sum(s.quality_score for s in sessions3) / len(sessions3),
        'quality_scores': [s.quality_score for s in sessions3]
    }
    
    return results

def create_comparison_charts(results):
    """Create comparison visualizations"""
    
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('JamSync Algorithm Comparison', fontsize=16, fontweight='bold')
    
    algorithms = list(results.keys())
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    # Chart 1: Average Quality Comparison
    ax1 = axes[0, 0]
    avg_qualities = [results[alg]['avg_quality'] for alg in algorithms]
    bars1 = ax1.bar(algorithms, avg_qualities, color=colors, alpha=0.8, edgecolor='black')
    ax1.set_ylabel('Average Quality Score (%)', fontweight='bold')
    ax1.set_title('Average Session Quality', fontweight='bold')
    ax1.set_ylim(0, 100)
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontweight='bold')
    
    # Chart 2: Match Rate Comparison
    ax2 = axes[0, 1]
    match_rates = [results[alg]['match_rate'] for alg in algorithms]
    bars2 = ax2.bar(algorithms, match_rates, color=colors, alpha=0.8, edgecolor='black')
    ax2.set_ylabel('Musicians Matched (%)', fontweight='bold')
    ax2.set_title('Musician Match Rate', fontweight='bold')
    ax2.set_ylim(0, 100)
    ax2.grid(axis='y', alpha=0.3)
    
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontweight='bold')
    
    # Chart 3: Quality Distribution (Box Plot)
    ax3 = axes[1, 0]
    quality_distributions = [results[alg]['quality_scores'] for alg in algorithms]
    bp = ax3.boxplot(quality_distributions, labels=algorithms, patch_artist=True)
    
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    ax3.set_ylabel('Quality Score (%)', fontweight='bold')
    ax3.set_title('Quality Score Distribution', fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    
    # Chart 4: Sessions Created
    ax4 = axes[1, 1]
    num_sessions = [results[alg]['num_sessions'] for alg in algorithms]
    bars4 = ax4.bar(algorithms, num_sessions, color=colors, alpha=0.8, edgecolor='black')
    ax4.set_ylabel('Number of Sessions', fontweight='bold')
    ax4.set_title('Sessions Created', fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)
    
    for bar in bars4:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    # Save figure
    output_dir = 'analysis'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    plt.savefig(f'{output_dir}/algorithm_comparison.png', dpi=300, bbox_inches='tight')
    print(f"\n✅ Saved comparison chart to {output_dir}/algorithm_comparison.png")
    
    plt.show()

def create_quality_tradeoff_scatter(results):
    """Create scatter plot showing quality vs match rate tradeoff"""
    
    plt.figure(figsize=(10, 6))
    
    algorithms = list(results.keys())
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    for alg, color in zip(algorithms, colors):
        match_rate = results[alg]['match_rate']
        avg_quality = results[alg]['avg_quality']
        
        plt.scatter(match_rate, avg_quality, s=300, color=color, 
                   alpha=0.7, edgecolors='black', linewidth=2, label=alg)
        
        # Add label
        plt.annotate(alg, (match_rate, avg_quality), 
                    xytext=(10, 10), textcoords='offset points',
                    fontsize=10, fontweight='bold')
    
    plt.xlabel('Match Rate (% of Musicians Matched)', fontsize=12, fontweight='bold')
    plt.ylabel('Average Quality Score (%)', fontsize=12, fontweight='bold')
    plt.title('Quality vs. Match Rate Tradeoff', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    
    # Add diagonal reference line (ideal would be top-right)
    plt.plot([0, 100], [0, 100], 'k--', alpha=0.2, linewidth=1)
    
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    
    plt.tight_layout()
    plt.savefig('analysis/quality_tradeoff.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved tradeoff chart to analysis/quality_tradeoff.png")
    plt.show()

def print_summary_table(results):
    """Print formatted table for paper"""
    
    print("\n" + "="*80)
    print("TABLE FOR PAPER (Copy this!)")
    print("="*80)
    print()
    print("Table 1: Algorithm Performance Comparison")
    print()
    print(f"{'Algorithm':<30} | {'Sessions':<10} | {'Match Rate':<12} | {'Avg Quality':<12}")
    print("-" * 80)
    
    for alg in results.keys():
        sessions = results[alg]['num_sessions']
        match = results[alg]['match_rate']
        quality = results[alg]['avg_quality']
        print(f"{alg:<30} | {sessions:<10} | {match:<11.1f}% | {quality:<11.1f}%")
    
    print()
    print("Key Findings:")
    greedy_q = results['Greedy CSP']['avg_quality']
    astar_q = results['CSP + A*']['avg_quality']
    improvement = astar_q - greedy_q
    
    print(f"- A* improved quality by {improvement:.1f} percentage points (+{improvement/greedy_q*100:.1f}%)")
    print(f"- Greedy matched {results['Greedy CSP']['match_rate']:.0f}% vs A* matched {results['CSP + A*']['match_rate']:.0f}%")
    print(f"- Quality-quantity tradeoff clearly demonstrated")

if __name__ == "__main__":
    print("Generating visualizations for JamSync paper...")
    print("="*60)
    
    # Run all algorithms
    results = run_all_algorithms()
    
    # Create charts
    print("\nCreating comparison charts...")
    create_comparison_charts(results)
    
    print("\nCreating quality-tradeoff scatter plot...")
    create_quality_tradeoff_scatter(results)
    
    # Print summary table
    print_summary_table(results)
    
    print("\n" + "="*60)
    print("✅ All visualizations complete!")
    print("📁 Check the analysis/ folder for PNG files")
    print("="*60)