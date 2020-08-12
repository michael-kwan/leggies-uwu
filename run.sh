FILE=./config.json
if ! test -f "$FILE"; then
    mv ./data/config.json ./config.json
fi
python3 legendary.py
