"""
Flask web application for Legal Case Analysis System
Provides interactive web interface for case analysis with audio verdict narration.

Run with: python app.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
import json
import os
from datetime import datetime
import uuid

from minor import DocumentParser, analyze_case_document, LANGCHAIN_AVAILABLE, COQUI_AVAILABLE, PYTTSX3_AVAILABLE
from config import *

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE
    app.config['DEBUG'] = FLASK_DEBUG
    
    # Create directories
    for folder in [UPLOAD_FOLDER, REPORTS_FOLDER, AUDIO_FOLDER, TEMP_FOLDER]:
        Path(folder).mkdir(exist_ok=True)
    
    # ========================================================================
    # ROUTES
    # ========================================================================
    
    @app.route('/')
    def index():
        """Home page with case upload form"""
        return render_template('index.html', 
                             llm_available=LANGCHAIN_AVAILABLE,
                             tts_available=COQUI_AVAILABLE or PYTTSX3_AVAILABLE,
                             theta_default=THETA_DEFAULT,
                             llm_weight_default=int(LLM_WEIGHT_DEFAULT * 100))
    
    @app.route('/api/analyze', methods=['POST'])
    def api_analyze():
        """API endpoint for case analysis
        
        Accepts:
            - JSON with case_text: full case document
            - OR FormData with case_file: uploaded file
            - Parameters: theta, llm_weight, enable_audio, llm_model
        
        Returns:
            JSON with verdicts, defense arguments, audio path
        """
        try:
            # Get case input
            case_text = None
            
            if 'case_file' in request.files:
                # File upload
                file = request.files['case_file']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        case_text = f.read()
            elif 'case_text' in request.form:
                # Direct text input
                case_text = request.form['case_text']
            elif request.is_json:
                # JSON payload
                case_text = request.json.get('case_text', '')
            
            if not case_text or not case_text.strip():
                return jsonify({"error": "No case text provided"}), 400
            
            # Parse parameters
            theta = float(request.form.get('theta', THETA_DEFAULT) or THETA_DEFAULT)
            llm_weight = float(request.form.get('llm_weight', LLM_WEIGHT_DEFAULT) or LLM_WEIGHT_DEFAULT)
            llm_model = request.form.get('llm_model', LLM_MODEL_NAME)
            enable_audio = request.form.get('enable_audio', 'false').lower() == 'true'
            
            # Constrain parameters
            theta = max(THETA_MIN, min(THETA_MAX, theta))
            llm_weight = max(0.0, min(1.0, llm_weight))
            
            # Parse document
            doc = DocumentParser.parse_text_document(case_text)
            if not doc:
                return jsonify({"error": "Failed to parse case document"}), 400
            
            # Generate unique case ID for this analysis session
            case_session_id = str(uuid.uuid4())[:8]
            
            # Analyze case
            result = analyze_case_document(
                doc,
                theta=theta,
                llm_weight=llm_weight if LANGCHAIN_AVAILABLE and llm_weight > 0 else 0.0,
                llm_model=llm_model,
                enable_audio=enable_audio and (COQUI_AVAILABLE or PYTTSX3_AVAILABLE),
                audio_output=os.path.join(AUDIO_FOLDER, f"verdict_{case_session_id}.wav") if enable_audio else None
            )
            
            # Build response
            verdicts_data = []
            for verdict in result['verdicts']:
                verdict_dict = {
                    "charge": verdict.charge,
                    "verdict": verdict.verdict,
                    "confidence": round(verdict.confidence * 100, 1),
                    "prosecution_score": round(verdict.prosecution_score, 3),
                    "defense_score": round(verdict.defense_score, 3),
                    "recommendation": verdict.recommendation,
                    "theta_threshold": verdict.theta_threshold
                }
                
                # Add LLM arguments if available
                if hasattr(verdict, 'llm_arguments'):
                    verdict_dict["llm_arguments"] = verdict.llm_arguments
                
                verdicts_data.append(verdict_dict)
            
            # Save report
            report_filename = f"report_{case_session_id}.txt"
            report_path = os.path.join(REPORTS_FOLDER, report_filename)
            result['report_generator'].save_report(report_path)
            
            # Build response
            response = {
                "success": True,
                "case_id": case_session_id,
                "case_number": doc.case_number,
                "verdicts": verdicts_data,
                "case_summary": result['case_summary'],
                "report_path": f"/download/report/{case_session_id}",
                "audio_path": f"/download/audio/{case_session_id}" if result.get('audio_file') else None,
                "llm_weight": llm_weight,
                "theta": theta,
                "timestamp": datetime.now().isoformat()
            }
            
            return jsonify(response), 200
        
        except Exception as e:
            return jsonify({"error": str(e), "success": False}), 500
    
    @app.route('/verdict/<case_id>')
    def verdict_page(case_id):
        """Display verdict page for a specific case"""
        try:
            # Load verdict data from analysis result
            # For now, render template that fetches via AJAX
            return render_template('verdict.html', case_id=case_id)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/download/report/<case_id>')
    def download_report(case_id):
        """Download text report"""
        try:
            report_path = os.path.join(REPORTS_FOLDER, f"report_{case_id}.txt")
            if not os.path.exists(report_path):
                return jsonify({"error": "Report not found"}), 404
            
            return send_file(report_path, as_attachment=True, 
                           download_name=f"verdict_{case_id}.txt")
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/download/audio/<case_id>')
    def download_audio(case_id):
        """Download audio verdict"""
        try:
            # Look for audio file (could be .wav or .mp3)
            for ext in ['.wav', '.mp3']:
                audio_path = os.path.join(AUDIO_FOLDER, f"verdict_{case_id}{ext}")
                if os.path.exists(audio_path):
                    return send_file(audio_path, as_attachment=True,
                                   download_name=f"verdict_{case_id}{ext}")
            
            return jsonify({"error": "Audio file not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/status')
    def api_status():
        """System status and capabilities"""
        return jsonify({
            "system": SYSTEM_NAME,
            "version": SYSTEM_VERSION,
            "llm_available": LANGCHAIN_AVAILABLE,
            "tts_available": COQUI_AVAILABLE or PYTTSX3_AVAILABLE,
            "tts_backend": "coqui" if COQUI_AVAILABLE else ("pyttsx3" if PYTTSX3_AVAILABLE else "none"),
            "timestamp": datetime.now().isoformat()
        }), 200
    
    @app.route('/api/config')
    def api_config():
        """Get system configuration"""
        return jsonify({
            "theta_default": THETA_DEFAULT,
            "theta_range": {"min": THETA_MIN, "max": THETA_MAX},
            "llm_weight_default": int(LLM_WEIGHT_DEFAULT * 100),
            "supported_charges": SUPPORTED_CHARGES,
            "max_upload_size_mb": MAX_UPLOAD_SIZE / (1024 * 1024)
        }), 200
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors"""
        return render_template('error.html', error=str(error)), 500
    
    return app

if __name__ == "__main__":
    app = create_app()
    print("\n" + "="*80)
    print(f"{SYSTEM_NAME}")
    print("="*80)
    print(f"\nWeb interface running at: http://localhost:{WEB_PORT}")
    print(f"\nLLM Defense Analysis: {'✓ Enabled' if LANGCHAIN_AVAILABLE else '✗ Disabled'}")
    print(f"TTS Audio Generation: {'✓ Enabled' if COQUI_AVAILABLE or PYTTSX3_AVAILABLE else '✗ Disabled'}")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host="127.0.0.1", port=WEB_PORT, debug=FLASK_DEBUG)
