from flask import Flask, request, jsonify, send_from_directory
from pydantic import BaseModel
import sys
import re
from io import StringIO
import contextlib
import os
from urllib.request import urlopen
import json
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import traceback
from werkzeug.middleware.proxy_fix import ProxyFix
from asgiref.wsgi import WsgiToAsgi

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flask_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add common imports to the global namespace for code execution
try:
    globals().update({
        'urlopen': urlopen,
        'json': json,
        'requests': requests,
        'pd': pd,
        'np': np,
        'plt': plt
    })
except Exception as e:
    logger.error(f"Error importing common modules: {str(e)}")
    logger.error(traceback.format_exc())

app = Flask(__name__)
# Handle proxy headers if behind a reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Create ASGI app
asgi_app = WsgiToAsgi(app)

# Serve static files
@app.route('/static/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('static', path)
    except Exception as e:
        logger.error(f"Error serving static file {path}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "File not found"}), 404

class CodeRequest(BaseModel):
    code: str

@contextlib.contextmanager
def capture_output():
    """Capture stdout and stderr"""
    stdout, stderr = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = stdout, stderr
        yield stdout, stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

@app.route('/execute', methods=['POST'])
def execute_code():
    try:
        if not request.is_json:
            logger.error("Request is not JSON")
            return jsonify({
                "output": "",
                "error": "Request must be JSON",
                "status": "error"
            }), 400

        data = request.get_json()
        if not data or 'code' not in data:
            logger.error("No code provided in request")
            return jsonify({
                "output": "",
                "error": "No code provided",
                "status": "error"
            }), 400

        logger.info("Executing code")
        with capture_output() as (stdout, stderr):
            matches = re.findall(r"```python(.*?)```", data['code'], re.DOTALL)
            if matches:
                if matches[0] == "":
                    code_to_execute = data['code'].strip()
                else:
                    code_to_execute = matches[0].strip()
            else:
                code_to_execute = data['code'].strip()
            
            # Create a new dictionary for the execution environment
            exec_globals = globals().copy()
            exec(code_to_execute, exec_globals)

        output = stdout.getvalue()
        error = stderr.getvalue()
        
        if error:
            logger.warning(f"Code execution produced stderr: {error}")
        
        return jsonify({
            "output": output,
            "error": error,
            "status": "success"
        })

    except Exception as e:
        error_msg = f"Error executing code: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return jsonify({
            "output": "",
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/tracedata', methods=['GET'])
def get_trace_data():
    try:
        return jsonify({"url": "/static/TraceData.json"})
    except Exception as e:
        logger.error(f"Error in get_trace_data: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {str(error)}")
    logger.error(traceback.format_exc())
    return jsonify({
        "error": "Internal server error",
        "details": str(error) if app.debug else "An unexpected error occurred"
    }), 500

if __name__ == '__main__':
    # Check if required directories exist
    if not os.path.exists('static'):
        os.makedirs('static')
        logger.info("Created static directory")
    
    # Check if required packages are installed
    required_packages = ['flask', 'requests', 'pandas', 'numpy', 'matplotlib', 'asgiref', 'uvicorn']
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install missing packages using: pip install " + " ".join(missing_packages))
        sys.exit(1)
    
    # Run the app
    import uvicorn
    
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting server on {host}:{port} (debug={debug})")
    
    # Use uvicorn to run the ASGI app
    # uvicorn.run(
    #     "main2:asgi_app",
    #     host=host,
    #     port=port,
    #     reload=debug,
    #     log_level="info"
    # )
