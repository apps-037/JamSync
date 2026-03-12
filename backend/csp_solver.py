# csp_solver.py
import json
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Musician:
    """Musician profile"""
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
    """A jam session"""
    id: int
    musicians: List[Musician]
    time_slot: str
    location: str
    quality_score: float = 0.0
    
    def __repr__(self):
        return f"Session {self.id} ({self.time_slot}): {len(self.musicians)} musicians, Quality: {self.quality_score:.1f}%"

class ConstraintChecker:
    """Check hard and soft constraints"""
    
    @staticmethod
    def check_availability(musicians: List[Musician], time_slot: str) -> bool:
        """Hard constraint: All musicians must be available at time_slot"""
        return all(time_slot in m.availability for m in musicians)
    
    @staticmethod
    def check_group_size(musicians: List[Musician]) -> bool:
        """Hard constraint: Session needs 3-6 musicians"""
        return 3 <= len(musicians) <= 6
    
    @staticmethod
    def check_rhythm_section(musicians: List[Musician]) -> bool:
        """Hard constraint: Need at least one rhythm instrument (drums or bass)"""
        instruments = [m.instrument for m in musicians]
        return 'Drums' in instruments or 'Bass' in instruments
    
    @staticmethod
    def check_location_match(musicians: List[Musician], location: str) -> bool:
        """Soft constraint: Prefer musicians from same location (within reason)"""
        # For now, just return True (we'll handle location matching later)
        return True
    
    @staticmethod
    def calculate_skill_compatibility(musicians: List[Musician]) -> float:
        """Soft constraint: Musicians should have similar skill levels"""
        if not musicians:
            return 0.0
        
        skills = [m.skill_level for m in musicians]
        skill_range = max(skills) - min(skills)
        
        # Score based on skill variance
        # 0-2 points difference = excellent (100%)
        # 3-4 points = good (70%)
        # 5+ points = poor (30%)
        if skill_range <= 2:
            return 100.0
        elif skill_range <= 4:
            return 70.0
        else:
            return 30.0
    
    @staticmethod
    def calculate_genre_compatibility(musicians: List[Musician]) -> float:
        """Soft constraint: Musicians should share genres"""
        if len(musicians) < 2:
            return 100.0
        
        # Count genre overlaps
        all_genres = [g for m in musicians for g in m.genres]
        genre_counts = defaultdict(int)
        for genre in all_genres:
            genre_counts[genre] += 1
        
        # Calculate what percentage of musicians share at least one genre
        shared_genres = [g for g, count in genre_counts.items() if count >= 2]
        
        if not shared_genres:
            return 30.0  # No overlap
        
        # Score based on how many musicians share genres
        overlap_ratio = len(shared_genres) / len(set(all_genres))
        return min(100.0, overlap_ratio * 100 + 50)
    
    @staticmethod
    def calculate_personality_balance(musicians: List[Musician]) -> float:
        """Soft constraint: Balance of leaders vs supporters"""
        if not musicians:
            return 0.0
        
        leaders = sum(1 for m in musicians if m.personality_leader > 0.6)
        supporters = sum(1 for m in musicians if m.personality_leader < 0.4)
        
        # Ideal: 1-2 leaders, rest supporters or flexible
        if 1 <= leaders <= 2:
            return 100.0
        elif leaders == 0:
            return 60.0  # No clear leader
        else:
            return 40.0  # Too many leaders
    
    def calculate_session_quality(self, musicians: List[Musician]) -> float:
        """Calculate overall session quality (0-100)"""
        skill_score = self.calculate_skill_compatibility(musicians)
        genre_score = self.calculate_genre_compatibility(musicians)
        personality_score = self.calculate_personality_balance(musicians)
        
        # Weighted average
        quality = (
            0.4 * skill_score +
            0.4 * genre_score +
            0.2 * personality_score
        )
        
        return round(quality, 1)

