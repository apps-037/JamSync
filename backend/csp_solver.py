# csp_solver.py
# CSP solver for musician scheduling

import json
from typing import List
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Musician:
    id: int
    name: str
    instrument: str
    skill_level: int
    genres: List[str]
    availability: List[str]
    location: str
    personality_leader: float
    personality_improviser: float

@dataclass
class Session:
    id: int
    musicians: List[Musician]
    time_slot: str
    location: str
    quality_score: float = 0.0
    
    def __repr__(self):
        return f"Session {self.id} ({self.time_slot}): {len(self.musicians)} musicians, Quality: {self.quality_score:.1f}%"

class ConstraintChecker:
    
    @staticmethod
    def check_availability(musicians, time_slot):
        # all musicians must be free at this time
        for m in musicians:
            if time_slot not in m.availability:
                return False
        return True
    
    @staticmethod
    def check_group_size(musicians):
        # need 3-6 people
        return 3 <= len(musicians) <= 6
    
    @staticmethod
    def check_rhythm_section(musicians):
        # need at least one drummer or bassist
        instruments = []
        for m in musicians:
            instruments.append(m.instrument)
        return 'Drums' in instruments or 'Bass' in instruments
    
    @staticmethod
    def calculate_skill_compatibility(musicians):
        # musicians should have similar skill levels
        
        if not musicians:
            return 0.0
        
        skills = []
        for m in musicians:
            skills.append(m.skill_level)
        
        skill_range = max(skills) - min(skills)
        
        if skill_range <= 2:
            return 100.0
        elif skill_range <= 4:
            return 70.0
        else:
            return 30.0
    
    @staticmethod
    def calculate_genre_compatibility(musicians):
        # musicians should share some genres
        
        if len(musicians) < 2:
            return 100.0
        
        all_genres = []
        for m in musicians:
            for g in m.genres:
                all_genres.append(g)
        
        genre_counts = defaultdict(int)
        for genre in all_genres:
            genre_counts[genre] += 1
        
        # genres that appear in multiple musicians
        shared_genres = []
        for g, count in genre_counts.items():
            if count >= 2:
                shared_genres.append(g)
        
        if not shared_genres:
            return 30.0
        
        overlap_ratio = len(shared_genres) / len(set(all_genres))
        score = overlap_ratio * 100 + 50
        if score > 100:
            score = 100
        return score
    
    @staticmethod
    def calculate_personality_balance(musicians):
        
        if not musicians:
            return 0.0
        
        leaders = 0
        for m in musicians:
            if m.personality_leader > 0.6:
                leaders += 1
        
        if 1 <= leaders <= 2:
            return 100.0
        elif leaders == 0:
            return 60.0
        else:
            return 40.0
    
    def calculate_session_quality(self, musicians):
        # overall quality combines skill, genre, and personality
        
        skill_score = self.calculate_skill_compatibility(musicians)
        genre_score = self.calculate_genre_compatibility(musicians)
        personality_score = self.calculate_personality_balance(musicians)
        
        quality = (
            0.4 * skill_score +
            0.4 * genre_score +
            0.2 * personality_score
        )
        
        return round(quality, 1)

