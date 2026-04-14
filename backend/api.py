# api.py
# Flask backend for JamSync

from flask import Flask, request, jsonify, make_response
from csp_solver import BasicCSPSolver, Musician
from astar_grouping import GroupFormationHeuristics

app = Flask(__name__)

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        response.headers.add("Access-Control-Max-Age", "3600")
        return response, 200

@app.after_request  
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response

# load the static dataset
print("Loading musicians...")
solver = BasicCSPSolver(use_adversarial_prediction=True, use_astar=True)
static_musicians = solver.load_musicians()
print(f"Loaded {len(static_musicians)} musicians")

@app.route('/')
def home():
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
    return jsonify({
        'status': 'healthy', 
        'musicians': len(static_musicians),
        'message': 'API running'
    })

@app.route('/api/find-sessions', methods=['POST'])
def find_sessions():
    try:
        user_data = request.get_json()
        
        if not user_data:
            return jsonify({'success': False, 'error': 'No data'}), 400
        
        print(f"\nRequest from: {user_data.get('name', 'Unknown')}")
        
        # check required fields
        required = ['name', 'instrument', 'skill_level', 'genres', 'availability', 'location']
        for field in required:
            if field not in user_data:
                return jsonify({'success': False, 'error': f'Missing {field}'}), 400
        
        # make a musician object from user input
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
        
        heuristics = GroupFormationHeuristics()
        recommendations = []
        session_id = 1
        
        # go through each time slot user is available
        for time_slot in new_musician.availability[:10]:
            compatible = []
            
            # find musicians available at this time
            for m in static_musicians:
                if time_slot not in m.availability:
                    continue
                
                skill_diff = abs(m.skill_level - new_musician.skill_level)
                genre_overlap = len(set(m.genres) & set(new_musician.genres))
                
                # basic compatibility check
                if skill_diff <= 4 and genre_overlap >= 1:
                    compatible.append({
                        'musician': m,
                        'skill_diff': skill_diff,
                        'genre_overlap': genre_overlap
                    })
            
            # sort by most compatible first
            compatible.sort(key=lambda x: (x['genre_overlap'], -x['skill_diff']), reverse=True)
            
            if len(compatible) < 2:
                continue
            
            # pick top musicians
            group_size = min(5, len(compatible))
            session_musicians = [new_musician]
            for c in compatible[:group_size]:
                session_musicians.append(c['musician'])
            
            # check if we have drums or bass
            has_rhythm = False
            for m in session_musicians:
                if m.instrument in ['Drums', 'Bass']:
                    has_rhythm = True
                    break
            
            # try to add rhythm section if missing
            if not has_rhythm:
                for c in compatible:
                    if c['musician'].instrument in ['Drums', 'Bass']:
                        found = False
                        for m in session_musicians:
                            if m.id == c['musician'].id:
                                found = True
                                break
                        if not found:
                            session_musicians.append(c['musician'])
                            has_rhythm = True
                            break
            
            # validate session
            if 3 <= len(session_musicians) <= 6 and has_rhythm:
                quality = heuristics.combined_heuristic(session_musicians)
                
                musicians_list = []
                for m in session_musicians:
                    if m.id != new_musician.id:
                        musicians_list.append({
                            'name': m.name,
                            'instrument': m.instrument,
                            'skill_level': m.skill_level,
                            'genres': m.genres
                        })
                
                recommendations.append({
                    'id': session_id,
                    'time_slot': time_slot,
                    'location': new_musician.location,
                    'quality_score': round(quality, 1),
                    'num_musicians': len(session_musicians),
                    'musicians': musicians_list
                })
                session_id += 1
        
        # sort by quality
        recommendations.sort(key=lambda x: x['quality_score'], reverse=True)
        
        top = recommendations[:5]
        
        print(f"Found {len(top)} sessions")
        if top:
            print(f"Best quality: {top[0]['quality_score']:.1f}%")
        
        return jsonify({
            'success': True,
            'recommendations': top,
            'total_found': len(recommendations),
            'user_name': new_musician.name
        }), 200
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/all-sessions', methods=['GET'])
def get_all_sessions():
    try:
        print("\nGenerating schedule...")
        
        full_solver = BasicCSPSolver(use_adversarial_prediction=True, use_astar=True)
        full_solver.sessions_created = []
        full_solver.assigned_musicians = set()
        
        sessions = full_solver.solve(static_musicians)
        
        sessions_data = []
        for session in sessions:
            musicians_list = []
            for m in session.musicians:
                musicians_list.append({
                    'name': m.name,
                    'instrument': m.instrument,
                    'skill_level': m.skill_level,
                    'genres': m.genres
                })
            
            sessions_data.append({
                'id': session.id,
                'time_slot': session.time_slot,
                'location': session.location,
                'quality_score': session.quality_score,
                'num_musicians': len(session.musicians),
                'musicians': musicians_list
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
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("JAMSYNC API")
    print("="*70)
    print(f"\nLoaded {len(static_musicians)} musicians")
    print(f"Using Hybrid algorithm")
    print(f"\nServer: http://localhost:5000")
    print("\nEndpoints:")
    print("   GET  /api/health")
    print("   POST /api/find-sessions")
    print("   GET  /api/all-sessions")
    print("\n" + "="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True, use_reloader=False)