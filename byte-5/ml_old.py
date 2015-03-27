import httplib2
from StringIO import StringIO
from apiclient.discovery import build
import urllib
import json
import csv
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
from sklearn.naive_bayes import GaussianNB
from sklearn import tree
from sklearn import cross_validation
from sklearn import preprocessing
from sklearn import metrics
from sklearn.dummy import DummyClassifier

# This API key is provided by google as described in the tutorial
API_KEY = "AIzaSyCfRmwMKY8NVG1YSP_bJzA44orhsZOtjmY"
TABLE_ID = "1HLka9ST2CZW9EE8kQkrw8FACWEttqFEqrzYPkf3N"

# open the data stored in a file called "data.json"
try:
    fp = open("data/dogs1.json")
    dogs = json.load(fp)
    fp = open("data/cats1.json")
    cats = json.load(fp)

# but if that file does not exist, download the data from fusiontables
except IOError:
    service = build('fusiontables', 'v1', developerKey=API_KEY)
    query = "SELECT * FROM " + TABLE_ID + " WHERE  'Animal Type' = 'DOG'"
    dogs = service.query().sql(sql=query).execute()
    fp = open("data/dogs1.json", "w+")
    json.dump(dogs, fp)
    query = "SELECT * FROM " + TABLE_ID + " WHERE  'Animal Type' = 'CAT'"
    cats = service.query().sql(sql=query).execute()
    fp = open("data/cats1.json", "w+")
    json.dump(cats, fp)



#================================================================
# Machine Learning
#================================================================
# We want to store the complete data set to disk
# beacuse we need to randomize the order and we don't
# want to have the random order change every time we
# run this program. This is especially important because
# if we re randomize every time the optimization set will
# be different every time which will add bias to our results
try:
    fp = open("data/random_dogs_and_cats4.json")
    all_data = np.array(json.load(fp))

# but if that file does not exist, download the data from fusiontables
except IOError:
    # make an array of all data about cats and dogs
    all_data = cats['rows'] + dogs['rows']
    # randomize it so the cats aren't all first
    np.random.shuffle(all_data)
    fp = open("data/random_dogs_and-cats4.json", "w+")
    json.dump(all_data, fp)
    all_data = np.array(all_data)

# We'd like to use both dogs and cats, and we'll want to use several different
# features (not just the two we were playing with)

# For a first pass, these are likely to be useful features
# I'm avoiding actual dates because they are hard to parse
# and I'm avoiding anything to do with the outcome  (such as outcome date)
# as that might bias the results
# It may be important to calculate features based on these though
# such as something that deals better with mixed breeds to improve the results

# IMPORTANT NOTE: make sure these appear in this array in the same order as they
# do in the columns array (this will help with labeling later in the machine
# learning work)
features = ['Animal Type', 'IntakeMonth', 'Breed', 'Age', 'Sex', 'SpayNeuter',
            'Size', 'Color', 'IntakeType']
# this will be the class we are predicting.
# We will need to narrow it down to fewer classes probably
out = 'Outcome'

# the column names are the same for cats and dogs. Pick one
# to work with
cols = cats['columns']

# make a new, empty array that will store
# for each column we should use
use_data = []
out_index = 13
# and loop through the columns
ncols = len(cols)
for i in np.arange(ncols):
    try:
        # we want to use a column 
        # if its name is in the list of features we want to keep
        features.index(cols[i])
        use_data.append(i)
    except ValueError:
        # and if it matches the name of the column we are predicting
        # ('Outcome') we capture the column index for later
        if cols[i] == out:
            out_index = i

# Now we create a new array that only has the columns we care about in it
X = all_data[:, use_data]
# This is just the column with the outcome values
y = all_data[:, out_index]

# Make all the outcomes that are very rare be "Other"
y[y == "No Show"] = "Other"
y[y == "Missing Report Expired"] = "Other"
y[y == "Found Report Expired"] = "Other"
y[y == "Lost Report Expired"] = "Other"
y[y == "Released in Field"] = "Other"
y[y == ''] = "Other"
y[y == "Died"] = "Other"
y[y == "Disposal"] = "Other"
y[y == "Missing"] = "Other"
y[y == "Trap Neuter/Spay Released"] = "Other"
y[y == "Transferred to Rescue Group"] = "Other"
y[y == u'Foster'] = "Other"

# Leave the following outcomes as separate (may want to 
# combine some of these to reduce the number of classes 
# and improve the results) 
# Returned to Owner; Adopted; Euthanized
y[y == "Returned to Owner"] = "Home"
y[y == u'Adopted'] = "Home"
y[y == u'Euthanized'] = "Euthanized"
# So for now we have 5 classes total: Other, Foster, Owner, Adopted, Euthanized
Outcomes = ["Euth.", "Home", "Other"]

