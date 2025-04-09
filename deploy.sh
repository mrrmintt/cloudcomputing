#!/bin/bash

# Exit on any error
set -e

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "Terraform could not be found. Please install it."
    exit 1
fi

# Check if ansible is installed
if ! command -v ansible &> /dev/null; then
    echo "Ansible could not be found. Please install it."
    exit 1
fi

# Variables
LOCATION=${1:-"westeurope"}
PREFIX=${2:-"imgtag"}

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Create infrastructure with Terraform
echo "Creating infrastructure with Terraform..."
terraform apply -auto-approve -var "location=$LOCATION" -var "prefix=$PREFIX"

# Get outputs from Terraform
VM_IP=$(terraform output -raw vm_public_ip)
COSMOS_ENDPOINT=$(terraform output -raw cosmos_db_endpoint)
COSMOS_KEY=$(terraform output -raw cosmos_db_key)

# Wait for VM to be ready
echo "Waiting for VM to be ready..."
sleep 60

# Update inventory with VM IP
sed -i "s/VM_IP_ADDRESS/$VM_IP/g" inventory.ini

# Get Azure Computer Vision credentials
read -p "Enter Azure Computer Vision API Key: " CV_KEY
read -p "Enter Azure Computer Vision Endpoint: " CV_ENDPOINT

# Deploy with Ansible
echo "Deploying application with Ansible..."
ansible-playbook -i inventory.ini playbook.yml \
  --extra-vars "computer_vision_key=$CV_KEY" \
  --extra-vars "computer_vision_endpoint=$CV_ENDPOINT" \
  --extra-vars "cosmos_db_endpoint=$COSMOS_ENDPOINT" \
  --extra-vars "cosmos_db_key=$COSMOS_KEY" \
  --extra-vars "use_nginx=true"

echo ""
echo "Deployment completed successfully!"
echo "Application is available at: http://$VM_IP"