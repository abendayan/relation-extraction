# Relation Extraction - Report
> Adele Bendayan - 336141056

** I worked on the Live_In relation **
## Description of the system
I implemented a mix of feature learning and rule based approach.
First I broke each sentence in the training file into chunk and created features, and than I learned on them.

This is done in the learn.py.
### Feature based learning
#### Features used
* entity of the head words
* the head words
* concatenation of the entities
* the pos tags of all the words in the chunk
* the words before and after each chunk (if exist)
* the words between the 2 chunks
* the pos tags of the words between the two chunks
* if the pos tag of the words chunk start with NN (a type of noun), I added a feature with the tag NN, if not with the pos tag of the word
* with wordnet I got all the synonyms of each words, and added them as feature
* the dependency tree between the words
* I used json files to get the countries, cities, state in the U.S, and for each word, I check if it's a country a city or a state, if yes, I added this as a feature

Once I got all of this features, I check if the chunk is connected in the training annotation file, if it is, I mark it as correct and give as a tag the tag of the connection (any connection that exist in the training file, not just Live_In).

I train with an SVC classifier.

### Rectification of errors
When extracting the relations, to compensate the error of the classifier, I implemented a rule based approach.

The idea is, I first use the classifier, if I get the tag of Live_In I added the chunks in the annotations file, if I get the Other_Tag (the classifier didn't succeed in placing the relation in one of the tags that we learned on), then I go through the rules:

#### Patterns
The left chunk should be a person and the right chunk should be a location (or a tag location or in countries cities, or state).
If that is the case, than we go through the rules, if not, we throw the chunk away.
* If before the first chunk we have a "work" word than we accept the rule
* If between the words we see words like "live in", "stay in", "live on"... than we accept the words
* If we have words like "home of", "governor of" ("Reith Chuol governor of the Upper Nile region")
* If we see words like "manager" we do not accept the chunk (it probably is correct for Work_For)

## Error analysis
Most of the error in prediction are confusion with the tag Work_For or OrgBased_In: tags that also have location in them. I didn't succeed in lowering this type of error without hurting the recall.

The recall errors mostly came from location that are not tagged as location but as GPE or other, adding those tags to the possible location hurt the precision and the recall, I think because it's harder for the classifier to learn.

## Results
Relation  | Dev Recall | Dev Prec | Dev F1 | Test Recall| Test Prec | Test F1
-------- | --|-|-|-|-|
Live_In  | 0.27 | 0.37 | 0.32 | 0.60 | 0.80 | 0.68
