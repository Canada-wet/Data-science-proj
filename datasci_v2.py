# -*- coding: utf-8 -*-
"""DataSci-V2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mkXaxztKt-sOwPR561TTuBTb7vRYP2As
"""

# code for data science project #1
# arthur: Zhongheng Shen, Tianyu Ren, Hongyi Wu
# Oct, 2019
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
import copy
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
import seaborn as sns

data = pd.read_csv("project_data_2.csv")

"""## data cleaning: Hongyi Wu"""

# use the trader column as index
# then delete trader column
data.index = data.iloc[:, 0]
del data["Trader ID #"]

# convert all abnormal cells to NaN
def dataclean(x):
    
    try:
        x = float(x)
        if abs(x)<2: # return should be less than 1
            return x
        else:
            return np.nan
    except:
        return np.nan

data = data.applymap(dataclean)

# normalize by asset to remove market's effect 
def normalize(col):
    mean = np.mean(col[~col.isna()])
    std = np.std(col[~col.isna()])
    return (col - mean) / std

data_norm = data.apply(normalize)

asset=[1,2,3,4,5]
def meanFill(data):
  for i in asset:
    A = [True if 'A'+str(i) in x else False for x in data.columns]
    data[data.columns[A]] = data[data.columns[A]].T.apply(lambda x:x.fillna(np.mean(x))).T
  return data
  
data_norm = meanFill(data_norm)

data_norm

"""## compute volatility : Zhongheng Shen

> 缩进块
"""

# generate new features, calculate vol of five assets
def asset_volatility(asset_type):
    A = [True if asset_type in x else False for x in data_norm.columns]
    data_norm_A = data_norm[data_norm.columns[A]]
    A_vol_list = []
    for i in range(0, len(data_norm_A)):
        A_vol_list.append(np.std(data_norm_A.iloc[i, :]))
    return A_vol_list

A1_vol_list = asset_volatility("A1")
A2_vol_list = asset_volatility("A2")
A3_vol_list = asset_volatility("A3")
A4_vol_list = asset_volatility("A4")
A5_vol_list = asset_volatility("A5")

vol_df = pd.DataFrame([A1_vol_list, A2_vol_list, A3_vol_list, A4_vol_list, A5_vol_list]).T

vol_df

"""## compute stats of volatility"""

vol_df['max1'] = vol_df.iloc[:, 0:5].max(axis=1)
vol_df["min"] = vol_df.iloc[:, 0:5].min(axis=1)
#vol_df['max2'] = vol_df.iloc[:, 0:5].T.apply(lambda x: x.nlargest(2))
def get_second_largest(x):
  return sorted(x)[-2]
vol_df['max2'] = vol_df.iloc[:, 0:5].apply(lambda row: get_second_largest(row), axis = 1)
vol_df['average'] = vol_df.iloc[:, 0:5].mean(axis=1)

vol_df

"""## isolation tree part1: Zhongheng Shen"""

scaler = StandardScaler()
#np_scaled = scaler.fit_transform(vol_df)
#data_vol_scaled = pd.DataFrame
# train isolation forest
outliers_fraction = 0.1
model = IsolationForest(contamination=outliers_fraction)
model.fit(vol_df.iloc[:,0:5]) 
vol_df['anomaly2'] = pd.Series(model.predict(vol_df.iloc[:,0:5]))
#vol_df['iso_score'] = pd.Series(model.score_samples(vol_df.iloc[:, 0:5]))

vol_df

"""## isolation tree part2"""

good = vol_df[vol_df['anomaly2']==1].index
bad = vol_df[vol_df['anomaly2']==-1].index

# vol_df.loc[bad].iloc[:,0:2].plot.scatter(0,1)
# vol_df.loc[good].iloc[:,0:2].plot.scatter(0,1)
# fig = plt.figure()
# ax = fig.add_subplot(111)
# ax.scatter(vol_df.loc[bad].iloc[:,0], vol_df.loc[bad].iloc[:,1], c='#74787a')
# ax.scatter(vol_df.loc[good].iloc[:,0], vol_df.loc[good].iloc[:,1],c='#f26b1f')

#vol_df[vol_df['anomaly2'] == -1]['iso_score']

