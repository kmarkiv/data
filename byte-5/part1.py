__author__ = 'vikram'
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
    fp = open("data/dogs21.json")
    dogs1 = json.load(fp)
    fp = open("data/dogs22.json")
    dogs2 = json.load(fp)
    fp = open("data/dogs23.json")
    dogs0 = json.load(fp)


# but if that file does not exist, download the data from fusiontables
except IOError:
    service = build('fusiontables', 'v1', developerKey=API_KEY)
    query = "SELECT * FROM " + TABLE_ID + " WHERE  'Animal Type' = 'DOG' AND 'Estimated Age' IN ('Infant - Younger than 6 months', 'Youth - Younger than 1 year')"
    dogs1 = service.query().sql(sql=query).execute()
    fp = open("data/dogs21.json", "w+")
    json.dump(dogs1, fp)
    query = "SELECT * FROM " + TABLE_ID + " WHERE  'Animal Type' = 'DOG' AND 'Estimated Age' NOT IN ('','Infant - Younger than 6 months', 'Youth - Younger than 1 year')"
    dogs2 = service.query().sql(sql=query).execute()
    fp = open("data/dogs22.json", "w+")
    json.dump(dogs2, fp)
    query = "SELECT * FROM " + TABLE_ID + " WHERE  'Animal Type' = 'DOG' AND 'Estimated Age' IN ('')"
    dogs0 = service.query().sql(sql=query).execute()
    fp = open("data/dogs23.json", "w+")
    json.dump(dogs0, fp)

# ================================================================
# Statistics
# ================================================================

# Checking whether a difference is significant
# Are dogs2 returned to owners at the same rate as dogs (H0)
# or is the difference significant (H1)

# first let's grab the data
n_groups = 2  # dogs2 and dogs
outcome_types = ['Returned to Owner', 'Transferred to Rescue Group', 'Adopted', 'Foster', 'Euthanized']
outcome_labels = ['Owner', 'Rescue Group', 'Adopted', 'Foster', 'Euthanized', 'Other']
dog_outcomes_old = np.array([0.0, 0, 0, 0, 0, 0])
dog_outcomes = np.array([0.0, 0, 0, 0, 0, 0])
dog_outcomes_na = np.array([0.0, 0, 0, 0, 0, 0])

# loop through all of the rows of data
rows = dogs1['rows']  # the actual data

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
rows = dogs2['rows']  # the actual data
for cat in rows:
    # get the outcome for this cat
    outcome = cat[13]
    try:
        i = outcome_types.index(outcome)
        # one of outcome_types
        dog_outcomes_old[i] = dog_outcomes_old[i] + 1
    except ValueError:
        # everything else
        dog_outcomes_old[5] = dog_outcomes_old[5] + 1

rows = dogs0['rows']  # the actual data
for cat in rows:
    # get the outcome for this cat
    outcome = cat[13]
    try:
        i = outcome_types.index(outcome)
        # one of outcome_types
        dog_outcomes_na[i] = dog_outcomes_na[i] + 1
    except ValueError:
        # everything else
        dog_outcomes_na[5] = dog_outcomes_na[5] + 1

print "cat_outcomes", dog_outcomes_old
print "dog_outcomes", dog_outcomes
print "dog_outcomes", dog_outcomes_na

dog_outcomes_old = 100 * dog_outcomes_old / sum(dog_outcomes_old)
dog_outcomes = 100 * dog_outcomes / sum(dog_outcomes)
dog_outcomes_na = 100 * dog_outcomes_na / sum(dog_outcomes_na)

print "DOG_outcomes OLD", dog_outcomes_old
print "dog_outcomes", dog_outcomes
print "dog_outcomes NA", dog_outcomes_na


def autolabel(rects):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2., 1.01 * h, '%d' % int(h) + '%',
                ha='center', va='bottom')

# plot the data to see what it looks like
fig, ax = plt.subplots()
index = np.arange(6)
bar_width = 0.45
opacity = 0.4
rects1 = plt.bar(index, dog_outcomes, bar_width / 2, alpha=opacity, color='b', label='Dogs < 1yr')
autolabel(rects1)
rects2 = plt.bar(index + bar_width / 2, dog_outcomes_old, bar_width / 2, alpha=opacity, color='r', label='Dogs > 1yr')
rects3 = plt.bar(index + bar_width, dog_outcomes_na, bar_width / 2, alpha=opacity, color='g', label='Unknown ')
autolabel(rects2)
autolabel(rects3)
plt.ylabel('Percent')
plt.title('Number of dogs and outcome type')
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

def adopted(dogs,var=2):
    return [dogs[var],sum(dogs)-dogs[var]]



Observed = np.array([adopted(dog_outcomes_old), adopted(dog_outcomes), adopted(dog_outcomes_na)])
X_2, p, dof, expected = scipy.stats.chi2_contingency(Observed)
print "CHI ", X_2, ", p", p

# Step 4: State decision rule
# Hypothesis 1 is rejected if p < alpha
# Hypothesis 2 is rejected if p > alpha

# Step 5: State conclusion:
if (p < alpha):
    print "The difference is significant. H0 (dogs<1yr and dogs>1yr have the same outcomes) is rejected."
else:
    print "The difference is not significant. H1 (dogs<1yr and dogs>1yr have the same outcomes) is rejected."

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


outcome_sums = Observed.sum(axis=0)     # sum across cats and dogs of each outcome type
animal_type_sums = Observed.sum(axis=1) # number of cats and number of dogs
n = np.sum(outcome_sums)         # total number of rows across cats and dogs

print "Obs", Observed
print "sums", outcome_sums
print "sums", animal_type_sums

rs = 2 # the number of animal types
cs = 6 # the number of outcome types
Exp = np.empty([rs,cs])
c = 2
for r in range(0, rs):
      Exp[r,c] = (animal_type_sums[r] * outcome_sums[c])/n

print "Exp", Exp
print "Obs", Observed
X_2 = 0
for r in range(0, rs):
      diff = Exp[r, c] - Observed[r, c]
      X_2 = X_2 + (diff*diff)/Exp[r, c]
print "my CHI2: ", X_2


# Step 5: State decision rule
# Hypothesis 1 is rejected if p < alpha
# Hypothesis 2 is rejected if p > alpha

# Step 6: State conclusion: