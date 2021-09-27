# -*- coding: utf-8 -*-
"""Final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1d5_d29UnTUh-1vP-qAESPXL07ssQ5dEE
"""

from google.colab import files
files.upload()

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline

import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv('All_good_data(lemmatization).csv')

df['HypРекомендация'] = 0
df['HypЗапрос'] = 0
df['HypПланировать'] = 0
df['HypФото'] = 0
df['HypГод'] = 0
df['HypРемонт'] = 0
df['HypРабота'] = 0
df['HypРассмотреть'] = 0
df['HypВыезд'] = 0

for i in range(0, len(df)):

  t = []
  for word in str.split(df['responsibleperson_msg'][i],' '):
    if (len(word) > 2 ) and (word[2] != '\''):

        start = 0
        end = -1

        while (word[start] == '\'' or word[start] == '['):
          start += 1
        while (word[end - 1] == '\'' or word[end - 1] == ']'):
          end -= 1

        t.append(word[start:end])

    if (word[2] == '\'') and (len(word) > 4):

      for more_words in str.split(word, ' '):

        start = 0
        end = -1

        while (more_words[start] == '\'' or more_words[start] == '['):
          start += 1
        while (more_words[end - 1] == '\'' or more_words[end - 1] == ']'):
          end -= 1

        t.append(more_words[start:end])

  #start hypothesises
  df['HypФото'][i] = int(df['is_photo_answer'][i])
  
  for word in t:

    if word == 'выезд':
      df['HypВыезд'][i] = 1

    if word == 'год':
      df['HypГод'][i] = 1

    if (word == 'запрос'):
      df['HypЗапрос'][i] = 1

    if (word == 'рассмотреть') or ( word == 'рассмотрение'):
      df['HypРассмотреть'][i] = 1

    if (word == 'план') or (word == 'планировать') or (word == 'запланировать') or (word == 'планироваться') or (word == 'плановый'):
      df['HypПланировать'][i] = 1

    if (word == 'рекомендация'):
      df['HypРекомендация'][i] = 1

    if (word == 'работа'):
      df['HypРабота'][i] = 1

    if (word == 'ремонт'):
      df['HypРемонт'][i] = 1

del df['Unnamed: 0']
del df['Unnamed: 0.1']

values = {'moderateperson_msg': 'NS', 'privateperson_msg': 'NS', 'moderateperson_name': 'NS', 'days_to_solve': df['days_to_solve'].mode()[0]}
df  = df.fillna(values)

!pip install navec

!wget https://storage.yandexcloud.net/natasha-navec/packs/navec_hudlit_v1_12B_500K_300d_100q.tar

from navec import Navec

path = './navec_hudlit_v1_12B_500K_300d_100q.tar'
navec = Navec.load(path)

to_preprocess = list(['description','name', 'executor', 'responsibleperson_msg',	'moderateperson_msg',	'privateperson_msg'	,'responsibleperson_name'	,'moderateperson_name'])

vector = [[0 for column in to_preprocess] for i in range(0, len(df))]

for column in range(0, len(to_preprocess)):
  for i in range(0, len(df)):

    t = []
    for word in str.split(df[to_preprocess[column]][i],' '):
      if (len(word) > 2 ) and (word[2] != '\''):
        if (word[2:-2] in navec):
          t.append(navec[word[2:-2]])
    vector[i][column] = t

concat_embed = [[[] for column in to_preprocess] for i in range(0, len(df))]

for j in range(0, len(to_preprocess)):

  m_len = 0
  for i in range(0, len(df)):
    
    concat_embed[i][j] = np.zeros(300)
    if (len(vector[i][j]) > 0):
      for k in range(0, len(vector[i][j])):
        concat_embed[i][j] = concat_embed[i][j] +  vector[i][j][k]

embeddings = pd.DataFrame(concat_embed, columns=to_preprocess)

embeddings = embeddings.merge(df[{'is_photo_request', 'is_photo_answer', 'days_to_solve', 'status', 'HypРекомендация','HypЗапрос', 'HypПланировать', 'HypФото', 'HypГод', 'HypРемонт', 'HypРабота', 'HypРассмотреть','HypВыезд' }], how = 'right', left_index=True, right_index=True)

embeddings['target'] = 1



for i in range(0, len(embeddings)):
  if (embeddings['status'][i] == 'revise'):
    embeddings['target'][i] = 0

features = ['description', 'name', 'executor', 'responsibleperson_msg',
       'moderateperson_msg', 'privateperson_msg', 'responsibleperson_name',
       'moderateperson_name', 'is_photo_request', 'is_photo_answer', 'days_to_solve', 'HypРекомендация','HypЗапрос', 'HypПланировать', 'HypФото', 'HypГод', 'HypРемонт', 'HypРабота', 'HypРассмотреть','HypВыезд']
