# 307 Kubernetes + Docker project

## For Application set up

### **Before running any commands, please make sure that Docker Desktop is running!**
### **Also, run the following codes in Git Bash!**

## On the first inital run

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

## Step 1: Build the images required

***Please replace <docker_hub_username> with your dockerhub username***
\
***> Dockerhub username is the name of your account in Docker***
```
docker build -t <docker_hub_username>/ui:latest -f ui/Dockerfile . 
docker push <docker_hub_username>/ui:latest

docker build -t <docker_hub_username>/preprocess-image -f preprocessing/Dockerfile .
docker push <docker_hub_username>/preprocess-image

docker build -t <docker_hub_username>/training-model:latest -f training/Dockerfile . 
docker push <docker_hub_username>/training-model:latest

docker build -t <docker_hub_username>/inference-image:latest -f inference/Dockerfile . 
docker push <docker_hub_username>/inference-image:latest
```

## Step 2: Set up service and deploy the containers
**In Git Bash**, run this command to create the database and application resources:
```
./run.sh
```
^ **Unless the code is edited, this only needs to be run once.**


- If the code is edited, change the codes according to the yaml files:
```
kubectl rollout restart deployment/<deployment_file_name> 
```


## Step 3: Ensure all pods are running
To ensure pods are running, run this command:
```
kubectl get pod
```


Example of Output: It should show that all statuses are **Running**
```
NAME                       READY   STATUS    RESTARTS   AGE
postgres-55869659f-kpsrp   1/1     Running   0          48s
postgres-55869659f-twlv9   1/1     Running   0          48s
postgres-55869659f-xzlp7   1/1     Running   0          48s
```

## Step 4: Run kubernetes dashboard and expose database 
To run kubernetes dashboard: (**Use another terminal for proxy**)
```
kubectl proxy
```
**^ PLEASE LEAVE THIS TERMINAL RUNNING IN BACKGROUND!**

Port-forward the PostgresSQL service, database to the local machine:
```
kubectl port-forward svc/postgres 5432:5432
```
**^ PLEASE LEAVE THIS TERMINAL RUNNING IN BACKGROUND!**

-  If successful, you should see this in terminal which shows that it has been connected.


```
Forwarding from 127.0.0.1:5432 -> 5432
Forwarding from [::1]:5432 -> 5432
```
**Note: This terminal must be running in the background for the database connection to work!**


## Step 5: For database connection (Only on first run)
- Go to **Extensions** and download 
- **PostgreSQL by Chris Kolkman**
- **Database Client** by Database Client
-  On the left shortcut panel, go to **Database**
-  Press **Create Connection** and choose **PostgreSQL** as the server type.


## Step 6: Enter in the table information
```
Name: prediction
Group: db 
Host: localhost
Database: postgres
Username: wonwoo
Password: wonwoo
Port: 5432
```
- Once created, go to db > prediction > predictions_db > public > Query


## Step 7: Create table
- Click on **+** to create new query (any name) and enter the following:
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
- Then, click **Run** or **Ctrl + Enter**

- In the shortcut panel on the left, navigate to PostgreSQL Explorer and click on '**+**' to add connection.
- Save query for future runs (name it anything you want)


## Step 8: Connecting to Postgres
- Go to shortcut panel on the left
- Go to PostgresSQL Explorer and click the '+'
- Then, enter in the following when the pop up appears:
```
Hostname: localhost
PostgreSQL user: wonwoo
Password: wonwoo
Port number: 5432
SSL connection: Standard connection

Click 'Show All Databases'

Display name of connection: localhost
```

## Step 9: Get the secret token for the dashboard
To get the secret token for the dashboard, run this command:
```
kubectl -n kubernetes-dashboard create token admin-user

Output will be something like this: 
eyJhbGciOiJSUzI1NiIsImtpZCI6IkFEU1VsdUdxdnB4YjM2R1dTOFRieW95ZzFDME1rdGEwTkpzTGNtaHR6a1UifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhZG1pbi11c2VyIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImFkbWluLXVzZXIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiJhM2EyMjM3OS03Yjg5LTRhYzMtYTVkNC1kMzIzZDRhMzk0ZTUiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZXJuZXRlcy1kYXNoYm9hcmQ6YWRtaW4tdXNlciJ9.hLWdAu8CI2H5WB9-tG2PemD_RYWdIoc4_MvV3zP9USkuOsGnxsGQDNNAEo67Xj-4vLHNCpxwGCgWO-umvAE77uUIgWXu0-qxuO51Sw9pPe1NiqeV0Ed-8hAr_BN3QniOHElGLACqneIxHDS7XKpd7lyW88iWzMZOEpCW92QAQzQN-BroSgm3raTw0ix7xjLgqrmQV9PbAEyjZQxO3yb24FBN81C_DlXtRdwMznd8p3cKctkpEf6YGDQ1Sh6H6BhqVJ1MoFx20-_aLxhMMRFnRrDnv-yoGxPqg1PVHEeyGK2mpjeH9bQj8xkIDY4iJ-IC5-vU8FaBSlEbZgbX3BWFtgWFtg
``` 