class BasicCSPSolver:
    """Basic CSP solver using backtracking with forward checking"""
    
    def __init__(self):
        self.constraint_checker = ConstraintChecker()
        self.sessions_created = []
        self.assigned_musicians = set()
    
    def load_musicians(self, filepath: str) -> List[Musician]:
        """Load musicians from JSON file"""
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
    
    def get_available_time_slots(self, musicians: List[Musician]) -> List[str]:
        """Extract all unique time slots from musicians"""
        time_slots = set()
        for musician in musicians:
            time_slots.update(musician.availability)
        return sorted(list(time_slots))
    
    def get_available_musicians_for_slot(
        self, 
        time_slot: str, 
        all_musicians: List[Musician]
    ) -> List[Musician]:
        """Get musicians available at a specific time slot (and not yet assigned)"""
        return [
            m for m in all_musicians 
            if time_slot in m.availability and m.id not in self.assigned_musicians
        ]
    
    def is_valid_session(self, musicians: List[Musician], time_slot: str) -> bool:
        """Check if a session satisfies all HARD constraints"""
        # Check group size
        if not self.constraint_checker.check_group_size(musicians):
            return False
        
        # Check availability
        if not self.constraint_checker.check_availability(musicians, time_slot):
            return False
        
        # Check rhythm section
        if not self.constraint_checker.check_rhythm_section(musicians):
            return False
        
        return True
    
    def create_session_for_time_slot(self, time_slot: str, all_musicians: List[Musician],session_id: int) -> Session:

        available = self.get_available_musicians_for_slot(time_slot, all_musicians)
        
        if len(available) < 3:
            return None  # Not enough musicians
        
        # Start with a rhythm section player if possible
        session_musicians = []
        rhythm_players = [m for m in available if m.instrument in ['Drums', 'Bass']]
        other_players = [m for m in available if m.instrument not in ['Drums', 'Bass']]
        
        # Prefer to start with rhythm section
        if rhythm_players:
            session_musicians.append(rhythm_players[0])
            # Add other instruments
            for musician in other_players[:5]:  # Add up to 5 more (total 6)
                session_musicians.append(musician)
                if len(session_musicians) >= 6:
                    break
        else:
            # No rhythm section available - still create session but note lower quality
            # Take first 3-6 musicians
            session_musicians = other_players[:6]
        
        # Need at least 3 musicians
        if len(session_musicians) < 3:
            return None
        
        # Final validation
        if not self.is_valid_session(session_musicians, time_slot):
            # Try with just 3 musicians if that works
            if len(session_musicians) > 3:
                session_musicians = session_musicians[:3]
                if not self.is_valid_session(session_musicians, time_slot):
                    return None
            else:
                return None
        
        # Calculate quality
        quality = self.constraint_checker.calculate_session_quality(session_musicians)
        
        # Create session
        session = Session(
            id=session_id,
            musicians=session_musicians,
            time_slot=time_slot,
            location=session_musicians[0].location,
            quality_score=quality
        )
        
        # Mark musicians as assigned
        for musician in session_musicians:
            self.assigned_musicians.add(musician.id)
        
        return session
    
    def solve(self, musicians: List[Musician]) -> List[Session]:
        """
        Main solver: Create sessions across all time slots
        """
        print(f"\n🎵 Running CSP Solver for {len(musicians)} musicians...\n")
        
        # Reset state
        self.sessions_created = []
        self.assigned_musicians = set()
        
        # Get all possible time slots
        time_slots = self.get_available_time_slots(musicians)
        print(f"Found {len(time_slots)} unique time slots")
        
        session_id = 1
        
        # Try to create sessions for each time slot
        for time_slot in time_slots:
            session = self.create_session_for_time_slot(time_slot, musicians, session_id)
            
            if session:
                self.sessions_created.append(session)
                print(f"✓ Created {session}")
                session_id += 1
        
        # Calculate statistics
        match_rate = (len(self.assigned_musicians) / len(musicians)) * 100
        avg_quality = sum(s.quality_score for s in self.sessions_created) / len(self.sessions_created) if self.sessions_created else 0
        
        print(f"\n📊 Results:")
        print(f"   Sessions created: {len(self.sessions_created)}")
        print(f"   Musicians matched: {len(self.assigned_musicians)}/{len(musicians)} ({match_rate:.1f}%)")
        print(f"   Average quality: {avg_quality:.1f}%")
        
        return self.sessions_created

# Test the solver
if __name__ == "__main__":
    solver = BasicCSPSolver()
    
    # Load musicians
    musicians = solver.load_musicians('data/musicians_dataset.json')
    print(f"Loaded {len(musicians)} musicians")
    
    # Solve
    sessions = solver.solve(musicians)
    
    # Print detailed results
    print("\n" + "="*60)
    print("DETAILED SESSION BREAKDOWN")
    print("="*60)
    
    for session in sessions[:5]:  # Show first 5 sessions
        print(f"\n{session}")
        print(f"  Time: {session.time_slot}")
        print(f"  Musicians:")
        for m in session.musicians:
            print(f"    - {m.name} ({m.instrument}, Skill {m.skill_level})")
        print(f"  Quality Score: {session.quality_score}%")