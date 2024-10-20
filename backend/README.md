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