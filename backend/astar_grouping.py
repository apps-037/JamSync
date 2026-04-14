# backend/astar_grouping.py
"""
A* Search for Optimal Group Formation
Uses custom heuristics to find best musician combinations
"""
import heapq
from typing import List, Set, Tuple
from dataclasses import dataclass, field
from csp_solver import Musician, Session, ConstraintChecker

@dataclass(order=True)
class SearchNode:
    """Node in A* search tree"""
    priority: float = field(compare=True)  # f(n) = g(n) + h(n)
    g_cost: float = field(compare=False) 
    h_cost: float = field(compare=False) 
    musicians: List[Musician] = field(compare=False)
    available_pool: List[Musician] = field(compare=False) 

class GroupFormationHeuristics:
    """
    Domain-specific heuristics for evaluating musician groups
    """
    
    def h_instrument_synergy(self, group: List[Musician]) -> float:
        """
        Heuristic 1: Instrument Synergy
        
        Certain instrument combinations work better together:
        - Guitar + Bass + Drums = classic rock trio (HIGH)
        - Keys + Bass + Drums = jazz rhythm section (HIGH)
        - Guitar + Guitar + Guitar = redundant (LOW)
        - Drums + Drums = impossible (ZERO)
        
        Returns: 0-100 score
        """
        if not group:
            return 0.0
        
        instruments = [m.instrument for m in group]
        instrument_counts = {}
        for inst in instruments:
            instrument_counts[inst] = instrument_counts.get(inst, 0) + 1
        
        score = 0.0
        
        # Perfect combinations
        has_guitar = 'Guitar' in instruments
        has_bass = 'Bass' in instruments
        has_drums = 'Drums' in instruments
        has_keys = 'Keys' in instruments
        
        # Classic rhythm section
        if has_bass and has_drums:
            score += 40
        
        # Full band
        if has_guitar and has_bass and has_drums:
            score += 30 
        
        if has_keys and has_bass and has_drums:
            score += 30 
        
        # Penalties for redundancy
        for inst, count in instrument_counts.items():
            if count > 1 and inst not in ['Guitar', 'Vocals']:
                score -= 20 * (count - 1)  
            elif count > 3: 
                score -= 10 * (count - 3)
        
        unique_instruments = len(set(instruments))
        score += unique_instruments * 5
        
        return max(0, min(100, score))
    
    def h_skill_variance(self, group: List[Musician]) -> float:
        """
        Heuristic 2: Goldilocks Skill Variance
        
        Not too similar (boring), not too different (frustrating)
        Optimal: 1-3 point spread on 1-10 scale
        
        Returns: 0-100 score
        """
        if len(group) < 2:
            return 100.0
        
        skills = [m.skill_level for m in group]
        skill_range = max(skills) - min(skills)
        avg_skill = sum(skills) / len(skills)
        
        # Score based on variance
        if skill_range == 0:
            return 50.0  
        elif skill_range <= 2:
            return 100.0 
        elif skill_range <= 3:
            return 85.0   
        elif skill_range <= 4:
            return 60.0  
        elif skill_range <= 5:
            return 35.0  
        else:
            return 10.0  
    
    def h_genre_consensus(self, group: List[Musician]) -> float:
        """
        Heuristic 3: Genre Consensus
        
        Need common musical ground for coherent jam
        At least 50% of musicians should share genres
        
        Returns: 0-100 score
        """
        if len(group) < 2:
            return 100.0
        
        # Count how often each genre appears
        all_genres = []
        for musician in group:
            all_genres.extend(musician.genres)
        
        from collections import Counter
        genre_counts = Counter(all_genres)
        
        # Find genres that at least half the group shares
        threshold = len(group) / 2
        common_genres = [g for g, count in genre_counts.items() if count >= threshold]
        
        if not common_genres:
            return 20.0
        
        # Score based on how many common genres and how widely shared
        consensus_strength = sum(genre_counts[g] for g in common_genres) / len(all_genres)
        
        base_score = len(common_genres) * 25 
        consensus_bonus = consensus_strength * 50
        
        return min(100.0, base_score + consensus_bonus)
    
    def h_role_balance(self, group: List[Musician]) -> float:
        """
        Heuristic 4: Role Balance (Leader/Supporter Distribution)
        
        Optimal: 1-2 leaders, rest supporters or flexible
        Bad: All leaders (conflict) or all supporters (no direction)
        
        Returns: 0-100 score
        """
        if not group:
            return 100.0
        
        leaders = sum(1 for m in group if m.personality_leader > 0.6)
        supporters = sum(1 for m in group if m.personality_leader < 0.4)
        flexible = len(group) - leaders - supporters
        
        # Ideal configurations
        if leaders == 1 and supporters >= 1:
            return 100.0  
        elif leaders == 2 and supporters >= 1:
            return 90.0  
        elif leaders == 1 and flexible >= 2:
            return 85.0  
        elif leaders == 0 and supporters >= 2:
            return 50.0 
        elif leaders >= 3:
            return 30.0  
        else:
            return 70.0 
    
    def combined_heuristic(self, group: List[Musician]) -> float:
        """
        Combine all heuristics with weights
        
        This is h(n) in A* search
        Higher score = better group (we want to MAXIMIZE)
        """
        synergy = self.h_instrument_synergy(group)
        variance = self.h_skill_variance(group)
        consensus = self.h_genre_consensus(group)
        balance = self.h_role_balance(group)
        
        # Weighted combination
        combined = (
            0.30 * synergy +    
            0.30 * variance +   
            0.25 * consensus +  
            0.15 * balance     
        )
        
        return combined

