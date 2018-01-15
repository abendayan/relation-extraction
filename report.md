# Relation Extraction - Report
> Adele Bendayan - 336141056

## Process
I started with a rule based system.

Rule:
1. According to the NER tags: search for tags that are location and person, and  create a relation based on that. If they are more than one location or person, concatenate it.
**Precision on test: 30,7%%**
2. Added relation _of_: if I see of, I change the person to be the person before this
**Precision on test: 33,7%%**
3. If we have a ".", check the previous word, if it was a person, add the point to the person
**Precision on test: 34,6%**
4. Location that have _to_ before do not belong in a Live_In Relation, so are not counted
**Precision on test: 35,6%**
5. If before a person we have a word with tag _IN_, we "delete" the previous saved person
**Precision on test: 37,6%**


### Analysis
#### Errors on rules
1. The type of errors that I see, are relations that have too many values in person / location