target = 'target'

X = pd.DataFrame()
for j in range(0, len(features) - 12):
    for k in range(0, 300):
      X[features[j] + '_' + str(k)] =0

Y = embeddings[target]

for i in range(0, len(embeddings)):
  print(i)
  row = {features[j] + '_' + str(k) : embeddings[features[j]][i][k] for k in range(0, 300) for j in range(0, len(features) - 12)}
  row['days_to_solve'] = df['days_to_solve'][i]
  row['is_photo_request'] = df['is_photo_request'][i]
  row['is_photo_answer'] = df['is_photo_answer'][i]
  row['HypРекомендация'] = df['HypРекомендация'][i]
  row['HypЗапрос'] = df['HypЗапрос'][i]
  row['HypПланировать'] = df['HypПланировать'][i]
  row['HypФото'] = df['HypФото'][i]
  row['HypГод'] = df['HypГод'][i]
  row['HypРемонт'] = df['HypРемонт'][i]
  row['HypРабота'] = df['HypРабота'][i]
  row['HypРассмотреть'] = df['HypРассмотреть'][i]
  row['HypВыезд'] = df['HypВыезд'][i]
  X = X.append(row, ignore_index= True)

from sklearn.naive_bayes import GaussianNB

classifier = GaussianNB()

files.upload()

old_df = pd.read_excel('Razmetka_ready.xlsx')

X_train = old_df[['is_photo_answer']]

X_train['HypРекомендация'] = 0
X_train['HypЗапрос'] = 0
X_train['HypПланировать'] = 0
X_train['HypФото'] = 0
X_train['HypГод'] = 0
X_train['HypРемонт'] = 0
X_train['HypРабота'] = 0
X_train['HypРассмотреть'] = 0
X_train['HypВыезд'] = 0

for i in range(0, len(X_train)):

  t = []
  for word in str.split(old_df['responsibleperson_msg'][i],' '):
    if (len(word) > 2 ) and (word[2] != '\''):

        start = 0
        end = -1

        while (word[start] == '\'' or word[start] == '['):
          start += 1
        while (word[end - 1] == '\'' or word[end - 1] == ']'):
          end -= 1

        t.append(word[start:end])

    if (word[2] == '\'') and (len(word) > 4):

      for more_words in str.split(word, ' '):

        start = 0
        end = -1

        while (more_words[start] == '\'' or more_words[start] == '['):
          start += 1
        while (more_words[end - 1] == '\'' or more_words[end - 1] == ']'):
          end -= 1

        t.append(more_words[start:end])

  print(t)
  #start hypothesises
  X_train['HypФото'][i] = int(X_train['is_photo_answer'][i])
  
  for word in t:

    if word == 'выезд':
      X_train['HypВыезд'][i] = 1

    if word == 'год':
      X_train['HypГод'][i] = 1

    if (word == 'запрос'):
      X_train['HypЗапрос'][i] = 1

    if (word == 'рассмотреть') or ( word == 'рассмотрение'):
      X_train['HypРассмотреть'][i] = 1

    if (word == 'план') or (word == 'планировать') or (word == 'запланировать') or (word == 'планироваться') or (word == 'плановый'):
      X_train['HypПланировать'][i] = 1

    if (word == 'рекомендация'):
      X_train['HypРекомендация'][i] = 1

    if (word == 'работа'):
      X_train['HypРабота'][i] = 1

    if (word == 'ремонт'):
      X_train['HypРемонт'][i] = 1

old_df['Lie'].value_counts()

X_train

classifier.fit(X_train[0:60], old_df['Lie'][0:60])

from sklearn.metrics import accuracy_score, f1_score
print('Testing accuracy %s' % accuracy_score(old_df['Lie'][60:-1], classifier.predict(X_train[60:-1])))
print('Testing F1 score: {}'.format(f1_score(old_df['Lie'][60:-1], classifier.predict(X_train[60:-1]), average='weighted')))

df['Result'] = 0

df['Result'] = classifier.predict(df[['is_photo_answer', 'HypРекомендация', 'HypЗапрос', 'HypПланировать', 'HypФото', 'HypГод', 'HypРемонт', 'HypРабота', 'HypРассмотреть','HypВыезд']])

df.to_csv('Final.csv')
df.to_excel('Final.xlsx')
files.download('Final.csv')
files.download('Final.xlsx')

true = old_df[old_df['target'] == 1][0:90]
false = old_df[old_df['target'] == 0][0:10]

test = true.append(false)