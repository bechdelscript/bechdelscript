#!/bin/bash
fileid="16Ae_Dqz7RjFTXc7reiNvnHpXZ3jfkQhg"
filename="back_end/data/input/"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o ${filename}
rm ./cookie