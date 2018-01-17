# Relation Extraction - Report
> Adele Bendayan - 336141056

## Process
I started with a rule based system.

Rule:
1. Find the connection according to the dependency graph. When we get a location, find a person that is parent to it
**Precision on test: 41,5%**;
**Recall on test: 20,7%**


### Analysis
#### Errors on rules
1. The type of errors that I see, are relations that have too many values in person / location
