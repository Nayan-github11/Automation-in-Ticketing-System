# -*- coding: utf-8 -*-
"""automation-in-ticketing-(LDA).ipynb

##CRISP - ML
Business Problem and understanding 

##Problem Statement 

To identify the repeated actions through automation and minimize the escalation.
Every day customers report their problems through online portal of firm, but gets delayed because this quiers
don't reach their respective department. So we need to bulid the model which would do this task automatically
and increase customer satisfaction.

Since data is not labelled we will use LDA to analyis pattern and classify tickets into different number of clusters

##Business Objective and Constraint 
objective: Maximize customer satisfaction 
           Minimize manual efforts

Constraint: Minimize the cost
            Maximize the automated application.

##Sucess Criteria
a. Business sucess criteria: Increase correct allocation of department that will resolve query
b. ML sucess criteria : Achive atleast 80% accuracy

##Data Collection 
Data was collected from opean source platform. Which contains 17 columns.

1. data_reciived: The date on which CFPB recived complaint.             
2. product: Type of product (like debt collection,loan installment,etc) customer identified in complaint.
3. sub_product: Its detail of product like if debt collection, in that what type of debt collection credit card or other type.
4. issue: The issue the consumer identified in the complaint
5. sub_issue: Brif of actual issue.  
6. consumer_complaint_narrative: Detail narration of issue submitted by customer. 
7. company_public_response: The company's optional, public-facing response to a consumer's complaint
8. company: Complaint abou thsi company.
9. state: The state of mailing address. 
10. zipcode: Mailing zip code provided by customer.
11. tags: Based on age, profession tags like 'older american' for submitter above 60 years of age or 'service member' for national gaurd, veteran or retiree.
12. consumer_consent_provided: Identifies whether the consumer opted in to publish their complaint narrative
13. submitted_via: How complaint was submitted to CFPB, mail, phone or referal. 
14. date_sent_to_company: The date on which complaint submitted by CFPB to company. 
15. company_response_to_consumer: How company responded eg. "closed with explaination"
16. timely_response: Weather company reponded on time?
17. consumer_disputed: Weather customer disputed company's response?
18. complaint_id: Unique identification no fo complaint.

##Pipeline for project

You need to perform the following eight major tasks to complete the assignment:

Data loading

Text preprocessing

Exploratory data analysis (EDA)

Feature extraction

Topic modelling

Model building using supervised learning

Model training and evaluation

Model inference
"""

import pandas as pd
import numpy as np
import seaborn as sns
import re
import nltk

import matplotlib.pyplot as plt

data = pd.read_csv("file_path")
data.info()

data.shape

# Disply all columns
print(data.columns)

# Check for missing values
data.isna()

# Number of missing values in 'narrative column"'
data['consumer_complaint_narrative'].isna().sum()

# Here 'consumer_complaint_narrative' is important so we will consider only those row where this column doesn't have null value 
#Remove all rows where complaints column is nan
data1 = data[~data['consumer_complaint_narrative'].isnull()]

data1.shape

data1.info()

data1.astype({"consumer_complaint_narrative":"str"},copy=True)

## Performing data preprocessing on this data
#1. Removing special charaters
#2. Convertiing text to lower case
#3. Applying

def clean_text(sent):
    sent = sent.lower()
    pattern = '[^\w\s]'
    sent = re.sub(pattern, '', sent)
    pattern = '\w*\d\w*'
    sent = re.sub(pattern, '',sent)
    return sent

com_txt = pd.DataFrame(data1['consumer_complaint_narrative'].apply(clean_text))

com_txt

# Lemmatization
import nltk
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('omw-1.4')
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

def lemmatize_text(text):
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(lemmatized_tokens)

com_txt['ccn_lemma'] = com_txt['consumer_complaint_narrative'].apply(lemmatize_text)

# Generally POS tagging is required for NLP for sentiment anaysis and name entity regcognition bus here 
# Removing POS tag will make data less complex which wil hel
from textblob import TextBlob
#nltk.download('averaged_perceptron_tagger')
def remove_textblob_tags(text):
    blob = TextBlob(text)
    return " ".join([word for word, pos in blob.tags if pos[0] in ['N', 'V']])

