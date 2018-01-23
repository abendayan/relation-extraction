# Relation Extraction - Report
> Adele Bendayan - 336141056

## Process
I first tried a rule based system, but I was stuck on low accuracy, so I tried a feature extraction system.

**Precision accuracy: 76,6%**
**Recall accuracy: 51,1%**

Adding a check to see that the words are person-location change the accuracy to:
**Precision accuracy: 88,4%**
**Recall accuracy: 45,8%**

Added NORP in location
**Prec accuracy: 79,2%**
**Recall accuracy: 48,8%**

Not JJ
**Prec accuracy: 88,57%**
**Recall accuracy: 46,5**

Pos is NN*:
**Prec accuracy: 92,3%**
**Recall accuracy: 45,0%**

When looking at the precision errors, I realized that some of the errors are "." in the end, I decided to ignore them.
What is missing are stuff like:
Prince + name
Mrs + name

**Prec accuracy: 95,9%**
**Recall accuracy: 34,4%**

Added cities

**Prec accuracy: 96,2%**
**Recall accuracy: 39,69%**

Added wordnet:

**Prec accuracy: 92,9%**
**Recall accuracy: 40,4%**

clean annotations:

**Prec accuracy: 94,7%**
**Recall accuracy: 40,9%**



############## remarks
learning for all the tags hurts the performance
### Analysis
#### Errors on rules
1. The type of errors that I see, are relations that have too many values in person / location
