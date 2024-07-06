# Caples Sound

A repo to assist in making the classifier for the Caples Creek Restoration Project at the California Academy of Sciences. We have terabytes of ARU data, and are using the Perch framework to build a customer classifier.

# Agile Modeling Workflow

- Compute the embeddings for all of the ARU recordings. [Notebook here](embed_all.ipynb)
- Gather "target recordings" for all of the species of interest. These recordings are used to gather examples of each species from the ARU recordings. Normally, these are from xeno-canto.
- Use the target recordings to search the ARU recordings for "similar" sound-bites that (hopefully) contain a similar vocalization to the target recordings. We can [precompute the results](precompute_search/) from the search to allow them to quickly be annotated by expert birders.
- Serve the precomputed search results to a web server that allows people (expert birders) to annotate the recordings and "train" the classifier. The goal of this step is to gather examples from the ARU data that contain the species of interest. We can split the species into song/call (or any other subclass), which the classifier will be able to distinguish with enough annotated examples. There is not a perfect number of examples for each class, but 10-20 seems to work well. We will call the annotated recordings "labeled outputs." See [this paper](https://www.nature.com/articles/s41598-023-49989-z) for more details.
- Train a classifier on the labeled outputs. Using this classifier (which is a single linear map from the embeddings to the output layer containing the classification), classify all of the recordings. 