com_txt['ccn_removedPOS'] = com_txt['ccn_lemma'].apply(remove_textblob_tags)

# So now we have clean "consumer_complaint_narrative" for further data mining
com_txt

# Explotary data analysis 
#we will perform EDA for data visualization according to complaint'c character length
#and finding top word frequency and unigram, bigram,trigram frequency using wordcloud

# Histogrm according to character length
char_len = [len(each_sent) for each_sent in com_txt['ccn_lemma']]

sns.displot(char_len, kind='hist', bins=60)
plt.xlabel("Complaint character length")
plt.ylabel("Total number of Complaints")
plt.title("Distribution of Complaint character length")
plt.show()

"""In above graph distribution is slightly right skew, but it is normal ditribution"""

# To Remove stopwords from data, import from library
import nltk
from nltk.corpus import stopwords
#nltk.download('stopwords') if error to download
from nltk.tokenize import word_tokenize

with open('D:\\360 digi tmg\\Internship\\stop.txt')as sw:
    stopwords = sw.read()

"""To Remove stopwords from data, import from library
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords') if error to download
from nltk.tokenize import word_tokenize

with open('/kaggle/input/stopwords/stopwords.txt')as sw:
    stopwords = sw.read()
"""

#define stopword function
def remove_stopwords(text,extended_stopwords=[]):
    filtered_words = [word for word in text.split() if word.lower() not in stopwords]
    return" ".join(filtered_words)

# Word cloud according to top 40 words with high frequency
from wordcloud import WordCloud
wordcloud = WordCloud(max_font_size=60, max_words=40, 
                      background_color="white", random_state=100).generate(str(com_txt['ccn_removedPOS']))
plt.figure(figsize=[12,12])
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

# There are some customize stopwords
#this extended stopwords we take according to data
# This x's are used for masking purpose to either date, names or other pecifications.
extended_stopwords = ["xxxx", "xxxxxxxx", "xxxxxxxxxxxx", "xxxx xxxx xxxx xxxx","xxxx xxxx", "wa", "ha"]

stopwords = set(stopwords).union(extended_stopwords)

#and apply it
com_txt['ccn_removedPOS'] = com_txt['ccn_removedPOS'].apply(remove_stopwords, extended_stopwords)

#After removing customize stop words we will again plot word cloud 
# Word cloud according to top 40 words with high frequency
from wordcloud import WordCloud
wordcloud = WordCloud(max_font_size=60, max_words=40, 
                      background_color="white", random_state=100).generate(str(com_txt['ccn_removedPOS']))
plt.figure(figsize=[12,12])
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

"""So here top words we observerd are loan, mortage,paid,account ,issue etc."""

#Removing -PRON- from the text corpus removing "-PRON-" from the text corpus involves replacing it with the appropriate personal pronoun in order to improve the accuracy of NLP analysis.
com_txt['ccn_clean'] = com_txt['ccn_removedPOS'].str.replace('-PRON-', '')

com_txt

# Now we will find top n_grams like unigram, bigram and trigram from data based on there frequency.it provides insights into the most common words and word sequences in a corpus.

from sklearn.feature_extraction.text import CountVectorizer

# Creating a function to extract top ngrams(unigram/bigram/trigram) based on the function inputs
def get_top_ngrams(text, n=None, ngram=(1,1)):
  vec = CountVectorizer(stop_words='english', ngram_range=ngram).fit(text)
  bagofwords = vec.transform(text)
  sum_words = bagofwords.sum(axis=0)
  words_frequency = [(word, sum_words[0, index]) for word, index in vec.vocabulary_.items()]
  words_frequency = sorted(words_frequency, key = lambda x: x[1], reverse=True)
  return words_frequency[:n]

# So we want top 30 unigram so 
n= 30
ngram_range = (1,1)

Top_30Unigrams = get_top_ngrams(com_txt['ccn_clean'].values.astype('U'), n,ngram_range)
data1_unigram = pd.DataFrame(Top_30Unigrams, columns = ['unigram', 'count'])
data1_unigram