fig = plt.figure()
ax = fig.add_subplot(111, projection = "3d")
max1 = vol_df['max1']
max2 = vol_df['max2']
min1 = vol_df['min']
c = vol_df['anomaly2']
min1_good, max1_good, max2_good = min1[c==1], max1[c==1], max2[c==1]
min1_bad, max1_bad, max2_bad = min1[c==-1], max1[c==-1], max2[c==-1]
ax.scatter(min1_good, max1_good, max2_good, c='#74787a')
ax.scatter(min1_bad, max1_bad, max2_bad, c='#f26b1f')
ax.set_xlabel("Volmax1")
ax.set_ylabel("volmax2")
ax.set_zlabel("volmin")
ax.set_title("Clustering Visualization")
plt.savefig("Isolation Tree")

fig, ax = plt.subplots(figsize=(10,6))
a = vol_df.loc[vol_df['anomaly2'] == -1, ['max1']] #anomaly
ax.plot(vol_df.index, vol_df['max1'], color='#74787a')
ax.scatter(a.index,a['max1'], color='#f26b1f')

result_df = vol_df.iloc[:,-6:]

result_df['gap'] = result_df['max1'] - result_df['min']

result_df

# a = result_df.loc[result_df['anomaly2'] == 1, 'max1']
# b = result_df.loc[result_df['anomaly2'] == -1, 'max1']
# plt.figure(figsize=(10, 6))
# plt.hist(a, bins = 80, alpha=0.5, label='Good Trader')
# plt.hist(b, bins = 80, alpha=0.5, label='Bad Trader')
# plt.legend(loc='upper right')
# plt.xlabel('Max - Min')
# plt.ylabel('Count')
# plt.show();


a = vol_df.loc[result_df['anomaly2'] == 1].iloc[:,2]
b = vol_df.loc[result_df['anomaly2'] == -1].iloc[:,2]

# # plt.figure(figsize=(10, 6))
# # plt.hist(a, bins = 80, alpha=0.5, label='Good Trader')
# # plt.hist(b, bins = 80, alpha=0.5, label='Bad Trader')
# # plt.legend(loc='upper right')
# # plt.xlabel('Maximum Volatility')
# # plt.ylabel('Count')
# # plt.show();
sns.set(rc={'figure.figsize':(10,6)})
sns.distplot(a,hist=True, kde=True,bins=30, color = '#74787a', hist_kws={'edgecolor':'black'},kde_kws={'linewidth': 2})
sns.distplot(b,hist=True, kde=True,bins=30, color = '#f26b1f', hist_kws={'edgecolor':'black'},kde_kws={'linewidth': 2})

a = result_df.loc[result_df['anomaly2'] == 1, 'min']
b = result_df.loc[result_df['anomaly2'] == -1, 'min']
sns.set(rc={'figure.figsize':(10,6)})
sns.distplot(a,hist=True, kde=True,bins=50, color = '#74787a', hist_kws={'edgecolor':'black'},kde_kws={'linewidth': 2})
sns.distplot(b,hist=True, kde=True,bins=50, color = '#f26b1f', hist_kws={'edgecolor':'black'},kde_kws={'linewidth': 2})
# plt.figure(figsize=(10, 6))
# plt.hist(a, bins = 50, alpha=0.5, label='Good Trader')
# plt.hist(b, bins = 50, alpha=0.5, label='Bad Trader')
# plt.legend(loc='upper right')
# plt.xlabel('Minimum Volatility')
# plt.ylabel('Count')
# plt.show();

"""##SVM part1"""

scaler = StandardScaler()
np_scaled = scaler.fit_transform(vol_df.iloc[:, 0:5])
data_svm = pd.DataFrame(np_scaled)
# train oneclassSVM
outliers_fraction = 0.1
model = OneClassSVM(nu=outliers_fraction, kernel="rbf", gamma=0.01)
model.fit(data_svm)
vol_df['anomaly3'] = pd.Series(model.predict(data_svm))
fig, ax = plt.subplots(figsize=(10,6))
a = vol_df.loc[vol_df['anomaly3'] == -1, ['max1']] #anomaly
ax.plot(vol_df.index, vol_df['max1'], color='#74787a')
ax.scatter(a.index,a['max1'], color='#f26b1f')
plt.show();

vol_df

vol_df['project_1_flag'] = 0
vol_df['project_1_flag'].loc[(vol_df['anomaly2'] == -1) & (vol_df['anomaly3'] == -1)] = 1

vol_df

sum(vol_df['project_1_flag'] == 1)

fig, ax = plt.subplots(figsize=(10,6))
ax.scatter(vol_df[vol_df['project_1_flag'] == 1].index,vol_df[vol_df['project_1_flag'] == 1]['max1'], color='#f26b1f')
ax.scatter(vol_df[vol_df['project_1_flag'] == 0].index,vol_df[vol_df['project_1_flag'] == 0]['max1'])