class BasicCSPSolver:
    
    def __init__(self, use_adversarial_prediction=False, use_astar=False):
        self.constraint_checker = ConstraintChecker()
        self.sessions_created = []
        self.assigned_musicians = set()
        self.use_adversarial_prediction = use_adversarial_prediction
        self.use_astar = use_astar
        
        if use_adversarial_prediction:
            from adversarial_quality import AdversarialQualityPredictor
            self.adversarial_predictor = AdversarialQualityPredictor()
        
        if use_astar:
            from astar_grouping import AStarGroupFormation
            self.astar_grouper = AStarGroupFormation()
    
    def load_musicians(self, filepath='data/musicians_dataset.json'):
        import os
        if not os.path.isabs(filepath):
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = os.path.join(project_root, filepath)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        musicians = []
        for m_data in data:
            musician = Musician(
                id=m_data['id'],
                name=m_data['name'],
                instrument=m_data['instrument'],
                skill_level=m_data['skill_level'],
                genres=m_data['genres'],
                availability=m_data['availability'],
                location=m_data['location'],
                personality_leader=m_data['personality_leader'],
                personality_improviser=m_data['personality_improviser']
            )
            musicians.append(musician)
        
        return musicians
    
    def get_available_time_slots(self, musicians):
        time_slots = set()
        for musician in musicians:
            for slot in musician.availability:
                time_slots.add(slot)
        return sorted(list(time_slots))
    
    def get_available_musicians_for_slot(self, time_slot, all_musicians):
        available = []
        for m in all_musicians:
            if time_slot in m.availability and m.id not in self.assigned_musicians:
                available.append(m)
        return available
    
    def is_valid_session(self, musicians, time_slot):
        if not self.constraint_checker.check_group_size(musicians):
            return False
        
        if not self.constraint_checker.check_availability(musicians, time_slot):
            return False
        
        if not self.constraint_checker.check_rhythm_section(musicians):
            return False
        
        return True
    
    def create_session_for_time_slot(self, time_slot, all_musicians, session_id):
        available = self.get_available_musicians_for_slot(time_slot, all_musicians)
        
        if len(available) < 3:
            return None
        
        # use A* if enabled
        if self.use_astar:
            session_musicians = self.astar_grouper.search(available, time_slot, max_group_size=6)
            
            if not session_musicians or len(session_musicians) < 3:
                return None
        
        else:
            session_musicians = []
            rhythm_players = []
            other_players = []
            
            for m in available:
                if m.instrument in ['Drums', 'Bass']:
                    rhythm_players.append(m)
                else:
                    other_players.append(m)
            
            if rhythm_players:
                session_musicians.append(rhythm_players[0])
                count = 0
                for musician in other_players:
                    if len(session_musicians) >= 6:
                        break
                    session_musicians.append(musician)
                    count += 1
                    if count >= 5:
                        break
            else:
                for i in range(min(6, len(other_players))):
                    session_musicians.append(other_players[i])
            
            if len(session_musicians) < 3:
                return None
            
            if not self.is_valid_session(session_musicians, time_slot):
                if len(session_musicians) > 3:
                    session_musicians = session_musicians[:3]
                    if not self.is_valid_session(session_musicians, time_slot):
                        return None
                else:
                    return None
        
        # get quality score
        if self.use_adversarial_prediction:
            from adversarial_quality import AdversarialQualityPredictor
            predictor = AdversarialQualityPredictor()
            prediction = predictor.predict_session_quality(session_musicians)
            quality = prediction['quality_score']
        else:
            quality = self.constraint_checker.calculate_session_quality(session_musicians)
        
        session = Session(
            id=session_id,
            musicians=session_musicians,
            time_slot=time_slot,
            location=session_musicians[0].location,
            quality_score=quality
        )
        
        for musician in session_musicians:
            self.assigned_musicians.add(musician.id)
        
        return session
    
    def solve(self, musicians):
        solver_name = "CSP"
        if self.use_astar:
            solver_name += " + A*"
        if self.use_adversarial_prediction:
            solver_name += " + Adversarial"
        
        print(f"\nRunning {solver_name} for {len(musicians)} musicians...\n")
        
        self.sessions_created = []
        self.assigned_musicians = set()
        
        time_slots = self.get_available_time_slots(musicians)
        print(f"Found {len(time_slots)} unique time slots")
        
        session_id = 1
        
        for time_slot in time_slots:
            session = self.create_session_for_time_slot(time_slot, musicians, session_id)
            
            if session:
                self.sessions_created.append(session)
                print(f"Created {session}")
                session_id += 1
        
        match_rate = (len(self.assigned_musicians) / len(musicians)) * 100
        
        if len(self.sessions_created) > 0:
            total_quality = 0
            for s in self.sessions_created:
                total_quality += s.quality_score
            avg_quality = total_quality / len(self.sessions_created)
        else:
            avg_quality = 0
        
        print(f"\nResults:")
        print(f"   Sessions created: {len(self.sessions_created)}")
        print(f"   Musicians matched: {len(self.assigned_musicians)}/{len(musicians)} ({match_rate:.1f}%)")
        print(f"   Average quality: {avg_quality:.1f}%")
        
        return self.sessions_created


if __name__ == "__main__":
    print("="*70)
    print("ALGORITHM COMPARISON")
    print("="*70)
    
    print("\n### APPROACH 1: Basic CSP (Greedy) ###\n")
    solver1 = BasicCSPSolver(use_adversarial_prediction=False, use_astar=False)
    musicians = solver1.load_musicians()
    sessions1 = solver1.solve(musicians)
    
    print("\n### APPROACH 2: CSP + A* ###\n")
    solver2 = BasicCSPSolver(use_adversarial_prediction=False, use_astar=True)
    musicians = solver2.load_musicians()
    sessions2 = solver2.solve(musicians)
    
    print("\n### APPROACH 3: Hybrid (A* + Adversarial) ###\n")
    solver3 = BasicCSPSolver(use_adversarial_prediction=True, use_astar=True)
    musicians = solver3.load_musicians()
    sessions3 = solver3.solve(musicians)
    
    print("\n" + "="*70)
    print("FINAL COMPARISON")
    print("="*70)
    
    print(f"\n{'Algorithm':<30} {'Sessions':<12} {'Match Rate':<15} {'Avg Quality':<15}")
    print("-" * 70)
    
    results = [
        ('Greedy CSP', sessions1, solver1),
        ('CSP + A*', sessions2, solver2),
        ('Hybrid (A* + Adversarial)', sessions3, solver3)
    ]
    
    for name, sessions, solver_obj in results:
        match_rate = (len(solver_obj.assigned_musicians) / 100) * 100
        
        if len(sessions) > 0:
            total_q = 0
            for s in sessions:
                total_q += s.quality_score
            avg_quality = total_q / len(sessions)
        else:
            avg_quality = 0
            
        print(f"{name:<30} {len(sessions):<12} {match_rate:<15.1f}% {avg_quality:<15.1f}%")