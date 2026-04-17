const fs = require('fs');
let code = fs.readFileSync('backend/app.py', 'utf8');
if (!code.includes('/api/instagram')) {
  const insertIndex = code.indexOf("@app.route('/api/schedule'");
  const newEndpoint = `
@app.route('/api/instagram', methods=['POST'])
def get_instagram_posts():
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id or session_id not in orchestrator_sessions:
        return jsonify({"error": "Invalid or missing session_id"}), 400
        
    orchestrator = orchestrator_sessions[session_id]
    
    try:
        insta_results = orchestrator.call_instagram_agent(memory=orchestrator.memory)
        return jsonify({"instagram": insta_results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

`;
  code = code.slice(0, insertIndex) + newEndpoint + code.slice(insertIndex);
  fs.writeFileSync('backend/app.py', code);
  console.log('Added /api/instagram');
} else {
  console.log('Already has /api/instagram');
}
