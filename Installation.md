# Installation de Excalibur

`git clone https://github.com/Joytide/Excalibur.git`

Se placer dans le dossier Excalibur (là où il y a le Dockerfile)

`docker build -t excalibur .` pour créer l'image docker

`docker run -ti excalibur` pour lancer le conteneur et rentrer dedans

`exit` pour sortir du conteneur

`docker exec -ti [id] bash` pour re rentrer dans le conteneur

`docker stop [id]` pour arrêter le conteneur