
from flask import Flask, request, jsonify
import numpy as np
import pickle
import json

app = Flask(__name__)



models_path = 'pickle_model.pkl'
#carga el modelo
# Endpoint
@app.route('/api', methods=['POST'])

def predecir():
    content = request.get_json()
    x_data = np.asarray(content['array']).reshape(1, -1)
    print(json.dumps(content))
    loaded_model = pickle.load(open(models_path, 'rb'))
    result = loaded_model.predict(x_data)
    return jsonify({'predicciones' : result.tolist()})
   
if __name__ == '__main__':
   
    app.run(port=5000, debug=True, host='0.0.0.0')