# Plotting top 30 Unigrams
plt.figure(figsize=[20,6])
sns.barplot(x=data1_unigram['unigram'], y=data1_unigram['count'])
plt.xticks(rotation=45)
plt.xlabel("Unigram")
plt.ylabel("Count")
plt.title("Count of top 30 Unigrams")
plt.show()

# Now lets find top 30 bigram  
n= 30
ngram_range = (2,2)

Top_30Unigrams = get_top_ngrams(com_txt['ccn_clean'].values.astype('U'), n,ngram_range)

data1_bigram = pd.DataFrame(Top_30Unigrams, columns = ['bigram', 'count'])
data1_bigram

#Plotting barplot for bigram
plt.figure(figsize=[20,6])
sns.barplot(x=data1_bigram['bigram'], y=data1_bigram['count'])
plt.xticks(rotation=45)
plt.xlabel("Bigram")
plt.ylabel("Count")
plt.title("Count of top 30 Unigrams")
plt.show()

# Now lets find top 30 trigram

n = 30
ngram_range = (3,3)

Top_30trigram = get_top_ngrams(com_txt['ccn_clean'].values.astype('U'), n,ngram_range)

Top_30trigram

data1_trigram = pd.DataFrame(Top_30trigram, columns = ['trigram', 'count'])
data1_trigram

#Plotting barplot for trigram
plt.figure(figsize=[20,6])
sns.barplot(x=data1_trigram['trigram'], y=data1_trigram['count'])
plt.xticks(rotation=45)
plt.xlabel("Bigram")
plt.ylabel("Count")
plt.title("Count of top 30 Unigrams")


plt.show()

com_txt

com_txt.info()

"""#Here we will do topic modeling using LDA"""

import gensim
from gensim import corpora

# Tokenize the documents
tokenized_docs = [doc.lower().split() for doc in com_txt['ccn_clean']]

#The function tokenize_text takes in a string of text and splits it into individual words. The resulting output is a list of strings,
#where each element of the list is a single word from the original input text.

def tokenize_text(text):
    return text.split()

com_txt['ccn_clean_2']= com_txt['ccn_clean'].apply(tokenize_text)

com_txt

# Create a dictionary of unique words
dictionary = corpora.Dictionary(com_txt['ccn_clean_2'])

# Convert the tokenized documents into a bag-of-words representation
corpus = [dictionary.doc2bow(tokens) for tokens in com_txt['ccn_clean_2']]

# Train the LDA model on the corpus
num_topics = 5
lda_model = gensim.models.ldamodel.LdaModel(corpus, num_topics=num_topics, id2word=dictionary)

# Print the topics and their top words
for topic in lda_model.show_topics():
    print(topic)

"""Considering above key words, we will assign repective banking department to those topics. 

So,
* Topic 0 = Bank Account Service
* Topic 1 = Theft/dispute reporting
* Topic 2 = Other
* Topic 3 = Loan Department
* Topic 4 = Customer Service
"""

topic_distributions = lda_model[corpus]

# Loop through the list of topic distributions and assign the corresponding topic to each sentence
topics = []
for i, doc in enumerate(topic_distributions):
    # Get the topic with the highest probability for this document
    topic_id = max(doc, key=lambda x: x[1])[0]
    # Append the topic ID to the list of topics
    topics.append(topic_id)

"""#Print the Top15 words for each of the topics

words = np.array(tfidf.get_feature_names())
topic_words = pd.DataFrame(np.zeros((no_topics,15)), index=[f'Topic {i + 1}' for i in range(no_topics)],
                           columns=[f'Word {i + 1}' for i in range(15)]).astype(str)
for i in range(no_topics):
    ix = H[i].argsort()[::-1][:15]
    topic_words.iloc[i] = words[ix]

topic_words
"""

#Create the best topic for each complaint in terms of integer value 0,1,2,3 & 4
#Assign the best topic to each of the cmplaints in Topic Column

# Create a new column in the com_txt dataset containing the topics
com_txt['Topic'] = topics

com_txt

#Print the first 10 Complaint for each of the Topics
com_txt_5=com_txt.groupby('Topic').head(10)
com_txt_5.sort_values('Topic')

# To select specific depetment for the topics we need to take advice from subject matter expert for that we will save last 2 columns
# Select the specific column using the loc function
col = com_txt_5.iloc[:,4:]

