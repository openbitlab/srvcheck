install:
	pip install .
	
test:
	tox 

coverage:
	coverage run -m pytest 
	coverage report -m