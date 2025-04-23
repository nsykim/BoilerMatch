## HOW TO LAUNCH THE API

The API can be run by using one of the following methods from the command line, however, usage of the bash script (first option) is preferred:

- ```run build:be```
- ```python3 src/api.py```

Upon initialization of the API, a couple of operations will occur automatically:
- Connection to the MongoDB
- Connection to the Firebase Firestore
- Default hosting to port 3020

## HOW TO CONFIGURE THE API

### To change the port that the API is hosted on: 
1. Navigate to the final line in ```src/api.py```. 
2. Find the line: ```app.run(host="0.0.0.0", port=3020, debug=True)```. 
3. Replace 3020 with the desired port number. 


## PRE-REQUISITES TO RUN THE API

The API relies on a variety of different packages and environment variables. To download all of the required libraries, please run ```pip install reqs.txt``` from the command line.

Access to the MongoDB and Firebase Firestore are also required, with correct formatting of permissions within a ```.env``` file. For access, please contact one of the authors of the repository. 

## HOW TO USE THE API

There are two main ways to interact with the API.

1. CURL commands within command line interfact
2. Postman requests

It is recommended to use Postman for user convenience. By default, the API is hosted locally on a loopback server, meaning that, if the user is making API requests from the same network that is hosting the API, the address of the requests should be of the format: 
- ```http://localhost:PORT_NUMBER/REQUEST```

For a more robust method, please find the IPv4 address of the device that is hosting the API using:
- Windows: ```ipconfig```
- Linux/Unix: ```ip addr```

For request specific questions (formatting, return types, request types, etc), please navigate to ```src/api.py```, where documentation for each endpoint can be found. 