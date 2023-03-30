#!/bin/bash
fileid="1u8tJT1nlmsQJQ0fA1OW0AUlCjfi9Bdzm"
filename="back_end/data/input/parsing_model.pth"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o ${filename}
rm ./cookie