## Step 10: Start application

Follow this steps to run application successfully: 

In another Terminal: 
```
minikube service ui-svc
```
**^ PLEASE LEAVE THIS TERMINAL RUNNING IN BACKGROUND!**

### Example output from terminal: 

![Alt text](data/display_readme.png)

**^ PLEASE LEAVE THIS TERMINAL RUNNING IN BACKGROUND!**

- **Click on the link that is boxed in RED!**

- **Hosting Url would change for every run**


# For future runs
**Before running any commands, please make sure that Docker Desktop is running!**
### Step 1: Set up service and deploy the containers
**In Git Bash**, run this command to create the database and application resources:
```
./run.sh
```


## Step 2: Ensure all pods are running
```
kubectl get pod
```
Example of Output: It should show that all statuses are **Running**
```
NAME                       READY   STATUS    RESTARTS   AGE
postgres-55869659f-kpsrp   1/1     Running   0          48s
postgres-55869659f-twlv9   1/1     Running   0          48s
postgres-55869659f-xzlp7   1/1     Running   0          48s
```


## Step 3: Database
- Go to the shortcut panel on the left, right click on 'db' and press **refresh**.
- Go to public > Query 
- Press on the query file that u have saved initially
- Click **Run** or Ctrl + Enter


## Step 4: Run kubernetes dashboard and expose database 
To run kubernetes dashboard: (Use another terminal for proxy)
```
kubectl proxy
```


Port-forward the PostgresSQL service, database to the local machine:
```
kubectl port-forward svc/postgres 5432:5432
```


-  If successful, you should see this in terminal which shows that it has been connected.


```
Forwarding from 127.0.0.1:5432 -> 5432
Forwarding from [::1]:5432 -> 5432
```
**Note: This terminal must be running in the background for the database connection to work.**

## Step 5: Get the secret token for the dashboard
To get the secret token for the dashboard, run this command:
```
kubectl -n kubernetes-dashboard create token admin-user

Output will be something like this: 
eyJhbGciOiJSUzI1NiIsImtpZCI6IkFEU1VsdUdxdnB4YjM2R1dTOFRieW95ZzFDME1rdGEwTkpzTGNtaHR6a1UifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhZG1pbi11c2VyIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImFkbWluLXVzZXIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiJhM2EyMjM3OS03Yjg5LTRhYzMtYTVkNC1kMzIzZDRhMzk0ZTUiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZXJuZXRlcy1kYXNoYm9hcmQ6YWRtaW4tdXNlciJ9.hLWdAu8CI2H5WB9-tG2PemD_RYWdIoc4_MvV3zP9USkuOsGnxsGQDNNAEo67Xj-4vLHNCpxwGCgWO-umvAE77uUIgWXu0-qxuO51Sw9pPe1NiqeV0Ed-8hAr_BN3QniOHElGLACqneIxHDS7XKpd7lyW88iWzMZOEpCW92QAQzQN-BroSgm3raTw0ix7xjLgqrmQV9PbAEyjZQxO3yb24FBN81C_DlXtRdwMznd8p3cKctkpEf6YGDQ1Sh6H6BhqVJ1MoFx20-_aLxhMMRFnRrDnv-yoGxPqg1PVHEeyGK2mpjeH9bQj8xkIDY4iJ-IC5-vU8FaBSlEbZgbX3BWFtgWFtg
``` 

## Step 6: Start application

Follow this steps to run application successfully: 

In another Terminal: 
```
minikube service ui-svc
```
**Ensure that the terminal is always running!**

# Troubleshooting

1. Docker is not running.
```
💣  Exiting due to PROVIDER_DOCKER_VERSION_EXIT_1: "docker version --format <no value>-<no value>:<no value>" exit status 1: error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.48/version": open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```
