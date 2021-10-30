# serverless-fastapi
Tinny example of how to run a webhook using fast-api with serverless framework.


# How to execute
To execute run the below command, the aws-profile will depend the profile that you configure in the aws credentials mostly default if you don't

```sls deploy --aws-profile=upsensor-jaime --stage=staging```


run server locally
```uvicorn main:app --reload```
