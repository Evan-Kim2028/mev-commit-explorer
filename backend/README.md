# backend-api

Describe your project here.


### What Tables are there
```bash
curl -X 'GET' \
  'http://localhost:8000/tables' \
  -H 'accept: application/json'
```

### Aggregation
```bash
curl -X 'GET' \
  'http://localhost:8000/preconfs/aggregations?group_by_field=bidder' \
  -H 'accept: application/json'
```



curl -X 'GET'   'http://45.250.253.241:8000/preconfs/aggregations?group_by_field=bidder'   -H 'accept: application/json'


curl -X GET "http://45.250.253.241:8000/preconfs?page=1" -H 'accept: application/json'



curl -X 'GET' \
  'http://localhost:8000/tables/encrypted_stores/schema' \
  -H 'accept: application/json'