"""## SVM part2"""

result_df_svm = vol_df[['max1', 'min', 'max2', 'anomaly3', 'average']]
result_df_svm['gap'] = result_df_svm['max1'] - result_df_svm['min']
result_df_svm

a = result_df_svm.loc[result_df_svm['anomaly3'] == 1, 'max1']
b = result_df_svm.loc[result_df_svm['anomaly3'] == -1, 'max1']
# plt.figure(figsize=(10, 6))
# plt.hist(a, bins = 100, alpha=0.5, label='Good Trader')
# plt.hist(b, bins = 100, alpha=0.5, label='Bad Trader')
# plt.legend(loc='upper right')
# plt.xlabel('Maximum Volatility')
# plt.ylabel('Count')
# plt.show();
sns.set(rc={'figure.figsize':(10,6)})
sns.distplot(a,hist=True, kde=True,bins=50, color = '#74787a', hist_kws={'edgecolor':'black'},kde_kws={'linewidth': 2})
sns.distplot(b,hist=True, kde=True,bins=50, color = '#f26b1f', hist_kws={'edgecolor':'black'},kde_kws={'linewidth': 2})
plt.legend(labels=['good trader', 'bad trader'])

"""## generate bad trader samples by using bootstrapping"""

# intersect_bad_trader = [x -1 for x in [48, 256, 579, 607, 608, 618, 629, 638, 644, 648, 649]]
# vol_df.loc[intersect_bad_trader]
# #model.decision_function(test_x)

# del vol_df['anomaly3']

vol_df.index = vol_df.index+1 #Match the index with trader ID

# get intersection between benchmark and the results of our model
# anomaly2 is label from islation tree model
# anamaly3 is label from oneclassSVM model
vol_df['Flagged'] = data['Flagged?']
vol_df['Flagged'].loc[vol_df['Flagged']==1] = -1
vol_df['Flagged'].loc[vol_df['Flagged']==0] = 1
TP = list(vol_df.loc[(vol_df['Flagged']== -1) & ((vol_df['anomaly2'] == -1) | (vol_df['anomaly3'] == -1))].index)
TN = list(vol_df.loc[(vol_df['Flagged']== 1) & ((vol_df['anomaly2'] == 1) | (vol_df['anomaly3'] == 1))].index)

# boostrap bad traders to mitigate overfitting
# first using bad trader features to generate dummy traders
samplePool = vol_df.loc[TP].iloc[:,0:5]
randomvol1 = list(np.random.choice(samplePool.iloc[:,0],4000))
randomvol2 = list(np.random.choice(samplePool.iloc[:,1],4000))
randomvol3 = list(np.random.choice(samplePool.iloc[:,2],4000))
randomvol4 = list(np.random.choice(samplePool.iloc[:,3],4000))
randomvol5 = list(np.random.choice(samplePool.iloc[:,4],4000))

randomBadTrader = pd.DataFrame([randomvol1,randomvol2,randomvol3,randomvol4,randomvol5]).T
randomBadTrader.columns = ['Vol1','Vol2','Vol3','Vol4','Vol5']
randomBadTrader

# use our oneclassSVM model to select bad traders from bootstrapping generated data
randomBadTrader['model_flag'] = model.decision_function(randomBadTrader.iloc[:, 0:5])

bad_trader_gen = randomBadTrader[randomBadTrader['model_flag'] < 0]
del bad_trader_gen['model_flag']
bad_trader_gen.columns = ['Vol1','Vol2','Vol3','Vol4','Vol5']

bad_trader_gen.drop_duplicates(inplace = True)

bad_trader_gen['Flagged'] = 1

# get good traders' features and labels
vol_TN = vol_df.loc[TN].iloc[:,0:5]
vol_TN.columns = ['Vol1','Vol2','Vol3','Vol4','Vol5']
vol_TN['Flagged'] = vol_df['Flagged'].loc[TN]
vol_TN['Flagged'] = vol_TN['Flagged']-1
vol_TN

# get bad traders' features and labels
vol_TP = vol_df.loc[TP].iloc[:,0:5]
vol_TP.columns = ['Vol1','Vol2','Vol3','Vol4','Vol5']
vol_TP['Flagged'] = vol_df['Flagged'].loc[TP]+2
vol_TP

