# challeger-sre
Challenger SRE NeuralWorks
Desafío
Como SRE Engineer, tu desafío consiste en tomar el trabajo del equipo, exponerlo para que sea explotado por un
sistema:
1. Exponer el modelo serializado a través API REST.

Se utilizara el framework flask ya que es mas simple para trabajar con api-rest en python.

```python
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
```
a. Puedes usar el modelo ya serializado (pickle_model.pkl) o volver a generarlo.
```python
models_path = 'pickle_model.pkl'
#carga el modelo
```

 El endpoint que por request del tipo POST recibe un vector
 con el siguiente formato.
 ```json
 
 {
    "array":[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0,0]
}
 ```
 ![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)
2. Automatizar el proceso de construcción y despliegue de la API, utilizando uno o varios servicios cloud.
3. Hacer pruebas de estrés a la API con el modelo expuesto con al menos 50.000 requests durante 45
segundos. Para esto debes utilizar esta herramienta y presentar las métricas obtenidas.
a. ¿Cómo podrías mejorar el performance de las pruebas anteriores?
4. El proceso de creación de infraestructura debe ser realizado con Terraform.
5. ¿Cuáles serían los mecanismos ideales para que sólo sistemas autorizados puedan acceder a esta API?
(NO es necesario implementarlo).
a. ¿Este mecanismo agrega algún nivel de latencia al consumidor? ¿Por qué?
6. ¿Cuáles serían los SLIs y SLOs que deﬁnirías y por qué?
Consideraciones
● Documentar MUY bien tu trabajo. Recomendamos utilizar un README o markdown donde puedas
contar y dar a entender tus decisiones y supuestos. Recuerda que no estamos en tu cabeza!
●      Criterios a considerar:
○ Creatividad en las técnicas y/o herramientas utilizadas.
○ Simplicidad y eﬁciencia.
○ Performance.
○ Calidad de conclusiones.
○ Orden y documentación.
