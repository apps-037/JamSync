# backend/api.py
"""
Flask API for JamSync - Complete Version
"""
from flask import Flask, request, jsonify, make_response
from csp_solver import BasicCSPSolver, Musician
from astar_grouping import AStarGroupFormation, GroupFormationHeuristics
import sys
import os

app = Flask(__name__)

# CORS configuration - handle preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        response.headers.add("Access-Control-Max-Age", "3600")
        return response, 200

# Add CORS headers to all responses
@app.after_request  
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response

# Initialize solver
print("Loading musicians dataset...")
solver = BasicCSPSolver(use_adversarial_prediction=True, use_astar=True)
static_musicians = solver.load_musicians()
print(f"✓ Loaded {len(static_musicians)} musicians")

@app.route('/')
def home():
    """Root endpoint"""
    return jsonify({
        'message': 'JamSync API',
        'version': '1.0',
        'endpoints': [
            'GET /api/health',
            'POST /api/find-sessions'
        ]
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if API is running"""
    return jsonify({
        'status': 'healthy', 
        'musicians': len(static_musicians),
        'message': 'JamSync API is running!'
    })

@app.route('/api/find-sessions', methods=['POST'])
def find_sessions():
    try:
        user_data = request.get_json()
        
        if not user_data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        print(f"\nReceived request for: {user_data.get('name', 'Unknown')}")
        print(f"   Instrument: {user_data.get('instrument')}")
        print(f"   Skill: {user_data.get('skill_level')}")
        print(f"   Availability slots: {len(user_data.get('availability', []))}")
        
        # Validate required fields
        required_fields = ['name', 'instrument', 'skill_level', 'genres', 'availability', 'location']
        for field in required_fields:
            if field not in user_data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Create temporary musician
        new_musician = Musician(
            id=101,
            name=user_data['name'],
            instrument=user_data['instrument'],
            skill_level=int(user_data['skill_level']),
            genres=user_data['genres'],
            availability=user_data['availability'],
            location=user_data['location'],
            personality_leader=float(user_data.get('personality_leader', 0.5)),
            personality_improviser=float(user_data.get('personality_improviser', 0.5))
        )
        
        print(f"   Finding compatible sessions...")
        
        heuristics = GroupFormationHeuristics()
        recommendations = []
        session_id = 1
        
        for time_slot in new_musician.availability[:10]:
            compatible = []
            
            for m in static_musicians:
                if time_slot not in m.availability:
                    continue
                
                skill_diff = abs(m.skill_level - new_musician.skill_level)
                genre_overlap = len(set(m.genres) & set(new_musician.genres))
                
                if skill_diff <= 4 and genre_overlap >= 1:
                    compatible.append({
                        'musician': m,
                        'skill_diff': skill_diff,
                        'genre_overlap': genre_overlap
                    })
            
            compatible.sort(key=lambda x: (x['genre_overlap'], -x['skill_diff']), reverse=True)
            
            if len(compatible) < 2:
                continue
            
            # Take top 3-5 compatible musicians
            group_size = min(5, len(compatible))
            session_musicians = [new_musician] + [c['musician'] for c in compatible[:group_size]]
            
            has_rhythm = any(m.instrument in ['Drums', 'Bass'] for m in session_musicians)
            
            if not has_rhythm:
                for c in compatible:
                    if c['musician'].instrument in ['Drums', 'Bass']:
                        if c['musician'] not in session_musicians:
                            session_musicians.append(c['musician'])
                            has_rhythm = True
                            break
            
            # Only keep sessions with 3-6 musicians and rhythm section
            if 3 <= len(session_musicians) <= 6 and has_rhythm:
                quality = heuristics.combined_heuristic(session_musicians)
                
                recommendations.append({
                    'id': session_id,
                    'time_slot': time_slot,
                    'location': new_musician.location,
                    'quality_score': round(quality, 1),
                    'num_musicians': len(session_musicians),
                    'musicians': [
                        {
                            'name': m.name,
                            'instrument': m.instrument,
                            'skill_level': m.skill_level,
                            'genres': m.genres
                        }
                        for m in session_musicians if m.id != new_musician.id
                    ]
                })
                session_id += 1
        
        # Sort by quality
        recommendations.sort(key=lambda x: x['quality_score'], reverse=True)
        
        # Take top 5
        top_recommendations = recommendations[:5]
        
        print(f"Found {len(top_recommendations)} matching sessions")
        if top_recommendations:
            print(f"   Best quality: {top_recommendations[0]['quality_score']:.1f}%")
        
        return jsonify({
            'success': True,
            'recommendations': top_recommendations,
            'total_found': len(recommendations),
            'user_name': new_musician.name
        }), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/all-sessions', methods=['GET'])
def get_all_sessions():
    """Get all generated sessions (admin view)"""
    try:
        print("\nGenerating full schedule for all musicians...")
        
        full_solver = BasicCSPSolver(use_adversarial_prediction=True, use_astar=True)
        full_solver.sessions_created = []
        full_solver.assigned_musicians = set()
        
        sessions = full_solver.solve(static_musicians)
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': session.id,
                'time_slot': session.time_slot,
                'location': session.location,
                'quality_score': session.quality_score,
                'num_musicians': len(session.musicians),
                'musicians': [
                    {
                        'name': m.name,
                        'instrument': m.instrument,
                        'skill_level': m.skill_level,
                        'genres': m.genres
                    }
                    for m in session.musicians
                ]
            })
        
        return jsonify({
            'success': True,
            'sessions': sessions_data,
            'total_sessions': len(sessions_data),
            'total_musicians': len(static_musicians),
            'musicians_matched': len(full_solver.assigned_musicians)
        }), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found', 'path': request.path}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🎵 JAMSYNC API SERVER")
    print("="*70)
    print(f"\n✓ Loaded {len(static_musicians)} musicians")
    print(f"✓ Using Hybrid algorithm (A* + Adversarial Prediction)")
    print(f"\nServer running on http://localhost:5000")
    print("\nEndpoints:")
    print("   GET  http://localhost:5000/")
    print("   GET  http://localhost:5000/api/health")
    print("   POST http://localhost:5000/api/find-sessions")
    print("   GET  http://localhost:5000/api/all-sessions")
    print("\nCORS enabled for all origins")
    print("\nPress Ctrl+C to stop")
    print("="*70 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True,
        use_reloader=False
    )