# put real bad traders, real good traders and generated bad traders together
# get our training data
sampleTrader = pd.concat([vol_TN,bad_trader_gen])
sampleTrader = pd.concat([vol_TP,sampleTrader])
sampleTrader.reset_index(inplace=True)
sampleTrader.drop(['index'],axis=1,inplace=True)
sampleTrader

"""## XGBoost"""

# # Xgboost
# xg_reg = xgb.XGBRegressor(objective="binary:logistic", colsample_bytree=0.8, learning_rate=0.05, \
#  max_depth=5, alpha=10, n_estamator=10, subsample=0.8, min_child_weight = 1, gamma = 0, seed=3)

# xg_reg.fit(X_train, y_train)
# preds = xg_reg.predict(X_test)
# preds[preds > 0.5] = 1
# preds[preds <= 0.5] = 0
# acc = np.sum(preds == y_test) / y_test.shape[0]
# print("Accuracy: %f" % (acc))

# get data of intersected bad traders and good traders
vol_df['True Label'] = 0
vol_df['True Label'].loc[TP]=1
real_TP = vol_df.loc[TP]
real_TN = vol_df.loc[TN]
real_test = pd.concat([real_TP,real_TN])
real_data = real_test.iloc[:,0:5]
real_data['Flagged'] = real_test['True Label']
real_data.reset_index(inplace = True)
real_data

from xgboost import XGBClassifier
import xgboost as xgb
from sklearn import metrics
from sklearn.model_selection import train_test_split
#model = XGBClassifier()

# fit the model with the training data
# train = sampleTrader.iloc[:,0:5]

# model.fit(train,sampleTrader['Flagged'])
 
 
# # predict the target on the train dataset
X_train = sampleTrader.iloc[:,0:5]
y_train = sampleTrader.iloc[:,5]
X_train.columns = ['Vol1','Vol2','Vol3','Vol4','Vol5']

X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.2, random_state=0)

# Train and test Xgboost
xg_reg = xgb.XGBRegressor(objective="binary:logistic", colsample_bytree=0.8, learning_rate=0.05, \
 max_depth=5, alpha=10, n_estamator=10, subsample=0.8, min_child_weight = 1, gamma = 0, seed=3)

xg_reg.fit(X_train, y_train)
# X_test = vol_df.iloc[:,0:5]
# X_test.columns = ['Vol1','Vol2','Vol3','Vol4','Vol5']
# y_test = vol_df['True Label']
preds = xg_reg.predict(X_test)
preds[preds > 0.5] = 1
preds[preds <= 0.5] = 0



acc = np.sum(preds == y_test) / y_test.shape[0]
print("Accuracy: %f" % (acc))
# predict_train.sum()
cm = metrics.confusion_matrix(y_test, preds)
print(cm)
plt.figure(figsize=(9,9))
sns.heatmap(cm, annot=True, fmt=".3f", linewidths=.5, square = True, cmap = 'Blues_r');
plt.ylabel('Actual label');
plt.xlabel('Predicted label');
all_sample_title = 'Accuracy Score: {0}'.format(acc)
plt.title(all_sample_title, size = 15);

Unkown_index = vol_df.index.isin(TN+TP)
Unkown_index
volUnknown = vol_df[~Unkown_index]
volUnknown = volUnknown.iloc[:,0:5]

volUnknown

#classify unknown traders
volUnknown.columns = ['Vol1','Vol2','Vol3','Vol4','Vol5']
preds = xg_reg.predict(volUnknown)
preds[preds > 0.5] = 1
preds[preds <= 0.5] = 0
volUnknown['Flagged'] = preds

#sum(volUnknown['Flagged'])
volUnknown
new_classification = pd.concat([vol_TN,vol_TP,volUnknown])
new_classification.sort_index(inplace=True)
new_classification

fig, ax = plt.subplots(figsize=(10,6))
a = new_classification.loc[new_classification['Flagged'] == 1, ['Vol1']] #anomaly
ax.plot(new_classification.index, new_classification['Vol1'], color='#74787a')
ax.scatter(a.index,a['Vol1'], color='#f26b1f')

new_classification['max1'] = new_classification.iloc[:, 0:5].max(axis=1)

fig, ax = plt.subplots(figsize=(10,6))
ax.scatter(new_classification[new_classification['Flagged'] == 1].index,new_classification[new_classification['Flagged'] == 1]['max1'], color='#f26b1f')
ax.scatter(new_classification[new_classification['Flagged'] == 0].index,new_classification[new_classification['Flagged'] == 0]['max1'])

