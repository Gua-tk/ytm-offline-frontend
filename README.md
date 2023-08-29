# ytm-offline-frontend

```shell
python3 -m venv venv
venv/bin/python3 -m pip install --upgrade pip
venv/bin/python3 -m pip install -r requirements.txt
venv/bin/python3 src/main.py
```

## To build HTML in dist folder
```shell
flet publish src/FrontEnd.py --web-render html --assets assets
```

## Check test of dist folder so we can see changed favicon and splash screen
```shell
python3 -m http.server 5010 --directory src/dist
```