# Save the column as a CSV file
#col.to_csv('Top_10_Topic.csv', index=False)

"""After evaluating the mapping, if the topics assigned are correct then assign these names to the relevant topic:

* Topic 0 = Bank Account Service
* Topic 1 = Theft/dispute reporting
* Topic 2 = Other
* Topic 3 = Loan Department
* Topic 4 = Customer Service
"""

#Create the dictionary of Topic names and Topics
Topic_names = { 0:"Bank account services", 1:"Theft/dispute reporting", 2:"Others",
               3:"Loan Department", 4:"Customer Service" }
#Replace Topics with Topic Names
com_txt['Topic'] = com_txt['Topic'].map(Topic_names)

com_txt.shape

com_txt

# Now as training_data we will take, first raw data column from com_txt, and Topic column 

Training_data = com_txt[["consumer_complaint_narrative", "Topic"]]

Training_data

Training_data["Topic"].value_counts

#Replace Topics with Topic Names
Training_data.loc[0:,'Topic'] = Training_data['Topic'].map({"Bank account services":0, "Theft/dispute reporting":1, "Others":2,
               "Loan Department":3, "Customer Service":4})


#{ 0:"Bank account services", 1:"Theft/dispute reporting", 2:"Others",
#              3:"Loan Department", 4:"Customer Service" }


#Topic 0 = Bank Account Service
#Topic 1 = Theft/dispute reporting
#Topic 2 = Other
#Topic 3 = Loan Department
#Topic 4 = Customer Service

Training_data

Training_data['Topic'].value_counts()

Training_data['consumer_complaint_narrative']

"""# Now we have to perform Supervised model on Training data 
considering "consumer_complaint_narrative" as input and "Topic" as output 

we can use various Supervised learning model such as Descision tree, Logistic Regression etc

#Now we will use Tfidf Vectorizer
consider its input as X2 and output as Y2
"""

from sklearn.feature_extraction.text import TfidfVectorizer

# create a TfidfVectorizer object with both CountVectorizer and TfidfTransformer
tfidf = TfidfVectorizer()

# fit the vectorizer to your ticket descriptions
tfidf.fit(Training_data["consumer_complaint_narrative"])

# transform the ticket descriptions into a TF-IDF weighted document-term matrix
# We will asin it as X
X = tfidf.transform(Training_data["consumer_complaint_narrative"])

X

# Now lets eveluate model using Descision Tree Supervsed learning 
# Slpit data into Predictor(X) and Target (Y) 
Y = Training_data["Topic"]

Y = Y.astype('int64')

X, Y

from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X,Y, test_size = 0.2, random_state=8) #1, 3, 8,15

#check for imbalance
Y.value_counts() / len(Y) #Consider it as A

Y_train.value_counts() / len(Y_train) # Consider it as B

Y_test.value_counts() / len(Y_test) # Condiser it as C

"""Now untill you get all values in B and C equal to A, keep repeating the split function.

"""

#Decision Tree
from sklearn.tree import DecisionTreeClassifier as DT
model = DT(criterion = 'entropy')
model.fit(X_train, Y_train)

#Predicting test model and train model

test_pred = model.predict(X_test)

train_pred = model.predict(X_train)

#Checking accuracy score and confusion matrix of test model
from sklearn.metrics import accuracy_score, confusion_matrix

confusion_matrix(Y_test, test_pred)

print(accuracy_score(Y_test, test_pred))

#Checking confusion matrix and accuracy score for train data

confusion_matrix(Y_train, train_pred)

print(accuracy_score(Y_train, train_pred))

"""Here test moel is showing 66% accuray and train model is showing 100% accuracy so, it is clear that model is over fitting.
To overcome this issue we will perform hyper parameter tunning on decision tree
"""

# Applying GridSearch CV 
from sklearn.tree import DecisionTreeClassifier as DT
from sklearn.model_selection import GridSearchCV

model1 = DT(criterion = 'entropy')

param_grid = {'min_samples_leaf': np.arange(1, 20, 2),
             'max_depth': [3, 5, 10],
              "min_samples_leaf": np.arange(1, 20, 2),
             'max_features':['sqrt']}

