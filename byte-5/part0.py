__author__ = 'vikram'
import json

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats

from apiclient.discovery import build


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

# ================================================================
# Statistics
#================================================================

# Checking whether a difference is significant
# Are cats returned to owners at the same rate as dogs (H0)
# or is the difference significant (H1)

# first let's grab the data
n_groups = 2  # cats and dogs
outcome_types = ['Returned to Owner', 'Transferred to Rescue Group', 'Adopted', 'Foster', 'Euthanized']
outcome_labels = ['Owner', 'Rescue Group', 'Adopted', 'Foster', 'Euthanized', 'Other']
cat_outcomes = np.array([0.0, 0, 0, 0, 0, 0])
dog_outcomes = np.array([0.0, 0, 0, 0, 0, 0])

# loop through all of the rows of data
rows = dogs['rows']  # the actual data

for dog in rows:
    # get the outcome for this dog
    outcome = dog[13]
    try:
        i = outcome_types.index(outcome)
        # one of outcome_types
        dog_outcomes[i] = dog_outcomes[i] + 1
    except ValueError:
        # everything else
        dog_outcomes[5] = dog_outcomes[5] + 1
rows = cats['rows']  # the actual data
for cat in rows:
    # get the outcome for this cat
    outcome = cat[13]
    try:
        i = outcome_types.index(outcome)
        # one of outcome_types
        cat_outcomes[i] = cat_outcomes[i] + 1
    except ValueError:
        # everything else
        cat_outcomes[5] = cat_outcomes[5] + 1

print "cat_outcomes", cat_outcomes
print "dog_outcomes", dog_outcomes

# plot the data to see what it looks like
fig, ax = plt.subplots()
index = np.arange(6)
bar_width = 0.35
opacity = 0.4
rects1 = plt.bar(index, dog_outcomes, bar_width, alpha=opacity, color='b', label='Dogs')
rects2 = plt.bar(index + bar_width, cat_outcomes, bar_width, alpha=opacity, color='r', label='Cats')
plt.ylabel('Number')
plt.title('Number of animals by animal type and outcome type')
plt.xticks(index + bar_width, outcome_labels)
plt.legend()
plt.tight_layout()
plt.show()

# from this I'd say it looks like there's a real difference.
# Let's do a significance test

# Step 1: alpha = .05
alpha = .05

# Step 2: define hypotheses:
# Hypothesis 1: cat_outcomes = dog_outcomes
# Hypothesis 2: cat_outcomes != dog_outcomes

# Step 3: calculate the statistic (in this case
# we will have to use a ChiSquare test beacuse the
# data is nominal (non-parametric). Note that this returns
# a p value, so we don't need to determine the critical value
# here is a good explanation of ChiSquare tests:
# http://stattrek.com/chi-square-test/independence.aspx
# this one too
# http://udel.edu/~mcdonald/statchiind.html

Observed = np.array([cat_outcomes, dog_outcomes])
X_2, p, dof, expected = scipy.stats.chi2_contingency(Observed)
print "X_2", X_2, ", p", p

# Step 4: State decision rule
# Hypothesis 1 is rejected if p < alpha
# Hypothesis 2 is rejected if p > alpha

# Step 5: State conclusion:
if (p < alpha):
    print "The difference is significant. H0 (cats and dogs have the same outcomes) is rejected."
else:
    print "The difference is not significant. H1 (cats and dogs have different outcomes) is rejected."

# =====================================================================
# Now do something similar for animals under one year of age
# =====================================================================

# first let's grab the data

# organize the data into outcome arrays for each age type

# plot the data to see what it looks like

# Step 1: alpha = .05
alpha = .05

# Step 2: define hypotheses (something like this):
# Hypothesis 1: young_outcomes = old_outcomes = unkwnown_outcomes
# Hypothesis 2: something is different

# Step 3: calculate the statistic (in this case
# we will have to use a ChiSquare test beacuse the
# data is nominal (non-parametric). Note that this returns
# a p value, so we don't need to determin the critical value



# Step 5: State decision rule
# Hypothesis 1 is rejected if p < alpha
# Hypothesis 2 is rejected if p > alpha

# Step 6: State conclusion: