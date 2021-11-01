# serverless-fastapi
Tinny example of how to run a webhook using fast-api with serverless framework.


# How to execute
To execute run the below command, the aws-profile will depend the profile that you configure in the aws credentials mostly default if you don't

```sls deploy --aws-profile=upsensor-jaime --stage=staging```


run server locally
```uvicorn main:app --reload```


Urls to download the zip files

1. https://9sbw0vf7d0.execute-api.us-east-1.amazonaws.com/staging/satellite_precipitation_history
2. https://9sbw0vf7d0.execute-api.us-east-1.amazonaws.com/staging/hydraulic_operation_reports
3. https://9sbw0vf7d0.execute-api.us-east-1.amazonaws.com/staging/daily_flow_forecast
4. https://9sbw0vf7d0.execute-api.us-east-1.amazonaws.com/staging/entry_exit_dectks_dessem