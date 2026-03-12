# tests/test_csp.py
import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# test_csp.py
from backend.csp_solver import BasicCSPSolver, Musician, ConstraintChecker

def test_group_size_constraint():
    """Test that group size constraint works"""
    checker = ConstraintChecker()
    
    # Too few (2 musicians)
    musicians = [
        Musician(1, "Test1", "Guitar", 5, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5),
        Musician(2, "Test2", "Drums", 5, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5)
    ]
    assert not checker.check_group_size(musicians), "Should reject 2 musicians"
    
    # Valid (3 musicians)
    musicians.append(Musician(3, "Test3", "Bass", 5, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5))
    assert checker.check_group_size(musicians), "Should accept 3 musicians"
    
    # Too many (7 musicians)
    for i in range(4, 8):
        musicians.append(Musician(i, f"Test{i}", "Guitar", 5, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5))
    assert not checker.check_group_size(musicians), "Should reject 7 musicians"
    
    print("✓ Group size constraint test passed")

def test_rhythm_section_constraint():
    """Test that rhythm section constraint works"""
    checker = ConstraintChecker()
    
    # No rhythm section
    musicians = [
        Musician(1, "Test1", "Guitar", 5, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5),
        Musician(2, "Test2", "Vocals", 5, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5),
        Musician(3, "Test3", "Keys", 5, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5)
    ]
    assert not checker.check_rhythm_section(musicians), "Should reject session without rhythm"
    
    # Has drums
    musicians[1].instrument = "Drums"
    assert checker.check_rhythm_section(musicians), "Should accept session with drums"
    
    # Has bass
    musicians[1].instrument = "Bass"
    assert checker.check_rhythm_section(musicians), "Should accept session with bass"
    
    print("✓ Rhythm section constraint test passed")

def test_skill_compatibility():
    """Test skill compatibility scoring"""
    checker = ConstraintChecker()
    
    # Perfect match (all skill 7)
    musicians = [
        Musician(1, "Test1", "Guitar", 7, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5),
        Musician(2, "Test2", "Drums", 7, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5),
        Musician(3, "Test3", "Bass", 7, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5)
    ]
    score = checker.calculate_skill_compatibility(musicians)
    assert score == 100.0, f"Perfect skill match should be 100%, got {score}"
    
    # Good match (skills 6, 7, 8)
    musicians[0].skill_level = 6
    musicians[2].skill_level = 8
    score = checker.calculate_skill_compatibility(musicians)
    assert score == 100.0, f"2-point range should be 100%, got {score}"
    
    # Poor match (skills 3, 7, 9)
    musicians[0].skill_level = 3
    musicians[2].skill_level = 9
    score = checker.calculate_skill_compatibility(musicians)
    assert score < 50, f"Large skill gap should score low, got {score}"
    
    print("✓ Skill compatibility test passed")

def test_solver_basic():
    """Test that solver creates valid sessions"""
    solver = BasicCSPSolver()
    musicians = solver.load_musicians('data/musicians_dataset.json')
    
    sessions = solver.solve(musicians)
    
    assert len(sessions) > 0, "Should create at least one session"
    assert len(solver.assigned_musicians) > 0, "Should assign at least some musicians"
    
    # Check that all sessions are valid
    for session in sessions:
        assert 3 <= len(session.musicians) <= 6, "Session should have 3-6 musicians"
        assert session.quality_score >= 0, "Quality score should be non-negative"
    
    print(f"✓ Solver test passed: Created {len(sessions)} sessions")

if __name__ == "__main__":
    print("Running CSP Tests...\n")
    test_group_size_constraint()
    test_rhythm_section_constraint()
    test_skill_compatibility()
    test_solver_basic()
    print("\n✅ All tests passed!")