# praktikum_new_diplom

сбилдить backend
dockeimage build -t backend-image --file backend/Dockerfile .

запустить контейнер backend
docker run --rm --name backend -p 7000:8000 --network foodNET backend-image

запустить контейнер nginx
docker container run --rm --name gateway -v foodgram-volume:/staticfiles/ --network foodNET -p 80:80 gateway