sum(new_classification['Flagged'])

#test on agreed good traders and bad traders
X_test = real_data.iloc[:,0:5]
X_test.columns = ['Vol1','Vol2','Vol3','Vol4','Vol5']
y_test = real_data.iloc[:,-1]
preds = xg_reg.predict(X_test)
preds[preds > 0.5] = 1
preds[preds <= 0.5] = 0

acc = np.sum(preds == y_test) / y_test.shape[0]
print("Accuracy: %f" % (acc))
# predict_train.sum()
cm = metrics.confusion_matrix(y_test, preds)
print(cm)
plt.figure(figsize=(9,9))
sns.heatmap(cm, annot=True, fmt=".3f", linewidths=.5, square = True, cmap = 'Blues_r');
plt.ylabel('Actual label');
plt.xlabel('Predicted label');
# all_sample_title = 'Accuracy Score: {0}'.format(preds)
plt.title(all_sample_title, size = 15);

vol_df['BenchmarkFlag'] = data['Flagged?']

#test on benchmark
X_test = vol_df.iloc[:,0:5]
X_test.columns = ['Vol1','Vol2','Vol3','Vol4','Vol5']
y_test = vol_df.iloc[:,-1]
preds = xg_reg.predict(X_test)
preds[preds > 0.5] = 1
preds[preds <= 0.5] = 0

acc = np.sum(preds == y_test) / y_test.shape[0]
print("Accuracy: %f" % (acc))
# predict_train.sum()
cm = metrics.confusion_matrix(y_test, preds)
print(cm)
plt.figure(figsize=(9,9))
sns.heatmap(cm, annot=True, fmt=".3f", linewidths=.5, square = True, cmap = 'Blues_r');
plt.ylabel('Actual label');
plt.xlabel('Predicted label');
# all_sample_title = 'Accuracy Score: {0}'.format(preds)
plt.title(all_sample_title, size = 15);

vol_df.head()

X_train = sampleTrader.iloc[:,0:5]
y_train = sampleTrader.iloc[:,5]


X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.2, random_state=0)

from sklearn.linear_model import LogisticRegression

clf = LogisticRegression(random_state=0).fit(X_train, y_train)
y_test = vol_df['BenchmarkFlag']
X_test = vol_df.iloc[:,0:5]
preds = clf.predict(X_test)
acc = clf.score(X_test, y_test)
print("Accuracy: %f" % (acc))

# predict_train.sum()
cm = metrics.confusion_matrix(y_test, preds)
print(cm)
plt.figure(figsize=(9,9))
sns.heatmap(cm, annot=True, fmt=".3f", linewidths=.5, square = True, cmap = 'Blues_r');
plt.ylabel('Actual label');
plt.xlabel('Predicted label');
# all_sample_title = 'Accuracy Score: {0}'.format(preds)
plt.title(all_sample_title, size = 15);

"""## Logistic Regression"""

from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(random_state=0, solver='lbfgs').fit(X_train, y_train)
preds = clf.predict(X_test)
acc = clf.score(X_test, y_test)
print("Accuracy: %f" % (acc))

# predict_train.sum()
cm = metrics.confusion_matrix(y_test, preds)
print(cm)
plt.figure(figsize=(9,9))
sns.heatmap(cm, annot=True, fmt=".3f", linewidths=.5, square = True, cmap = 'Blues_r');
plt.ylabel('Actual label');
plt.xlabel('Predicted label');
# all_sample_title = 'Accuracy Score: {0}'.format(preds)
plt.title(all_sample_title, size = 15);

from sklearn.linear_model import LogisticRegression
X_test = vol_df.iloc[:,0:5]
X_test.columns = ['Vol1','Vol2','Vol3','Vol4','Vol5']
y_test = vol_df.iloc[:,-1]

preds = clf.predict(X_test)
acc = clf.score(X_test, y_test)
print("Accuracy: %f" % (acc))

# predict_train.sum()
cm = metrics.confusion_matrix(y_test, preds)
print(cm)
plt.figure(figsize=(9,9))
sns.heatmap(cm, annot=True, fmt=".3f", linewidths=.5, square = True, cmap = 'Blues_r');
plt.ylabel('Actual label');
plt.xlabel('Predicted label');
# all_sample_title = 'Accuracy Score: {0}'.format(preds)
plt.title(all_sample_title, size = 15);

model = XGBClassifier()
model.fit(X_test, y_test)
# plot feature importance
xgb.plot_importance(model)

