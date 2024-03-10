.PHONY: init plan apply destroy test

init:
	terraform init

plan:
	terraform plan

apply:
	terraform apply -auto-approve

destroy:
	terraform destroy -auto-approve

test:
	python -m unittest discover tests

