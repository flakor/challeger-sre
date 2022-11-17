# challeger-sre
Challenger SRE NeuralWorks
Desafío
Como SRE Engineer, tu desafío consiste en tomar el trabajo del equipo, exponerlo para que sea explotado por un
sistema:
# 1. Exponer el modelo serializado a través API REST.

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
 Los headers necesarios.
 ![alt text](https://github.com/flakor/challeger-sre/blob/master/blob/headers.jpg?raw=true)
 
 ## Prueba en localhost
 Iniciar servidor.
 
 ```console
 chkdsk@DESKTOP-7O6LBAG:~/challenge$ python3 server.py
 * Serving Flask app "server" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 143-070-844
  ```
  Pruebas con curl.
  ```console
  chkdsk@DESKTOP-7O6LBAG:~$ curl --location --request POST 'http://localhost:5000/api' --header 'Content-Type: application/json' --data-raw '{
    "array":[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0]
}'
{
  "predicciones": [
    1
  ]
}
 ```
 Pruebas postman.
 
 ![alt text](https://github.com/flakor/challeger-sre/blob/master/blob/postman.jpg?raw=true)
 
 
# 2. Automatizar el proceso de construcción y despliegue de la API, utilizando uno o varios servicios cloud.

Para automatizar lo primero que se debe realizar es dockerificar la app

 ```yaml
 # Base de sistemas en el cual se carga el script
FROM python:3.8-slim-buster
# indica el directorio de trabajo
WORKDIR /challenge
#copia el archivo de dependencias
COPY requirements.txt requirements.txt
#instala las dependecias
RUN pip3 install -r requirements.txt
#copia los archivos locales en el docker.
COPY . . 
# Ejecuta python server.py

CMD [ "python" , "server.py" ]

# Exponer el puerto 5000 de la api
EXPOSE 5000
 
  ```
 Con este proceso la app "se empaqueta en un contenedor" que es compatible con cualquier sistema que pueda ejecutar docker.
 
 El siguiente paso es hacer en build y tagiar la app.
 Ademas voy a subir la imagen a dockerhub para utilizar esta para el proceso de kubernetes.
 lo comandos son:
 ```console
 sudo docker build --tag=sre-challenge .
 docker tag sre-challenge flakor/challenger:v1
 docker push flakor/challenger:v1
 ```
 Tener en consideracion las variables de entorno para docker login ademas de crear el repositorio antes de este proceso.
 ```console
 DOCKER_REGISTRY_SERVER=docker.io
 DOCKER_USER=pepe
 DOCKER_EMAIL=prueba@gmail.com
 DOCKER_PASSWORD=1234
 ```
 
 Para el despliege de la app se utilizara Google cloud platform con los siguientes servicios .
 
 Google Cloud Run.
 
 Google Kubernetes Engine GKE.
 
 Para esto es importante los siguientes permisos en la cuenta de servicio que se genere para app.
 
 ![alt text](https://github.com/flakor/challeger-sre/blob/master/blob/permisos-gcp.jpg?raw=true)
 
 Para el CD se utilizara github actions 
 
 GitHub -> Github Actions -> Google Build -> Google Cloud Run
 
 los comandos para google cloud run.
 ```console
 gcloud auth login
 
 gcloud builds submit --tag gcr.io/sre-challenger/sre-challenge-gc --project=sre-challenger
 
 
chkdsk@DESKTOP-7O6LBAG:~/challenge$ gcloud run deploy sre-challenge-gc --image gcr.io/sre-challenger/sre-challenge-gc --platform managed --port=5000 --project=sre-challenger --allow-unauthenticated --region us-central1
Deploying container to Cloud Run service [sre-challenge-gc] in project [sre-challenger] region [us-central1]
✓ Deploying... Done.
  ✓ Creating Revision...
  ✓ Routing traffic...
  ✓ Setting IAM Policy...
Done.
Service [sre-challenge-gc] revision [sre-challenge-gc-00003-fup] has been deployed and is serving 100 percent of traffic.
Service URL: https://sre-challenge-gc-shkwh5tmnq-uc.a.run.app
chkdsk@DESKTOP-7O6LBAG:~/challenge$

```
Esta es la url de la app publicada https://sre-challenge-gc-shkwh5tmnq-uc.a.run.app 


## Github actions.

primer paso es crear los secretos en github actions 

GCP_PROJECT_ID

GCP_SA_KEY_JSON

Luego crear el archivo deploy.yml en el directorio workflow de github.
```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloud Run

on:
  push:
    branches:
      - master

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  APP_ID: sre-challenge-gc
  RUN_REGION: us-central1
  SA_KEY_JSON: ${{ secrets.GCP_SA_KEY_JSON }}

jobs:
  deploy:
    name: Deploy a Cloud Run
    runs-on: ubuntu-latest
    if: "contains(github.event.head_commit.message, 'to deploy')"
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - id: 'auth'
        name: 'Authenticate to Google Cloud'
        uses: 'google-github-actions/auth@v0'
        with:
          credentials_json: '${{ secrets.GCP_SA_KEY_JSON }}'
      
      # Setup gcloud CLI
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v0

      - name: Authorize Docker push
        run: gcloud auth configure-docker
     
      # Build and push image to Google Container Registry
      - name: Build
        run: gcloud builds submit --tag gcr.io/$PROJECT_ID/$APP_ID:$GITHUB_SHA

      - name: Deploy
        run: gcloud run deploy $APP_ID --image gcr.io/$PROJECT_ID/$APP_ID:$GITHUB_SHA --platform managed --port=5000 --region $RUN_REGION --allow-unauthenticated


```

Se lanzara la actions solo cuando los commit contengan el mensaje "to deploy".




  
  
 
 
 
  

# 3. Hacer pruebas de estrés a la API con el modelo expuesto con al menos 50.000 requests durante 45
segundos. Para esto debes utilizar esta herramienta y presentar las métricas obtenidas.

Instalar wrk
```console
git clone https://github.com/wg/wrk.git
```
editar en la carpeta script
```console
nano post.lua

chkdsk@DESKTOP-7O6LBAG:~/wrk/scripts$ cat post.lua
-- example HTTP POST script which demonstrates setting the
-- HTTP method, body, and adding a header

wrk.method = "POST"
wrk.body   = '{"testarray":[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0]}'
wrk.headers["Content-Type"] = "application/json"
chkdsk@DESKTOP-7O6LBAG:~/wrk/scripts$
```
luego compilar con make
ejecutar 
```console
 ./wrk -t10 -c400 -d45s -s post.lua https://sre-challenge-gc-shkwh5tmnq-uc.a.run.app/api
``` 
 resultados.
 
 ![alt text](https://github.com/flakor/challeger-sre/blob/master/blob/wrk-sre.jpg?raw=true)
 




## a. ¿Cómo podrías mejorar el performance de las pruebas anteriores?

A nivel de hardware se tiene la posibilidad de crecimiento vertical y horizontal.

Que son aumento de ram y procesador en el crecimiento vertial o crear nuevas instancias en paralelo en el crecimiento horizontal.

A nivel de software se podria utilizar otro lenguaje de programacion como es lua. o generar un binario de la app.



# 4. El proceso de creación de infraestructura debe ser realizado con Terraform.

Se desplegara un cluster de kubernetes mediante terraform.

Archivos terraform necesarios.

main.tf
```yaml
provider "google" {
  credentials = file("sre-challenger-deaf1565b69c.json")
}

module "gke_auth" {
  source       = "terraform-google-modules/kubernetes-engine/google//modules/auth"
  depends_on   = [module.gke]
  project_id   = var.project_id
  location     = module.gke.location
  cluster_name = module.gke.name
}

resource "local_file" "kubeconfig" {
  content  = module.gke_auth.kubeconfig_raw
  filename = "kubeconfig-${var.env_name}"
}



module "gcp-network" {
  source       = "terraform-google-modules/network/google"
  project_id   = var.project_id
  network_name = "${var.network}-${var.env_name}"
  subnets = [
    {
      subnet_name   = "${var.subnetwork}-${var.env_name}"
      subnet_ip     = "10.10.0.0/16"
      subnet_region = var.region
    },
  ]
  secondary_ranges = {
    "${var.subnetwork}-${var.env_name}" = [
      {
        range_name    = var.ip_range_pods_name
        ip_cidr_range = "10.20.0.0/16"
      },
      {
        range_name    = var.ip_range_services_name
        ip_cidr_range = "10.30.0.0/16"
      },
    ]
  }
}

module "gke" {
  source            = "terraform-google-modules/kubernetes-engine/google//modules/private-cluster"
  project_id        = var.project_id
  name              = "${var.cluster_name}-${var.env_name}"
  regional          = false
  region            = var.region
  zones             = ["us-central1-c"]
  network           = module.gcp-network.network_name
  subnetwork        = module.gcp-network.subnets_names[0]
  ip_range_pods     = var.ip_range_pods_name
  ip_range_services = var.ip_range_services_name
  node_pools = [
    {
      name           = "node-pool"
      machine_type   = "n2-standard-2"
      node_locations = "us-central1-c"
      min_count      = var.minnode
      max_count      = var.maxnode
      disk_size_gb   = var.disksize
      preemptible    = false
      auto_repair    = false
      auto_upgrade   = true
    },
  ]
}
output "cluster_name" {
  description = "Cluster name"
  value       = module.gke.name
}
```
variables.tf
```yaml
variable "project_id" {
  description = "The project ID of your project"
  default = "sre-challenger"
}
variable "cluster_name" {
  description = "The name for the GKE cluster"
  default     = "gke-terraform-sre"
}
variable "env_name" {
  description = "The environment for the GKE cluster"
  default     = "challenger"
}
variable "region" {
  description = "The region to host the cluster in"
  default     = "us-central1"
}
variable "zones" {
  description = "Cluster zone"
  default     = "us-central1-c"
}
variable "network" {
  description = "The VPC network created to host the cluster in"
  default     = "gke-network"
}
variable "subnetwork" {
  description = "The subnetwork created to host the cluster in"
  default     = "gke-subnet"
}
variable "ip_range_pods_name" {
  description = "The secondary ip range to use for pods"
  default     = "ip-range-pods"
}
variable "ip_range_services_name" {
  description = "The secondary ip range to use for services"
  default     = "ip-range-services"
}

variable "service-account-id" {
  description = "The ID of service account of GCP"
  default     = "sre-challenger@sre-challenger.iam.gserviceaccount.com"
}


variable "cpus" {
  description = "Number of cpus"
  default     = "2"
}

variable "minnode" {
  description = "Minimum number of node pool"
  default     = 3
}
variable "maxnode" {
  description = "Maximum number of node pool"
  default     = 3
}

variable "disksize" {
  description = "Disk Size in GB"
  default     = 10
}
```
Comandos para ejecutar la configuracion propuesta.
```console
terraform init
terraform plan
terraform apply
```
Cluster funcioando en GCP
 ![alt text](https://github.com/flakor/challeger-sre/blob/master/blob/GKE.jpg?raw=true)
 
 El siguiente paso es desplegar el cluster de kubernetes para esto se necesita crear un archivo de deployment, servicios y crear un secreto para traer la imagen de app publicada en dockerhub.
 
 Comando para el secreto.
 ```console
 kubectl create secret docker-registry myregistrykey   --docker-server=$DOCKER_REGISTRY_SERVER   --docker-username=$DOCKER_USER   --docker-password=$DOCKER_PASSWORD   --docker-email=$DOCKER_EMAIL
 ```
 Archivo deployment
 ```yml
 apiVersion: apps/v1
kind: Deployment
metadata:
  name: sre-challenge-gc
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sre-challenge-gc
  template:
    metadata:
      labels:
        app: sre-challenge-gc
    spec:
      containers:
      - name: sre-challenge
        image: flakor/challenger:v1  
        resources:
          requests:
            memory: "1024Mi"
            cpu: "1000m"
          limits:
            memory: "1024Mi"
            cpu: "1000m"
        ports:
        - containerPort: 5000
        env:
          - name: PORT
            value: "5000"
      imagePullSecrets:
      - name: gcr
```
archivo de servicio.
```yml
apiVersion: v1
kind: Service
metadata:
  name: sre-challenge-gc
  labels:
    app: sre-challenge-gc
spec:
  ports:
  - name: 5000-5000
    port: 80
    protocol: TCP
    targetPort: 5000
  selector:
    app: sre-challenge-gc
  type: LoadBalancer
  # Replace the value with the IP address you reserved
  loadBalancerIP: 34.136.109.140
```



 



# 5. ¿Cuáles serían los mecanismos ideales para que sólo sistemas autorizados puedan acceder a esta API?
(NO es necesario implementarlo).

Basic Authentication, API Key, OAuth 2.0.


## a. ¿Este mecanismo agrega algún nivel de latencia al consumidor? ¿Por qué?
Toda solucion de autoriacion de usuario agrega una latencia ya que es una capa intermedia en la app y el usuario ademas por la naturaleza de los sistemas de autorizacion se agregar funciones criptograficas los cuales tienen diferentes tipos de robustes y por lo tanto la latencia asociada.

## 6. ¿Cuáles serían los SLIs y SLOs que deﬁnirías y por qué?.

Como SLI se podria medir el tiempo de respuesta de la API.

Como SLO podria ser que el tiempo de latencia que no sea menor que de las pruebas en local.