# We'll use the first 20%. This is fine
# to do because we know the data is randomized.
nrows = len(all_data)
percent = len(X) / 5
X_opt = X[:percent, :]
y_opt = y[:percent]

# and a train/test set
X_rest = X[percent:, :]
y_rest = y[percent:]

# ======================================================
# print out files for orange if you want to use that
# ======================================================



# ======================================================
# use scikit-learn
# ======================================================

# and we need to convert all the data from strings to numeric values
le = preprocessing.LabelEncoder()
labels = []
le
# collect all the labels. The csv files we are loading 
# were generated back in byte 2 and are provided as part
# of this source code. They just contain all possible
# values for each column. We're putting those values all
# in a list now
for name in features:
    csvfile = open('data/{0}.csv'.format(name), 'rb')
    datareader = csv.reader(csvfile, delimiter=',')
    for row in datareader:
        labels.append(row[0])
# make a label for empty values too
labels.append(u'')
le.fit(labels)

# now transform the array to have only numeric values instead
# of strings
X = le.transform(X)

# Lastly we need to split these into a optimization set
# using about 20% of the data
nrows = len(all_data)
percent = len(X) / 5

# We'll use the first 20%. This is fine
# to do because we know the data is randomized.
X_opt = X[:percent, :]
y_opt = y[:percent]

# and a train/test set
X_rest = X[percent:, :]
y_rest = y[percent:]

dc = DummyClassifier(strategy='most_frequent', random_state=0)
gnb = GaussianNB()
dt = tree.DecisionTreeClassifier(max_depth=5)
# you could try other classifiers here

# make a set of folds
skf = cross_validation.StratifiedKFold(y_opt, 10)
gnb_acc_scores = []
dc_acc_scores = []
dt_acc_scores = []
# loop through the folds
for train, test in skf:
    # extract the train and test sets
        # extract the train and test sets
    X_train, X_test = X_rest[train], X_rest[test]
    y_train, y_test = y_rest[train], y_rest[test]

    # train the classifiers
    dc = dc.fit(X_train, y_train)
    gnb = gnb.fit(X_train, y_train)
    dt = dt.fit(X_train, y_train)

    # test the classifiers
    dc_pred = dc.predict(X_test)
    gnb_pred = gnb.predict(X_test)
    dt_pred = dt.predict(X_test)

    # calculate metrics relating how well they did
    dc_accuracy = metrics.accuracy_score(y_test, dc_pred)
    dc_precision, dc_recall, dc_f, dc_support = metrics.precision_recall_fscore_support(y_test, dc_pred)

    gnb_accuracy = metrics.accuracy_score(y_test, gnb_pred)
    gnb_precision, gnb_recall, gnb_f, gnb_support = metrics.precision_recall_fscore_support(y_test, gnb_pred)

    dt_accuracy = metrics.accuracy_score(y_test, dt_pred)
    dt_precision, dt_recall, dt_f, dt_support = metrics.precision_recall_fscore_support(y_test, dt_pred)

    dc_acc_scores = dc_acc_scores + [dc_accuracy]
    gnb_acc_scores = gnb_acc_scores + [gnb_accuracy]
    dt_acc_scores = dt_acc_scores + [dt_accuracy]

    # print the results for this fold
    print "Accuracy "
    print "Dummy Cl: %.2f" % dc_accuracy
    print "Naive Ba: %.2f" % gnb_accuracy
    print "DT : %.2f" % dt_accuracy
    print "F Score"
    print "Dummy Cl: %s" % dc_f
    print "Naive Ba: %s" % gnb_f
    print "DT : %s" % dt_f
    print "Precision", "\t".join(list(Outcomes))
    print "Dummy Cl:", "\t".join("%.2f" % score for score in dc_precision)
    print "Naive Ba:", "\t".join("%.2f" % score for score in gnb_precision)
    print "DT :", "\t".join("%.2f" % score for score in dt_precision)
    print "Recall   ", "\t".join(list(Outcomes))
    print "Dummy Cl:", "\t".join("%.2f" % score for score in dc_recall)
    print "Naive Ba:", "\t".join("%.2f" % score for score in gnb_recall)
    print "DT :", "\t".join("%.2f" % score for score in dt_recall)

    dc_acc_scores = dc_acc_scores + [dc_accuracy]
    gnb_acc_scores = gnb_acc_scores + [gnb_accuracy]
    dt_acc_scores = dt_acc_scores + [dt_accuracy]

diff = np.mean(dc_acc_scores) - np.mean(gnb_acc_scores)
t, prob = scipy.stats.ttest_rel(dc_acc_scores, gnb_acc_scores)

