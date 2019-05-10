from flask import Flask, jsonify, request
import logging
from logging.handlers import RotatingFileHandler
import web_app_logic as wal
import apps_logger as apl


def Logger():
    return logging.getLogger('web_app_logger')


def create_app():
    app_ct = Flask(__name__)
    return app_ct

app = create_app()


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    """
    No need to reveal too much about the failure.
    In debug mode or for developers we would return more details.
    """
    status_code = 500
    response = {
        'success': False,
        'error': 'An unexpected error has occurred.'
    }
    return jsonify(response), status_code


@app.route("/")
def index():
    return jsonify(success=True)


@app.route('/photos/pending', methods=['GET'])
def pending_photos():
    """
    Endpoint that returns a list of photos in 'pending' status
    """
    return jsonify(wal.get_pending_photo())


@app.route('/photos/process', methods=['POST'])
def process_photos_request():
    """
    Expects JSON data: {"data":["uuid","uuid",...]}
    Endpoint that submits each uuid to the 'photo_processor' task queue
    """
    return jsonify(wal.submit_photo_for_processing(request.json['data']))


if __name__ == '__main__':
    apl.configure_logger(Logger())
    app.run(host='0.0.0.0', port=3000)
