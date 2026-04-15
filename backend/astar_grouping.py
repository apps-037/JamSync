# astar_grouping.py
# A* search for finding best musician groups
# Using heuristics based on music theory and what makes good bands

import heapq
from typing import List
from dataclasses import dataclass, field
from csp_solver import Musician, ConstraintChecker

@dataclass(order=True)
class SearchNode:
    priority: float = field(compare=True)
    g_cost: float = field(compare=False) 
    h_cost: float = field(compare=False) 
    musicians: List[Musician] = field(compare=False)
    available_pool: List[Musician] = field(compare=False) 

class GroupFormationHeuristics:
    
    def h_instrument_synergy(self, group):
        
        if not group:
            return 0.0
        
        instruments = []
        for m in group:
            instruments.append(m.instrument)
        
        instrument_counts = {}
        for inst in instruments:
            if inst in instrument_counts:
                instrument_counts[inst] += 1
            else:
                instrument_counts[inst] = 1
        
        score = 0.0
        
        has_guitar = 'Guitar' in instruments
        has_bass = 'Bass' in instruments
        has_drums = 'Drums' in instruments
        has_keys = 'Keys' in instruments
        
        # give points for rhythm section
        if has_bass and has_drums:
            score += 40
        
        # full rock band
        if has_guitar and has_bass and has_drums:
            score += 30
        
        # jazz combo
        if has_keys and has_bass and has_drums:
            score += 30
        
        # penalize if we have duplicates
        for inst, count in instrument_counts.items():
            if count > 1 and inst not in ['Guitar', 'Vocals']:
                score -= 20 * (count - 1)
            elif count > 3:
                score -= 10 * (count - 3)
        
        # reward diversity
        unique = len(set(instruments))
        score += unique * 5
        
        if score < 0:
            score = 0
        if score > 100:
            score = 100
            
        return score
    
    def h_skill_variance(self, group):
        
        if len(group) < 2:
            return 100.0
        
        skills = []
        for m in group:
            skills.append(m.skill_level)
        
        skill_range = max(skills) - min(skills)
        
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
    
    def h_genre_consensus(self, group):
        
        if len(group) < 2:
            return 100.0
        
        all_genres = []
        for musician in group:
            for g in musician.genres:
                all_genres.append(g)
        
        # count genres
        from collections import Counter
        genre_counts = Counter(all_genres)
        
        threshold = len(group) / 2
        common_genres = []
        for g, count in genre_counts.items():
            if count >= threshold:
                common_genres.append(g)
        
        if not common_genres:
            return 20.0
        
        consensus_strength = 0
        for g in common_genres:
            consensus_strength += genre_counts[g]
        consensus_strength = consensus_strength / len(all_genres)
        
        base = len(common_genres) * 25
        bonus = consensus_strength * 50
        
        total = base + bonus
        if total > 100:
            total = 100
            
        return total
    
    def h_role_balance(self, group):
        
        if not group:
            return 100.0
        
        leaders = 0
        supporters = 0
        for m in group:
            if m.personality_leader > 0.6:
                leaders += 1
            elif m.personality_leader < 0.4:
                supporters += 1
        
        flexible = len(group) - leaders - supporters
        
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
    
    def combined_heuristic(self, group):
        # combine all 4 heuristics
        
        synergy = self.h_instrument_synergy(group)
        variance = self.h_skill_variance(group)
        consensus = self.h_genre_consensus(group)
        balance = self.h_role_balance(group)
        
        combined = (
            0.30 * synergy +
            0.30 * variance +
            0.25 * consensus +
            0.15 * balance
        )
        
        return combined

