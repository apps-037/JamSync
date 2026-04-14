# adversarial_quality.py
# Quality prediction using Nash Equilibrium from game theory
# Based on Russell & Norvig Ch 5 (adversarial search)

from typing import List, Dict
from dataclasses import dataclass
from csp_solver import Musician, Session

@dataclass
class MusicianUtility:
    musician_id: int
    spotlight_utility: float
    skill_validation_utility: float 
    genre_comfort_utility: float 
    role_satisfaction_utility: float  
    total_utility: float

class AdversarialQualityPredictor:
    
    def __init__(self):
        self.weights = {
            'spotlight': 0.25,
            'skill_validation': 0.35, 
            'genre_comfort': 0.25,
            'role_satisfaction': 0.15
        }
    
    def calculate_spotlight_utility(self, musician, session_musicians):
        
        num_leaders = 0
        for m in session_musicians:
            if m.personality_leader > 0.6:
                num_leaders += 1
        
        # If this musician is a leader type
        if musician.personality_leader > 0.6:  
            if num_leaders == 1:
                return 100.0 
            elif num_leaders == 2:
                return 80.0 
            elif num_leaders == 3:
                return 50.0 
            else:
                return 20.0  
        
        # If this musician likes to support
        elif musician.personality_leader < 0.4:
            if num_leaders >= 1 and num_leaders <= 2:
                return 100.0 
            elif num_leaders == 0:
                return 40.0 
            else:
                return 70.0  
        
        else: 
            return 80.0
    
    def calculate_skill_validation_utility(self, musician, session_musicians):
        
        other_musicians = [m for m in session_musicians if m.id != musician.id]
        if not other_musicians:
            return 50.0
        
        other_skills = [m.skill_level for m in other_musicians]
        avg_other = sum(other_skills) / len(other_skills)
        
        gap = abs(musician.skill_level - avg_other)
        
        # sweet spot is being close but not identical
        if gap <= 1:
            return 100.0
        elif gap <= 2:
            return 85.0
        elif gap <= 3:
            return 60.0
        elif gap <= 4:
            return 35.0
        else:
            return 10.0  
    
    def calculate_genre_comfort_utility(self, musician, session_musicians):
        
        other_musicians = [m for m in session_musicians if m.id != musician.id]
        
        my_genres = set(musician.genres)
        other_genres = set()
        for m in other_musicians:
            for g in m.genres:
                other_genres.add(g)
        
        overlap = my_genres & other_genres
        
        if not other_genres:
            return 50.0
        
        overlap_ratio = len(overlap) / len(my_genres)
        
        if overlap_ratio >= 0.75:
            return 100.0 
        elif overlap_ratio >= 0.5:
            return 90.0 
        elif overlap_ratio >= 0.33:
            return 65.0  
        elif overlap_ratio > 0:
            return 40.0  
        else:
            return 10.0  
    
    def calculate_role_satisfaction_utility(self, musician, session_musicians):
        
        # calculate group average
        total_improv = 0
        for m in session_musicians:
            total_improv += m.personality_improviser
        avg_improv = total_improv / len(session_musicians)
        
        # if this musician loves to improvise
        if musician.personality_improviser > 0.7:
            if avg_improv > 0.6:
                return 100.0 
            elif avg_improv > 0.4:
                return 75.0 
            else:
                return 40.0 
        
        # if this musician prefers structure
        elif musician.personality_improviser < 0.3:
            if avg_improv < 0.4:
                return 100.0  
            elif avg_improv < 0.6:
                return 75.0  
            else:
                return 40.0 
        
        else:  
            return 85.0
    
    def calculate_musician_utility(self, musician, session_musicians):
        
        spot = self.calculate_spotlight_utility(musician, session_musicians)
        skill = self.calculate_skill_validation_utility(musician, session_musicians)
        genre = self.calculate_genre_comfort_utility(musician, session_musicians)
        role = self.calculate_role_satisfaction_utility(musician, session_musicians)
        
        total = (
            self.weights['spotlight'] * spot +
            self.weights['skill_validation'] * skill +
            self.weights['genre_comfort'] * genre +
            self.weights['role_satisfaction'] * role
        )
        
        return MusicianUtility(
            musician_id=musician.id,
            spotlight_utility=spot,
            skill_validation_utility=skill,
            genre_comfort_utility=genre,
            role_satisfaction_utility=role,
            total_utility=total
        )
    
    def predict_session_quality(self, session_musicians):
        
        utilities = []
        details = {}
        
        for musician in session_musicians:
            util = self.calculate_musician_utility(musician, session_musicians)
            utilities.append(util.total_utility)
            details[musician.name] = util
        
        # stats
        avg = sum(utilities) / len(utilities)
        min_util = min(utilities)
        max_util = max(utilities)
        
        # variance calculation
        var = 0
        for u in utilities:
            var += (u - avg) ** 2
        var = var / len(utilities)
        
        stability = min_util
        
        quality = (
            0.4 * avg +     
            0.4 * min_util + 
            0.2 * (100 - var)    
        )
        
        return {
            'quality_score': round(quality, 1),
            'stability_score': round(stability, 1),
            'avg_utility': round(avg, 1),
            'min_utility': round(min_util, 1),
            'max_utility': round(max_util, 1),
            'variance': round(var, 1),
            'musician_utilities': details,
            'nash_equilibrium_satisfied': min_util > 60.0 
        }


# Testing code
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from csp_solver import BasicCSPSolver
    
    solver = BasicCSPSolver()
    musicians = solver.load_musicians('data/musicians_dataset.json')
    
    test_session = musicians[:4]
    
    print("Testing Adversarial Quality Predictor")
    print("="*60)
    print("\nTest Session Musicians:")
    for m in test_session:
        print(f"  - {m.name} ({m.instrument}, Skill {m.skill_level})")
        print(f"    Genres: {', '.join(m.genres)}")
        print(f"    Leader: {m.personality_leader:.2f}, Improviser: {m.personality_improviser:.2f}")
    
    predictor = AdversarialQualityPredictor()
    result = predictor.predict_session_quality(test_session)
    
    print("\n" + "="*60)
    print("QUALITY PREDICTION RESULTS")
    print("="*60)
    print(f"\nOverall Quality Score: {result['quality_score']:.1f}%")
    print(f"Stability Score (Nash): {result['stability_score']:.1f}%")
    print(f"Nash Equilibrium Satisfied: {result['nash_equilibrium_satisfied']}")
    
    print(f"\nUtility Statistics:")
    print(f"  Average: {result['avg_utility']:.1f}%")
    print(f"  Minimum: {result['min_utility']:.1f}%")
    print(f"  Maximum: {result['max_utility']:.1f}%")
    print(f"  Variance: {result['variance']:.1f}")
    
    print(f"\nIndividual Musician Utilities:")
    for name, util in result['musician_utilities'].items():
        print(f"\n  {name}:")
        print(f"    Total Utility: {util.total_utility:.1f}%")
        print(f"    - Spotlight: {util.spotlight_utility:.1f}%")
        print(f"    - Skill Match: {util.skill_validation_utility:.1f}%")
        print(f"    - Genre Comfort: {util.genre_comfort_utility:.1f}%")
        print(f"    - Role Satisfaction: {util.role_satisfaction_utility:.1f}%")