tree.export_graphviz( dt, out_file = 'tree.dot', feature_names=features)

print "============================================="
print " Results of optimization  "
print "============================================="
print "Dummy Mean accuracy: ", np.mean(dc_acc_scores)
print "Naive Bayes Mean accuracy: ", np.mean(gnb_acc_scores)
print "DT Mean accuracy: ", np.mean(dt_acc_scores)
print "Accuracy for Dummy Classifier and Naive Bayes differ by {0}; p<{1}".format(diff, prob)
diff = np.mean(dc_acc_scores) - np.mean(dt_acc_scores)
t, prob = scipy.stats.ttest_rel(dc_acc_scores, dt_acc_scores)
print "Accuracy for Dummy Classifier and DT differ by {0}; p<{1}".format(diff, prob)

print "These are good summary scores, but you may also want to"
print "Look at the details of what is going on inside this"
print "Possibly even without 10 fold cross validation"
print "And look at the confusion matrix and other details"
print "Of where mistakes are being made for developing insight"

print "============================================="
print " Final Results "
print "============================================="
print "When you have finished this assignment you should"
print "train a final classifier using the X_rest and y_rest"
print "using 10-fold cross validation"
print "And you should print out some sort of statistics on how it did"

gnb_acc_scores = []
dc_acc_scores = []
dt_acc_scores = []
skf = cross_validation.StratifiedKFold(y_rest, 10)
# loop through the folds
for train, test in skf:
    # extract the train and test sets
    X_train, X_test = X_rest[train], X_rest[test]
    y_train, y_test = y_rest[train], y_rest[test]

    # train the classifiers
    dc = dc.fit(X_train, y_train)
    gnb = gnb.fit(X_train, y_train)
    dt = dt.fit(X_train, y_train)

    # test the classifiers
    dc_pred = dc.predict(X_test)
    gnb_pred = gnb.predict(X_test)
    dt_pred = dt.predict(X_test)

    # calculate metrics relating how well they did
    dc_accuracy = metrics.accuracy_score(y_test, dc_pred)
    dc_precision, dc_recall, dc_f, dc_support = metrics.precision_recall_fscore_support(y_test, dc_pred)

    gnb_accuracy = metrics.accuracy_score(y_test, gnb_pred)
    gnb_precision, gnb_recall, gnb_f, gnb_support = metrics.precision_recall_fscore_support(y_test, gnb_pred)

    dt_accuracy = metrics.accuracy_score(y_test, dt_pred)
    dt_precision, dt_recall, dt_f, dt_support = metrics.precision_recall_fscore_support(y_test, dt_pred)

    dc_acc_scores = dc_acc_scores + [dc_accuracy]
    gnb_acc_scores = gnb_acc_scores + [gnb_accuracy]
    dt_acc_scores = dt_acc_scores + [dt_accuracy]
    print "Accuracy "
    print "Dummy Cl: %.2f" % dc_accuracy
    print "Naive Ba: %.2f" % gnb_accuracy
    print "DT : %.2f" % dt_accuracy
    print "F Score"
    print "Dummy Cl: %s" % dc_f
    print "Naive Ba: %s" % gnb_f
    print "DT : %s" % dt_f
    print "Precision", "\t".join(list(Outcomes))
    print "Dummy Cl:", "\t".join("%.2f" % score for score in dc_precision)
    print "Naive Ba:", "\t".join("%.2f" % score for score in gnb_precision)
    print "DT :", "\t".join("%.2f" % score for score in dt_precision)
    print "Recall   ", "\t".join(list(Outcomes))
    print "Dummy Cl:", "\t".join("%.2f" % score for score in dc_recall)
    print "Naive Ba:", "\t".join("%.2f" % score for score in gnb_recall)
    print "DT :", "\t".join("%.2f" % score for score in dt_recall)


diff = np.mean(dc_acc_scores) - np.mean(gnb_acc_scores)
t, prob = scipy.stats.ttest_rel(dc_acc_scores, gnb_acc_scores)

print "============================================="
print " Results of optimization  NB"
print "============================================="
print "Dummy Mean accuracy: ", np.mean(dc_acc_scores)
print "Naive Bayes Mean accuracy: ", np.mean(gnb_acc_scores)
print "DT Mean accuracy: ", np.mean(dt_acc_scores)
print "Accuracy for Dummy Classifier and Naive Bayes differ by {0}; p<{1}".format(diff, prob)
diff = np.mean(dc_acc_scores) - np.mean(dt_acc_scores)
t, prob = scipy.stats.ttest_rel(dc_acc_scores, dt_acc_scores)
print "Accuracy for Dummy Classifier and DT differ by {0}; p<{1}".format(diff, prob)