grid_search = GridSearchCV(estimator = model1, param_grid = param_grid,
                          scoring = 'accuracy', n_jobs = -1, cv=5,
                          refit = True, return_train_score = True)

grid_search.fit(X_train, Y_train)
grid_search.best_params_
cv_grid = grid_search.best_estimator_

# Estimating test data accuracy according to above best parameters
confusion_matrix(Y_test, cv_grid.predict(X_test))

print(accuracy_score(Y_test, cv_grid.predict(X_test)))

confusion_matrix(Y_train, cv_grid.predict(X_train))

print(accuracy_score(Y_train, cv_grid.predict(X_train)))

# Applying Random Forest 

from sklearn.ensemble import RandomForestClassifier

RFC = RandomForestClassifier(n_estimators=100, n_jobs=1, random_state=40)

RFC.fit(X_train, Y_train)

# Evaluating confusion matrix and accuracy score of test data with Random Forest
confusion_matrix(Y_test, RFC.predict(X_test))

print(accuracy_score(Y_test, RFC.predict(X_test)))

#Evaluating same for train data
confusion_matrix(Y_train, RFC.predict(X_train))

print(accuracy_score(Y_train, RFC.predict(X_train)))

#Above models ae giving overfitting model so lets try Multinomial Naive Bayes 

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

# Now lets try Multinomial Naive Bayes technique
from sklearn.naive_bayes import MultinomialNB as MB

classifier_mb = MB(alpha = 0.25)
classifier_mb.fit(X_train, Y_train)

X_train_pred = classifier_mb.predict(X_train)

X_test_pred = classifier_mb.predict(X_test)

# Evaluation test data 
pd.crosstab(X_test_pred, Y_test)

print(accuracy_score(X_test_pred, Y_test))

pd.crosstab(X_train_pred, Y_train)

print(accuracy_score(X_train_pred, Y_train))


## Logistic regression ###
# Importing LogisticRegression from sklearn
from sklearn.linear_model import LogisticRegression
logreg = LogisticRegression(random_state=42, solver='liblinear').fit(X_train, Y_train)

Y_train_pred = logreg.predict(X_train)
Y_test_pred = logreg.predict(X_test)

# Calculate accuracy of the model
pd.crosstab(Y_test, Y_test_pred)
print(accuracy_score(Y_test, Y_test_pred))

pd.crosstab(Y_train, Y_train_pred)
print(accuracy_score(Y_train, Y_train_pred)) 

"""So comparing from above applied models, Mutinomial Naive Bayes is giving us 
best result i.e 83% percent and 87% accuracy for test and train data respectivly which is acceptable.
"""

####### Deployment #######
from sklearn.pipeline import Pipeline

pipeline = Pipeline([                
                ('tfidf', TfidfVectorizer(sublinear_tf= True, min_df=10, norm='l2', ngram_range=(1, 2), stop_words='english')),
                ('logreg', LogisticRegression()),
               ])

'''
Now while creating pipeline we can't use pre processed train and tet data so we will again take raw data
from Training_data set and divide it in to X1(Input data) and Y1 (Output data)

'''
print(Training_data.head(5))

X1 =Training_data["consumer_complaint_narrative"]
Y1 = Training_data["Topic"]
Y1 = Y1.astype('int64')

#Replace Topics with Topic Names
Topic_names = { 0:"Bank account services", 1:"Theft/dispute reporting", 2:"Others",
               3:"Loan Department", 4:"Customer Service" }
#Replace Topics with Topic Names
Y1 = Y1.map(Topic_names)
Y1.head(5)

X_train1, X_test1, Y_train1, Y_test1 = train_test_split(X1,Y1, test_size = 0.2, random_state=8)

load_pipe = pipeline.fit(X_train1, Y_train1)
load_pipe

y_pred1 = load_pipe.predict(X_test1)
y_pred1

from sklearn import metrics
metrics.accuracy_score(y_pred1, Y_test1)

import pickle 
pickle.dump(pipeline, open('pipeline.pkl','wb'))

import os
os.getcwd()


#Link after deployment is complete
#http://127.0.0.1:5000/
#################################################################################
