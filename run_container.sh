docker run -it -d \
    --name wdps-group-19 \
    -v ./group-19:/home/user/code \
    -v ./requirements.txt:/home/user/requirements.txt \
    -v ./input_and_output:/home/user/input_and_output \
    karmaresearch/wdps2

docker exec -it wdps-group-19 pip install --prefer-binary  -r /home/user/requirements.txt

docker exec -it wdps-group-19 python3 -m spacy download en_core_web_sm