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

Build the image:
```
docker build -t wldkdnps/ui:latest ./ui
docker push wldkdnps/ui:latest
```

Run these to create database resources:
```
kubectl apply -f db/pv.yaml
kubectl apply -f db/pvc.yaml
kubectl apply -f db/configmap.yaml
kubectl apply -f db/deployment.yaml
kubectl apply -f db/service.yaml

kubectl apply -f ui/deployment.yaml

kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

kubectl apply -f dashboard/dashboard-adminuser.yaml -n kubernetes-dashboard
kubectl apply -f dashboard/dashboard-clusterrole.yaml -n kubernetes-dashboard
kubectl apply -f dashboard/dashboard-secret.yaml -n kubernetes-dashboard
```
^ **Unless the code is edited, this only needs to be run once.**

To get the secret token:
```
kubectl get secret admin-user -n kubernetes-dashboard -o jsonpath={".data.token"} | base64 -d

eyJhbGciOiJSUzI1NiIsImtpZCI6IkFEU1VsdUdxdnB4YjM2R1dTOFRieW95ZzFDME1rdGEwTkpzTGNtaHR6a1UifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhZG1pbi11c2VyIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImFkbWluLXVzZXIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiJhM2EyMjM3OS03Yjg5LTRhYzMtYTVkNC1kMzIzZDRhMzk0ZTUiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZXJuZXRlcy1kYXNoYm9hcmQ6YWRtaW4tdXNlciJ9.hLWdAu8CI2H5WB9-tG2PemD_RYWdIoc4_MvV3zP9USkuOsGnxsGQDNNAEo67Xj-4vLHNCpxwGCgWO-umvAE77uUIgWXu0-qxuO51Sw9pPe1NiqeV0Ed-8hAr_BN3QniOHElGLACqneIxHDS7XKpd7lyW88iWzMZOEpCW92QAQzQN-BroSgm3raTw0ix7xjLgqrmQV9PbAEyjZQxO3yb24FBN81C_DlXtRdwMznd8p3cKctkpEf6YGDQ1Sh6H6BhqVJ1MoFx20-_aLxhMMRFnRrDnv-yoGxPqg1PVHEeyGK2mpjeH9bQj8xkIDY4iJ-IC5-vU8FaBSlEbZgbX3BWFtgWFtg
```
To run kubernetes dashboard:
```
kubectl proxy
```

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
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  feedback TEXT
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

## Application will be hosted on: http://127.0.0.1:5000/

Build the image for Preprocessing: 
```
docker build -t <docker_hub_username>/preprocessing-img -f preprocessing/Dockerfile .
docker push <docker_hub_username>/preprocessing-image
```
Run these to create the preprocessing resources 
```
kubectl apply -f preprocessing/deployment.yaml
kubectl apply -f preprocessing/service.yaml
```

port-forwarding:
```
kubectl port-forward svc/preprocess-svc 5001:5001
```

# Troubleshooting

1. Docker is not running.
```
💣  Exiting due to PROVIDER_DOCKER_VERSION_EXIT_1: "docker version --format <no value>-<no value>:<no value>" exit status 1: error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.48/version": open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```
