The file path is hardcoded in indexer.py,merger.py, and search.py.
For indexer.py the path variable should be the folder containing folders of json files
For Merger.py the path variable should point to the folder containing the pickled partial indexes
for search.py the chdir at the top should change to the folder containing the pickled files

Run indexer.py first to build partial indexes which will be output into pickle files organized by starting letter once the total size of the total indexed words exceeded 6MB.
At the end of runtime, a pickle file containing all the file id's and their urls is also output.

Run merger.py second to combine all the partial pickled files into a large raw-text file. merger.py opens all pickle files that have the same starting letter, combines all same words and their postings, and finally writes the postings to a line in the text file.
Each line in the text file is referenceable from the 'indexindex.p' pickle file which has an index of the word and where in the text file the postings for that word start. On its own, the text file is comprised of comma separated values fid,weightedTFscore which are separated by semicolons to denote the next posting.


After indexer.py and merger.py have been run to completion, search.py can be run to handle search queries.