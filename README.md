# k8s_project

## For database connection/set up

**Note: Ensure that docker is up and running before running any commands.**
\
\
Firstly, delete all instances of minikube in docker:
\
^ Make sures that there will not be any conflicts.
```
minikube delete
```
Then, start a minikube cluster:
```
minikube start
```
Run these to create database resources
```
kubectl apply -f db/configmap.yaml
kubectl apply -f db/pv.yaml
kubectl apply -f db/pvc.yaml
kubectl apply -f db/deployment.yaml
kubectl apply -f db/service.yaml
```
To ensure pods are running:
```
kubectl get pod
```
```
NAME                       READY   STATUS    RESTARTS   AGE
postgres-55869659f-kpsrp   1/1     Running   0          48s
postgres-55869659f-twlv9   1/1     Running   0          48s
postgres-55869659f-xzlp7   1/1     Running   0          48s
```
Port-forward the PostgresSQL service to the local machine
```
kubectl port-forward svc/postgres 5432:5432
```
### If successful,
You should see this in terminal which shows that it has been connected.
\
**Note: This terminal must be running in the background for the database connection to work.**
```
Forwarding from 127.0.0.1:5432 -> 5432
Forwarding from [::1]:5432 -> 5432
Handling connection for 5432
```

## For application

Firstly, install all required dependencies.
```
pip install -r requirements.txt
```
To upgrade PIP,
```
python.exe -m pip install --upgrade pip
```
To run app.py,
```
python ui/app.py
```