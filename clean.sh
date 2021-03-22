set -e
set -x
set -u

IPYKERNEL_NAME=merge-spec-poc

rm -rf venv eth2.0-specs
jupyter kernelspec remove $IPYKERNEL_NAME