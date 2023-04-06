#!/bin/bash
fileid="1FfQDJRqHQsQPxw-lWUw_4ja30lWHbbSD"
filename="back_end/data/input/scripts_kaggle.zip"
destination_folder="back_end/data/input/"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o ${filename}
rm ./cookie
unzip ${filename} -d ${destination_folder}
rm ${filename}