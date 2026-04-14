# test_csp.py
# unit tests for constraint checking

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.csp_solver import BasicCSPSolver, Musician, ConstraintChecker

def test_group_size():
    checker = ConstraintChecker()
    
    # test with 2 musicians - should fail
    m1 = Musician(1, "Test1", "Guitar", 5, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5)
    m2 = Musician(2, "Test2", "Drums", 5, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5)
    musicians = [m1, m2]
    
    result = checker.check_group_size(musicians)
    assert not result, "2 musicians should fail"
    
    # add one more - should pass
    m3 = Musician(3, "Test3", "Bass", 5, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5)
    musicians.append(m3)
    
    result = checker.check_group_size(musicians)
    assert result, "3 musicians should pass"
    
    # add too many - should fail
    for i in range(4, 8):
        m = Musician(i, f"Test{i}", "Guitar", 5, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5)
        musicians.append(m)
    
    result = checker.check_group_size(musicians)
    assert not result, "7 musicians should fail"
    
    print("Group size test passed")

def test_rhythm_section():
    checker = ConstraintChecker()
    
    # no drums or bass - should fail
    m1 = Musician(1, "Test1", "Guitar", 5, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5)
    m2 = Musician(2, "Test2", "Vocals", 5, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5)
    m3 = Musician(3, "Test3", "Keys", 5, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5)
    musicians = [m1, m2, m3]
    
    result = checker.check_rhythm_section(musicians)
    assert not result, "no rhythm should fail"
    
    # change to drums - should pass
    m2.instrument = "Drums"
    result = checker.check_rhythm_section(musicians)
    assert result, "drums should pass"
    
    # change to bass - should pass
    m2.instrument = "Bass"
    result = checker.check_rhythm_section(musicians)
    assert result, "bass should pass"
    
    print("Rhythm section test passed")

def test_skill_scoring():
    checker = ConstraintChecker()
    
    # all same skill
    m1 = Musician(1, "Test1", "Guitar", 7, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5)
    m2 = Musician(2, "Test2", "Drums", 7, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5)
    m3 = Musician(3, "Test3", "Bass", 7, ["Rock"], ["Mon_18-21"], "Boston", 0.5, 0.5)
    musicians = [m1, m2, m3]
    
    score = checker.calculate_skill_compatibility(musicians)
    assert score == 100.0, f"same skill should be 100, got {score}"
    
    # 2 point range
    m1.skill_level = 6
    m3.skill_level = 8
    score = checker.calculate_skill_compatibility(musicians)
    assert score == 100.0, f"2 point range should be 100, got {score}"
    
    # big gap
    m1.skill_level = 3
    m3.skill_level = 9
    score = checker.calculate_skill_compatibility(musicians)
    assert score < 50, f"big gap should score low, got {score}"
    
    print("Skill compatibility test passed")

def test_solver():
    solver = BasicCSPSolver()
    musicians = solver.load_musicians('data/musicians_dataset.json')
    
    sessions = solver.solve(musicians)
    
    assert len(sessions) > 0, "should create sessions"
    assert len(solver.assigned_musicians) > 0, "should assign musicians"
    
    # check all sessions are valid
    for session in sessions:
        assert 3 <= len(session.musicians) <= 6, "session should have 3-6 musicians"
        assert session.quality_score >= 0, "quality should be non-negative"
    
    print(f"Solver test passed - created {len(sessions)} sessions")

if __name__ == "__main__":
    print("Running tests...\n")
    test_group_size()
    test_rhythm_section()
    test_skill_scoring()
    test_solver()
    print("\nAll tests passed")