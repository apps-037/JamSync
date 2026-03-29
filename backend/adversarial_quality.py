# backend/adversarial_quality.py
"""
Adversarial Search Module for Quality Prediction
Uses Nash Equilibrium concepts to predict session harmony
"""
from typing import List, Dict, Tuple
from dataclasses import dataclass
from csp_solver import Musician, Session

@dataclass
class MusicianUtility:
    """Utility scores for a musician in a session"""
    musician_id: int
    spotlight_utility: float      # How much spotlight time they get
    skill_validation_utility: float  # Are they challenged appropriately?
    genre_comfort_utility: float   # Playing familiar music?
    role_satisfaction_utility: float  # Getting preferred role?
    total_utility: float

class AdversarialQualityPredictor:
    """
    Predict session quality using adversarial modeling
    
    Key Insight: Musicians have COMPETING objectives in a jam session:
    - Leaders want spotlight time vs Supporters want to back others up
    - Everyone wants appropriate skill challenge (not too easy, not too hard)
    - Everyone wants familiar genres vs exploring new sounds
    - Structured players vs Improvisers want different things
    
    Uses Nash Equilibrium concept: A stable session is one where
    no musician would unilaterally prefer to leave.
    """
    
    def __init__(self):
        self.weights = {
            'spotlight': 0.25,
            'skill_validation': 0.35,
            'genre_comfort': 0.25,
            'role_satisfaction': 0.15
        }
    
    def calculate_spotlight_utility(
        self, 
        musician: Musician, 
        session_musicians: List[Musician]
    ) -> float:
        """
        Calculate spotlight competition utility
        
        Leaders want spotlight, but too many leaders = conflict
        Supporters want to support, but need someone to follow
        """
        other_musicians = [m for m in session_musicians if m.id != musician.id]
        
        # Count leaders and supporters
        num_leaders = sum(1 for m in session_musicians if m.personality_leader > 0.6)
        num_supporters = sum(1 for m in session_musicians if m.personality_leader < 0.4)
        
        if musician.personality_leader > 0.6:  # This musician is a leader
            # Leaders want spotlight but not too much competition
            if num_leaders == 1:
                return 100.0  # Perfect! Only leader
            elif num_leaders == 2:
                return 80.0   # Good, can share spotlight
            elif num_leaders == 3:
                return 50.0   # Crowded, but manageable
            else:
                return 20.0   # Too many leaders competing
        
        elif musician.personality_leader < 0.4:  # This musician is a supporter
            # Supporters want someone to follow
            if num_leaders >= 1 and num_leaders <= 2:
                return 100.0  # Perfect! Clear leadership
            elif num_leaders == 0:
                return 40.0   # No one to follow
            else:
                return 70.0   # Multiple leaders to support
        
        else:  # Flexible musician
            return 80.0  # Happy in most situations
    
    def calculate_skill_validation_utility(
        self, 
        musician: Musician, 
        session_musicians: List[Musician]
    ) -> float:
        """
        Calculate skill challenge utility
        
        Musicians want to be challenged but not overwhelmed
        The "Goldilocks zone" is ±1-2 skill points
        """
        other_musicians = [m for m in session_musicians if m.id != musician.id]
        other_skills = [m.skill_level for m in other_musicians]
        
        if not other_skills:
            return 50.0
        
        avg_other_skill = sum(other_skills) / len(other_skills)
        skill_gap = abs(musician.skill_level - avg_other_skill)
        
        # Calculate utility based on gap
        if skill_gap <= 1:
            return 100.0  # Perfect match! Will learn and contribute equally
        elif skill_gap <= 2:
            return 85.0   # Good match, slight challenge
        elif skill_gap <= 3:
            return 60.0   # Manageable but not ideal
        elif skill_gap <= 4:
            return 35.0   # Significant gap, frustration likely
        else:
            return 10.0   # Too big a gap, will be frustrated or bored
    
    def calculate_genre_comfort_utility(
        self, 
        musician: Musician, 
        session_musicians: List[Musician]
    ) -> float:
        """
        Calculate genre familiarity utility
        
        Musicians want familiar territory but some variety is good
        """
        other_musicians = [m for m in session_musicians if m.id != musician.id]
        
        # Find overlapping genres
        musician_genres = set(musician.genres)
        other_genres = set()
        for m in other_musicians:
            other_genres.update(m.genres)
        
        overlap = musician_genres & other_genres
        
        if not other_genres:
            return 50.0
        
        overlap_ratio = len(overlap) / len(musician_genres)
        
        # Sweet spot: 50-100% overlap
        if overlap_ratio >= 0.75:
            return 100.0  # Very comfortable
        elif overlap_ratio >= 0.5:
            return 90.0   # Good balance of familiar and new
        elif overlap_ratio >= 0.33:
            return 65.0   # Some common ground
        elif overlap_ratio > 0:
            return 40.0   # Mostly unfamiliar
        else:
            return 10.0   # No common genres!
    
    def calculate_role_satisfaction_utility(
        self, 
        musician: Musician, 
        session_musicians: List[Musician]
    ) -> float:
        """
        Calculate role preference satisfaction
        
        Improviser vs Structured preference
        """
        other_musicians = [m for m in session_musicians if m.id != musician.id]
        
        # Calculate average improvisation preference
        avg_improv = sum(m.personality_improviser for m in session_musicians) / len(session_musicians)
        
        # If musician is strong improviser (>0.7)
        if musician.personality_improviser > 0.7:
            if avg_improv > 0.6:
                return 100.0  # Everyone likes to improvise!
            elif avg_improv > 0.4:
                return 75.0   # Mixed, but workable
            else:
                return 40.0   # Too structured for this musician
        
        # If musician prefers structure (<0.3)
        elif musician.personality_improviser < 0.3:
            if avg_improv < 0.4:
                return 100.0  # Everyone likes structure!
            elif avg_improv < 0.6:
                return 75.0   # Mixed, but workable
            else:
                return 40.0   # Too much improv for this musician
        
        else:  # Flexible
            return 85.0  # Happy with most styles
    
    def calculate_musician_utility(
        self, 
        musician: Musician, 
        session_musicians: List[Musician]
    ) -> MusicianUtility:
        """
        Calculate total utility for a musician in this session
        """
        spotlight_util = self.calculate_spotlight_utility(musician, session_musicians)
        skill_util = self.calculate_skill_validation_utility(musician, session_musicians)
        genre_util = self.calculate_genre_comfort_utility(musician, session_musicians)
        role_util = self.calculate_role_satisfaction_utility(musician, session_musicians)
        
        # Weighted sum
        total_utility = (
            self.weights['spotlight'] * spotlight_util +
            self.weights['skill_validation'] * skill_util +
            self.weights['genre_comfort'] * genre_util +
            self.weights['role_satisfaction'] * role_util
        )
        
        return MusicianUtility(
            musician_id=musician.id,
            spotlight_utility=spotlight_util,
            skill_validation_utility=skill_util,
            genre_comfort_utility=genre_util,
            role_satisfaction_utility=role_util,
            total_utility=total_utility
        )
    
    def predict_session_quality(self, session_musicians: List[Musician]) -> Dict:
        """
        Predict overall session quality using Nash Equilibrium concept
        
        A high-quality session is one where:
        1. Average utility is high (everyone is reasonably happy)
        2. Minimum utility is acceptable (no one is miserable)
        3. Variance is low (balanced satisfaction)
        
        Nash Equilibrium interpretation:
        - If min_utility is high, no musician would unilaterally choose to leave
        - This indicates a stable, sustainable jam session
        """
        utilities = []
        musician_details = {}
        
        for musician in session_musicians:
            util = self.calculate_musician_utility(musician, session_musicians)
            utilities.append(util.total_utility)
            musician_details[musician.name] = util
        
        # Calculate metrics
        avg_utility = sum(utilities) / len(utilities)
        min_utility = min(utilities)
        max_utility = max(utilities)
        
        # Calculate variance (how unequal is the satisfaction?)
        variance = sum((u - avg_utility) ** 2 for u in utilities) / len(utilities)
        
        # Nash Equilibrium stability score
        # High if min_utility is high (no one wants to leave)
        stability_score = min_utility
        
        # Overall quality (weighted combination)
        quality_score = (
            0.4 * avg_utility +      # Average happiness
            0.4 * min_utility +       # Weakest link (Nash Equilibrium)
            0.2 * (100 - variance)    # Fairness (low variance is good)
        )
        
        return {
            'quality_score': round(quality_score, 1),
            'stability_score': round(stability_score, 1),
            'avg_utility': round(avg_utility, 1),
            'min_utility': round(min_utility, 1),
            'max_utility': round(max_utility, 1),
            'variance': round(variance, 1),
            'musician_utilities': musician_details,
            'nash_equilibrium_satisfied': min_utility > 60.0  # Threshold for stability
        }

# Test the predictor
if __name__ == "__main__":
    from csp_solver import BasicCSPSolver
    
    # Load musicians
    solver = BasicCSPSolver()
    musicians = solver.load_musicians('data/musicians_dataset.json')
    
    # Create a test session
    test_session = musicians[:4]  # First 4 musicians
    
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