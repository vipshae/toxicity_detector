from predictor import Predictor
import argparse, os, pickle
from flask import Flask, request, jsonify
from flask_cors import CORS

application = Flask(__name__)
CORS(application)
predictor = Predictor()

@application.route("/")
def index():
  return jsonify({"name": "model_server"})


@application.route('/predict', methods=['POST'])
def predict():
    try:
        json = request.get_json()
        model_version = json.get('version', 1)
        text = json.get('q')

        ## Make the request
        toxicity = predictor.predict_toxicity(text, model_version=model_version).outputs['outputs'].float_val
        return jsonify({
            "status": "ok",
            "text": text,
            "toxicity": str(toxicity[0])
            })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        })

if __name__ == "__main__":

  # argument parser from command line
  parser = argparse.ArgumentParser(add_help=True)

  # set of arguments to parse
  parser.add_argument(
      "--port", type=int, default=9001,
      help="port to run flask server")

  # debug or not
  parser.add_argument(
      "--dev", action='store_true',
      help='Run in debug mode')

  # host
  parser.add_argument(
      '--host', default="0.0.0.0",
      help='host to run flask server')

  # tensorflow server
  parser.add_argument(
      "--server", "-s",
      help='Server for tensorflow')

  # parse arguments
  args = parser.parse_args()

  # launch flask server accessible from all hosts
  application.run(debug=args.dev, port=args.port, host=args.host)


