## How-to Guide

### Prerequisites
Create a virtual environment using conda and install necessary packages
```shell
conda install -n bentoml python==3.9
conda activate bentoml
```

### Local development
Test your service locally by simply running the following command
```shell 
bentoml serve service:svc
```
OR the command below if you want to use the configuration file
```shell 
BENTOML_CONFIG=bentoml_configuration.yaml bentoml serve service:svc
```

### Package your application
Package your service into a Docker image using the following command
```shell
bentoml build
bentoml containerize anomaly_detection_demo:6kzsvxduf6cw7oo3
```
OR use a single command like this
```shell
bentoml build --containerize
```

### Run your application locally

```shell
docker run -p 3000:3000 anomaly_detection_demo:
fsalwcdugccw7oo3
```
Note that, your tag may be different from mine, which is `fsalwcdugccw7oo3`, so please use yours.

There are several ways to make predictions, please refer to [this tutorial](https://docs.bentoml.org/en/latest/quickstarts/deploy-a-transformer-model-with-bentoml.html#create-a-bentoml-service).