class AStarGroupFormation:
    
    def __init__(self):
        self.heuristics = GroupFormationHeuristics()
        self.constraint_checker = ConstraintChecker()
        self.nodes_explored = 0
    
    def is_goal_state(self, group, time_slot):
        if len(group) < 3:
            return False
        
        if not self.constraint_checker.check_group_size(group):
            return False
        
        if not self.constraint_checker.check_availability(group, time_slot):
            return False
        
        if not self.constraint_checker.check_rhythm_section(group):
            return False
        
        return True
    
    def get_successors(self, current_group, available_pool, time_slot):
        successors = []
        
        if len(current_group) >= 6:
            return successors
        
        for musician in available_pool:
            new_group = current_group + [musician]
            
            if self.constraint_checker.check_availability(new_group, time_slot):
                successors.append((new_group, musician))
        
        return successors
    
    def search(self, available_musicians, time_slot, max_group_size=6):
        # A* search implementation
        
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
        best_score = -999999
        
        # limit search to avoid going forever
        while frontier and self.nodes_explored < 1000:
            current = heapq.heappop(frontier)
            self.nodes_explored += 1
            
            current_group = current.musicians
            
            # signature to check if we've seen this state
            ids = []
            for m in current_group:
                ids.append(m.id)
            state_signature = tuple(sorted(ids))
            
            if state_signature in explored:
                continue
            explored.add(state_signature)
            
            if self.is_goal_state(current_group, time_slot):
                quality = self.heuristics.combined_heuristic(current_group)
                
                if quality > best_score:
                    best_score = quality
                    best_complete_group = current_group
                
                if len(current_group) >= max_group_size:
                    continue
            
            remaining_pool = []
            for m in current.available_pool:
                if m not in current_group:
                    remaining_pool.append(m)
            
            successors = self.get_successors(current_group, remaining_pool, time_slot)
            
            for new_group, added_musician in successors:
                # cost = negative quality (since we're minimizing)
                g_cost = -self.heuristics.combined_heuristic(new_group)
                
                # heuristic = potential improvement from adding more
                remaining_slots = max_group_size - len(new_group)
                h_cost = -remaining_slots * 10
                
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


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from csp_solver import BasicCSPSolver
    
    print("Testing A* Group Formation")
    print("="*70)
    
    solver = BasicCSPSolver()
    musicians = solver.load_musicians('data/musicians_dataset.json')
    
    test_time_slot = "Fri_18-21"
    
    available = []
    for m in musicians:
        if test_time_slot in m.availability:
            available.append(m)
    
    print(f"\nTime Slot: {test_time_slot}")
    print(f"Available Musicians: {len(available)}")
    
    astar = AStarGroupFormation()
    best_group = astar.search(available, test_time_slot)
    
    if best_group:
        print(f"\nA* found optimal group ({len(best_group)} musicians)")
        print(f"Nodes explored: {astar.nodes_explored}")
        
        heuristics = GroupFormationHeuristics()
        
        print(f"\nMusicians:")
        for m in best_group:
            print(f"  - {m.name} ({m.instrument}, Skill {m.skill_level})")
            genre_str = ', '.join(m.genres)
            print(f"    Genres: {genre_str}")
        
        print(f"\nHeuristic Scores:")
        print(f"  Instrument Synergy: {heuristics.h_instrument_synergy(best_group):.1f}%")
        print(f"  Skill Variance: {heuristics.h_skill_variance(best_group):.1f}%")
        print(f"  Genre Consensus: {heuristics.h_genre_consensus(best_group):.1f}%")
        print(f"  Role Balance: {heuristics.h_role_balance(best_group):.1f}%")
        print(f"  Combined Score: {heuristics.combined_heuristic(best_group):.1f}%")
    else:
        print("\nNo valid group found")
    
    # compare with greedy
    print("\n" + "="*70)
    print("COMPARISON: A* vs Greedy")
    print("="*70)
    
    greedy_group = available[:4] if len(available) >= 4 else available
    
    if len(greedy_group) >= 3:
        print(f"\nGreedy Group ({len(greedy_group)} musicians):")
        for m in greedy_group:
            print(f"  - {m.name} ({m.instrument}, Skill {m.skill_level})")
        
        greedy_score = heuristics.combined_heuristic(greedy_group)
        astar_score = heuristics.combined_heuristic(best_group) if best_group else 0
        
        print(f"\nGreedy Score: {greedy_score:.1f}%")
        print(f"A* Score: {astar_score:.1f}%")
        improvement = astar_score - greedy_score
        print(f"Improvement: {improvement:+.1f} points")