"""ROC"""

from sklearn.metrics import roc_curve, auc

#XGBoost
X_test = real_data.iloc[:,0:5]
X_test.columns = ['Vol1','Vol2','Vol3','Vol4','Vol5']
y_test = real_data.iloc[:,-1]
preds1 = xg_reg.predict(X_test)


# preds1[preds1 > 0.5] = 1
# preds1[preds1 <= 0.5] = 0

plt.figure(figsize = (8, 6))
plt.plot([0,1], [0,1], 'r--')


fpr1, tpr1, thresholds1 = roc_curve(y_test, preds1)
roc_auc1 = auc(fpr1, tpr1)



#LogisticRegression
from sklearn.linear_model import LogisticRegression


preds2 = clf.predict_proba(X_test)
preds2=preds2[:,0]

fpr2, tpr2, thresholds2 = roc_curve(y_test, preds2)
roc_auc2 = auc(fpr2, tpr2)

label = 'XGBoost AUC:' + ' {0:.2f}'.format(roc_auc1)
plt.plot(fpr1, tpr1, c = 'g', label = label, linewidth = 2)
plt.xlabel('False Positive Rate', fontsize = 10)
plt.ylabel('True Positive Rate', fontsize = 10)
plt.title('Receiver Operating Characteristic', fontsize = 10)
plt.legend(loc = 'lower right', fontsize = 10)

# label = 'LogisticRegression AUC:' + ' {0:.2f}'.format(roc_auc2)
# plt.plot(fpr2, tpr2, c = 'b', label = label, linewidth = 2)
# plt.xlabel('False Positive Rate', fontsize = 10)
# plt.ylabel('True Positive Rate', fontsize = 10)
# plt.title('Receiver Operating Characteristic', fontsize = 10)
# plt.legend(loc = 'lower right', fontsize = 10)

preds2[:,1]

from xgboost import XGBClassifier
import xgboost as xgb
from sklearn import metrics
from sklearn.model_selection import train_test_split
#model = XGBClassifier()

# fit the model with the training data
# train = sampleTrader.iloc[:,0:5]

# model.fit(train,sampleTrader['Flagged'])
 
 
# # predict the target on the train dataset
X_train = sampleTrader.iloc[:,0:5]
y_train = sampleTrader.iloc[:,5]
X_train.columns = ['Vol1','Vol2','Vol3','Vol4','Vol5']

X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.2, random_state=0)

# Train and test Xgboost
xg_reg = xgb.XGBRegressor(objective="binary:logistic", colsample_bytree=0.8, learning_rate=0.05, \
 max_depth=5, alpha=10, n_estamator=10, subsample=0.8, min_child_weight = 1, gamma = 0, seed=3)

xg_reg.fit(X_train, y_train)
# X_test = vol_df.iloc[:,0:5]
# X_test.columns = ['Vol1','Vol2','Vol3','Vol4','Vol5']
# y_test = vol_df['True Label']
preds1 = xg_reg.predict(X_test)


plt.figure(figsize = (8, 6))
plt.plot([0,1], [0,1], 'r--')


fpr1, tpr1, thresholds1 = roc_curve(y_test, preds1)
roc_auc1 = auc(fpr1, tpr1)



#LogisticRegression
from sklearn.linear_model import LogisticRegression
clf = LogisticRegression(random_state=0, solver='lbfgs').fit(X_train, y_train)

preds2 = clf.predict_proba(X_test)
preds2=preds2[:,1]

fpr2, tpr2, thresholds2 = roc_curve(y_test, preds2)
roc_auc2 = auc(fpr2, tpr2)

label = 'XGBoost AUC:' + ' {0:.2f}'.format(roc_auc1)
plt.plot(fpr1, tpr1, c = 'g', label = label, linewidth = 2)
plt.xlabel('False Positive Rate', fontsize = 10)
plt.ylabel('True Positive Rate', fontsize = 10)
plt.title('Receiver Operating Characteristic', fontsize = 10)
plt.legend(loc = 'lower right', fontsize = 10)

label = 'LogisticRegression AUC:' + ' {0:.2f}'.format(roc_auc2)
plt.plot(fpr2, tpr2, c = 'b', label = label, linewidth = 2)
plt.xlabel('False Positive Rate', fontsize = 10)
plt.ylabel('True Positive Rate', fontsize = 10)
plt.title('Receiver Operating Characteristic', fontsize = 10)
plt.legend(loc = 'lower right', fontsize = 10)

preds1



