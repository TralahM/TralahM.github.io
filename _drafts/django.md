## Scaling databases
1. Too much load - replicate db
* master slaves
* replication lags
* no increase on write speed
2. Too much data = sharding db
* multiples slaves and masters
* complex queries
* joins become difficult
* Design the data such that you would not need joins

## Best practices scaling django

### scaling Out
* adding more servers across multiple data centers
* Running out space,power outages
* Multiple regions to fallback on.
* application tolerance for inconsistency

### scaling Up
* use a few cpu instructions as possible
* as few servers as possible
* cpu usage versus API endpoint
* python cprofile

### Scaling Dev Teams
