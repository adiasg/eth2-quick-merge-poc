IPYKERNEL_NAME = merge-spec-poc

install: venv deps pyevm eth2spec thispackage ipykernel

venv:
	python3 -m venv venv

deps: venv
	. venv/bin/activate; pip install ipykernel wheel pytest

pyevm: venv
	. venv/bin/activate; pip install py-evm

eth2spec: venv
	git clone https://github.com/ethereum/eth2.0-specs.git; \
		cd ./eth2.0-specs; git checkout dev; cd -
	. venv/bin/activate; pip install ./eth2.0-specs

ipykernel:
	. venv/bin/activate; \
		python3 -m ipykernel install --user --name=$(IPYKERNEL_NAME)

thispackage:
	. venv/bin/activate; \
		pip install -e .

test:
	. venv/bin/activate; \
		pytest tests/

clean:
	rm -rf venv eth2.0-specs
	jupyter kernelspec remove $(IPYKERNEL_NAME)