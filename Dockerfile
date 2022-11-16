
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