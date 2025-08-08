# k8s_project

## For database set up

**Note: Ensure that docker is up and running before running any commands.**
\
\
**On first run**, delete all instances of minikube in docker:
- Make sures that there will not be any conflicts.
- **From second run onwards**, skip running 'minikube delete'.
```
minikube delete
```
Then, start a minikube cluster:
```
minikube start
```
Run these to create database resources:
```
kubectl apply -f db/configmap.yaml
kubectl apply -f db/pv.yaml
kubectl apply -f db/pvc.yaml
kubectl apply -f db/deployment.yaml
kubectl apply -f db/service.yaml
```
^ **Unless the code is edited, this only needs to be run once.**

To ensure pods are running:
```
kubectl get pod
```
Output should show that all statuses are **Running**:
```
NAME                       READY   STATUS    RESTARTS   AGE
postgres-55869659f-kpsrp   1/1     Running   0          48s
postgres-55869659f-twlv9   1/1     Running   0          48s
postgres-55869659f-xzlp7   1/1     Running   0          48s
```
Port-forward the PostgresSQL service to the local machine:
```
kubectl port-forward svc/postgres 5432:5432
```
## If successful, 
You should see this in terminal which shows that it has been connected.
\
\
**Note: This terminal must be running in the background for the database connection to work.**
```
Forwarding from 127.0.0.1:5432 -> 5432
Forwarding from [::1]:5432 -> 5432
Handling connection for 5432
```

## For database connection (Only on first run)

1. Go to **Extensions** and download 
- **PostgreSQL by Chris Kolkman**
- **Database Client** by Database Client
2. On the left shortcut panel, go to **Database**
3. Press **Create Connection** and choose **PostgreSQL** as the server type.
4. Enter in the following information:
```
Name: prediction
Group: db 
Host: localhost
Database: postgres
Username: wonwoo
Password: wonwoo
Port 5432
```
5. Once created, go to db > prediction > predictions_db > Query 
6. Click on **+** to create new query (any name) and enter the following:
```
CREATE TABLE IF NOT EXISTS prediction_history (
  id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  filename TEXT,
  image_bytes BYTEA NOT NULL,
  label TEXT,
  confidence FLOAT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
```
Then, click **Run** or **Ctrl + Enter**
\
\
7. In the shortcut panel on the left, navigate to PostgreSQL Explorer and click on '**+**' to add connection.
\
8. Enter the following
```
Hostname: localhost
PostgreSQL user: wonwoo
Password: wonwoo
Port number: 5432
SSL connection: Standard connection

Click 'Show All Databases'

Display name of connection: localhost
```

## For application

Firstly, install all required dependencies.
```
pip install -r ui/requirements.txt 
# use ui/requirements.txt for now
```
To upgrade PIP,
```
python.exe -m pip install --upgrade pip
```
To run app.py,
```
python ui/app.py
```

#### Application will be hosted on: http://127.0.0.1:5000/


# Troubleshooting

1. Docker is not running.
```
💣  Exiting due to PROVIDER_DOCKER_VERSION_EXIT_1: "docker version --format <no value>-<no value>:<no value>" exit status 1: error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.48/version": open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```
