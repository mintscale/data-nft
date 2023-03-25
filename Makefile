ms:
	mkdir $@

init: ms
	python3 -m venv ms
	source ms/bin/activate && pip3 install -r requirements.txt

api:
	source ms/bin/activate && cd tools/api && uvicorn mintapi:app --reload
