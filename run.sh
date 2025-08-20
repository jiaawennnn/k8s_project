# stops if any command fails
#!/bin/bash

# This script sets up a Kubernetes environment with Minikube and deploys various services.
# It applies Persistent Volumes, ConfigMaps, and deployments for Postgres, UI, Preprocessing, Training, and Inference services.
set -e  

echo "Applying Persistent Volumes and Claims..."
kubectl apply -f db/pv.yaml
kubectl apply -f db/pvc.yaml
kubectl apply -f inference/model-pv-pvc.yaml
echo " "

echo "Applying ConfigMaps..."
kubectl apply -f db/configmap.yaml
echo " "

echo "Deploying Postgres service..."
kubectl apply -f db/deployment.yaml
kubectl apply -f db/service.yaml
echo " "

echo "Deploying UI service..."
kubectl apply -f ui/deployment.yaml
kubectl apply -f ui/service-ui.yaml
kubectl apply -f ui/hpa.yaml
echo " "

echo "Deploying Preprocessing service..."
kubectl apply -f preprocessing/deployment.yaml
kubectl apply -f preprocessing/service.yaml 
kubectl apply -f preprocessing/hpa.yaml
echo " "

# Wait until the helper pod is running
# echo "Creating helper pod to mount the model"
# kubectl apply -f inference/model-pod.yaml

# # Copy model into PVC
# echo "Copying model into PVC..."
# kubectl cp data/saved_model/final_model.h5 model-uploader:/mnt/models/final_model.h5

echo "Model successfully uploaded to PVC!"
echo " "

echo "Deploying Inference service..."
kubectl apply -f inference/deployment.yaml
kubectl apply -f inference/service.yaml 
kubectl apply -f inference/hpa.yaml
echo " "

echo "Deploying Kubernetes Dashboard..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
kubectl apply -f dashboard/dashboard-adminuser.yaml -n kubernetes-dashboard
kubectl apply -f dashboard/dashboard-clusterrole.yaml -n kubernetes-dashboard
echo " "

echo "All deployments have been applied!"
echo "Please wait a few moments for pods to start, then run: "
echo " "
echo "↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓"
echo "                   kubectl get pods                   "
echo "↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑"
echo " "
echo "to check status of pods."