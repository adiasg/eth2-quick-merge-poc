set -e
set -x

IPYKERNEL_NAME=merge-spec-poc

python3 -m venv venv
. venv/bin/activate
pip install ipykernel wheel pytest
python3 -m ipykernel install --user --name=$IPYKERNEL_NAME

if [ ! -d "eth2.0-specs" ]; then
    git clone https://github.com/ethereum/eth2.0-specs.git
    cd ./eth2.0-specs; git checkout adiasg-quick-merge-poc; cd -
fi
pip install ./eth2.0-specs
pip install py-evm