#### Relation Extraction
To train the model, run learn.py (you can use the already trained model model.pkl & feature.pkl)
Please use the .txt file
python learn.py CORPUS.TRAIN.txt TRAIN.annotations

To extract the relations, run extract.py:
Please use the .txt file
python extract.py CORPUS.TRAIN.txt train.annotations

It will write in train.annotations the extracted relations

To evaluate, run eval.py:
python eval.py TRAIN.annotations train.annotations
It follow the format
python eval.py gold pred