class AStarGroupFormation:
    """
    A* Search for finding optimal musician groups
    
    State: Current group of musicians
    Goal: Group of 3-6 musicians with high quality score
    Actions: Add a musician to the group
    Cost: -quality (we minimize cost, so negate quality to maximize it)
    Heuristic: Estimated quality based on current group composition
    """
    
    def __init__(self):
        self.heuristics = GroupFormationHeuristics()
        self.constraint_checker = ConstraintChecker()
        self.nodes_explored = 0
    
    def is_goal_state(self, group: List[Musician], time_slot: str) -> bool:
        """Check if this is a valid complete group"""
        if len(group) < 3:
            return False
        
        # Must satisfy hard constraints
        if not self.constraint_checker.check_group_size(group):
            return False
        
        if not self.constraint_checker.check_availability(group, time_slot):
            return False
        
        if not self.constraint_checker.check_rhythm_section(group):
            return False
        
        return True
    
    def get_successors(
        self, 
        current_group: List[Musician], 
        available_pool: List[Musician],
        time_slot: str
    ) -> List[Tuple[List[Musician], Musician]]:
        """
        Generate successor states (groups with one more musician added)
        """
        successors = []
        
        if len(current_group) >= 6:
            return successors
        
        for musician in available_pool:
            new_group = current_group + [musician]
            
            if self.constraint_checker.check_availability(new_group, time_slot):
                successors.append((new_group, musician))
        
        return successors
    
    def search(
        self, 
        available_musicians: List[Musician], 
        time_slot: str,
        max_group_size: int = 6
    ) -> List[Musician]:
        """
        A* search to find optimal group for a time slot
        
        Returns: Best group of musicians (or None if no valid group found)
        """
        self.nodes_explored = 0
   
        start_node = SearchNode(
            priority=0.0,
            g_cost=0.0,
            h_cost=0.0,
            musicians=[],
            available_pool=available_musicians
        )
        
        frontier = []
        heapq.heappush(frontier, start_node)
        
        explored = set()
        best_complete_group = None
        best_score = -float('inf')
        
        while frontier and self.nodes_explored < 1000:  
            current = heapq.heappop(frontier)
            self.nodes_explored += 1
            
            current_group = current.musicians
            
            state_signature = tuple(sorted(m.id for m in current_group))
            if state_signature in explored:
                continue
            explored.add(state_signature)
            
            # Check if this is a valid complete group
            if self.is_goal_state(current_group, time_slot):
                quality = self.heuristics.combined_heuristic(current_group)
                
                if quality > best_score:
                    best_score = quality
                    best_complete_group = current_group
                
                # Continue searching for better solutions if group isn't max size
                if len(current_group) >= max_group_size:
                    continue
            
            # Generate successors
            remaining_pool = [m for m in current.available_pool if m not in current_group]
            successors = self.get_successors(current_group, remaining_pool, time_slot)
            
            for new_group, added_musician in successors:
                # g(n) = negative quality so far (we want to maximize quality)
                g_cost = -self.heuristics.combined_heuristic(new_group)
                
                # h(n) = estimated remaining potential
                remaining_slots = max_group_size - len(new_group)
                h_cost = -remaining_slots * 10  
                
                # f(n) = g(n) + h(n)
                f_cost = g_cost + h_cost
                
                new_node = SearchNode(
                    priority=f_cost,
                    g_cost=g_cost,
                    h_cost=h_cost,
                    musicians=new_group,
                    available_pool=remaining_pool
                )
                
                heapq.heappush(frontier, new_node)
        
        return best_complete_group

