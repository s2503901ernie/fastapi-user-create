# fastapi-user-create

## Introduction

This simple FastAPI server provides two APIs to play around:
1. Create a user
2. Verify a user

The detailed API spec please check the below session.

## Prerequisites 
1. Clone this repository to your local machine.
2. Pull the image to your local machine:
```bash

# Pull the docker image
$ docker pull hunghsianghuang/my-fastapi:1.0.0

# Check image is available
$ docker images
REPOSITORY                   TAG       IMAGE ID       CREATED          SIZE
hunghsianghuang/my-fastapi   1.0.0     ad01832936b0   27 minutes ago   226MB
```
Once you have the repository and the docker, you could start to launch the service.

>>>NOTICE<<<
> Please ensure that your platform is compatible with the Linux/amd64 OS and architecture before utilizing the image.

## Launch 

1. Please navigate to the repository
```bash
# Navigate to the repo
$ cd fastapi-user-create

# Navigate to the dev directory
$ cd dev
```
2. Launch the container

There is a file `docker-compose.yaml` in the dev folder.
```bash
# Launch the container
$ docker-compose up -d 

# Check the service is running
$ docker ps
CONTAINER ID   IMAGE                              COMMAND                  CREATED          STATUS          PORTS                    NAMES
86ca0f49f87c   hunghsianghuang/my-fastapi:1.0.0   "uvicorn main:app --…"   33 minutes ago   Up 10 seconds   0.0.0.0:8080->8080/tcp   my-fastapi
```
You should see a service running. The address is `localhost:8080` or `127.0.0.1:8080`.

## API specs

### Create User

**Endpoint:**
> POST users/create_user/

**Description**

Create a new user.

**Example Request**

> URL: http://127.0.0.1:8080/users/create_user
```json
{
    "username": "Jason",
    "password": "Jason1234"
}
```
**Responses**

**201** Created: Successfully created.  
```json
{
  "success": true,
  "reason": ""
}
```

**400** Bad Request: Invalid request format. 
1. Username less than three characters
```json
{
  "success": false,
  "reason": "The length of the user name is too short, should be at least 3 characters."
}
```
2. Username is larger than 32 characters
```json
{
  "success": false,
  "reason": "The length of the user name is too long, should be at most 32 characters."
}
```
3. Password is too short
```json
{
  "success": false,
  "reason": "The length of the password is too short, should be at least 8 characters."
}
```
4. Password is too long
```json
{
  "success": false,
  "reason": "The length of the password is too long, should be at most 32 characters."
}
```
5. Password should have at least one uppercase
```json
{
  "success": false,
  "reason": "The uppercase is missing, should be at least one."
}
```
6. Password should have at least one lowercase
```json
{
  "success": false,
  "reason": "The lowercase is missing, should be at least one."
}
```
7. Password should have a least one digit
```json
{
  "success": false,
  "reason": "The number is missing, should be at least one."
}
```
**409** Conflict: Duplicated username.  
```json
{
  "success": false,
  "reason": "The username: [Jason] has been created already, please change another one."
}
```

**Notes**
> IP address: localhost  
> Port: 8080

### Verify user

**Endpoint**

> POST users/verify_user/
 
**Description**

To verify a user is available and the password is correct.

**Example Request**
> URL: http://127.0.0.1:8080/users/verify_user
```json
{
    "username": "Jason",
    "password": "Jason1234"
}
```
**Responses**

**200** OK: Successfully verified.
```json
{
  "success": true,
  "reason": ""
}
```

**401** Unauthorized: The password is not correct.
```json
{
  "success": false,
  "reason": "The password is not correct!"
}
```
**404** Not Found: The username does not exist.
```json
{
  "success": false,
  "reason": "The username: Jason does not exist!"
}
```
**429** Too Many Requests: User is not allowed for verification within a period.
```json
# This format is shown when reaching the fifth failure.
{
  "success": false,
  "reason": "You have entered wrong password for over 5 time. Please retry after 60 seconds."
}
          
# This format is shown when the user is still not allowed to do the verification.
{
  "success": false,
  "reason": "Please try later."
}
```

**Notes**
> IP address: localhost  
> Port: 8080