# Test the A* search
if __name__ == "__main__":
    from csp_solver import BasicCSPSolver
    
    print("Testing A* Group Formation")
    print("="*70)
    
    # Load musicians
    solver = BasicCSPSolver()
    musicians = solver.load_musicians('data/musicians_dataset.json')
    
    # Pick a time slot to test
    test_time_slot = "Fri_18-21"
    
    # Get musicians available at this time
    available = [m for m in musicians if test_time_slot in m.availability]
    
    print(f"\nTime Slot: {test_time_slot}")
    print(f"Available Musicians: {len(available)}")
    
    # Run A* search
    astar = AStarGroupFormation()
    best_group = astar.search(available, test_time_slot)
    
    if best_group:
        print(f"\n✓ A* found optimal group ({len(best_group)} musicians)")
        print(f"  Nodes explored: {astar.nodes_explored}")
        
        heuristics = GroupFormationHeuristics()
        
        print(f"\n  Musicians:")
        for m in best_group:
            print(f"    - {m.name} ({m.instrument}, Skill {m.skill_level})")
            print(f"      Genres: {', '.join(m.genres)}")
        
        print(f"\n  Heuristic Scores:")
        print(f"    Instrument Synergy: {heuristics.h_instrument_synergy(best_group):.1f}%")
        print(f"    Skill Variance: {heuristics.h_skill_variance(best_group):.1f}%")
        print(f"    Genre Consensus: {heuristics.h_genre_consensus(best_group):.1f}%")
        print(f"    Role Balance: {heuristics.h_role_balance(best_group):.1f}%")
        print(f"    Combined Score: {heuristics.combined_heuristic(best_group):.1f}%")
    else:
        print("\n✗ No valid group found")
    
    # Compare with greedy approach
    print("\n" + "="*70)
    print("COMPARISON: A* vs Greedy Selection")
    print("="*70)
    
    # Greedy: just take first N available musicians
    greedy_group = available[:4] if len(available) >= 4 else available
    
    if len(greedy_group) >= 3:
        print(f"\nGreedy Group ({len(greedy_group)} musicians):")
        for m in greedy_group:
            print(f"  - {m.name} ({m.instrument}, Skill {m.skill_level})")
        
        greedy_score = heuristics.combined_heuristic(greedy_group)
        astar_score = heuristics.combined_heuristic(best_group) if best_group else 0
        
        print(f"\nGreedy Score: {greedy_score:.1f}%")
        print(f"A* Score: {astar_score:.1f}%")
        print(f"Improvement: {astar_score - greedy_score:+.1f} points")