# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 14:10:25 2022

@author: engantchou
"""
import streamlit         as st 
import numpy             as np 
import pandas            as pd 
# import opendatasets      as od
import seaborn           as sns
import matplotlib.pyplot as plt
import plotly.express    as px
import joblib



from sklearn.preprocessing     import LabelEncoder
from sklearn.ensemble          import RandomForestClassifier
from sklearn.linear_model      import SGDClassifier
from sklearn.linear_model      import LogisticRegression
from xgboost                   import XGBClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.preprocessing     import RobustScaler
from imblearn.over_sampling    import SMOTE 
from sklearn.model_selection   import train_test_split, GridSearchCV
from collections               import Counter
from sklearn.pipeline          import Pipeline
from sklearn.metrics           import precision_score, accuracy_score
from sklearn.metrics           import precision_score, accuracy_score, recall_score, f1_score
from joblib                    import dump, load
from PIL                       import  Image

def load_data():
    # J'importe les données 
    data = pd.read_csv("PS_20174392719_1491204439457_log.csv" , encoding = "ISO-8859-1" , sep = ",", nrows=200000)
    df = data
    df.isnull().sum()
    df['isFraud'].value_counts(normalize=True)
    df['isFlaggedFraud'].value_counts(normalize=True)
    return df

def encode_df (df):
    colName = []
    for i in df.columns:
        if (df[i].dtypes == 'object'):
            colName.append(i)
    # Encode Categorical Columns
    le = LabelEncoder()
    df[colName] = df[colName].apply(le.fit_transform)
    return df


# Chargement des données en cache
df = load_data()
# Je ressorts les colonnes numériques du dataset 

# Page centrale
st.title("DEMO: FRAUD DETECTION ON MOBILE MONEY TRANSACTION", anchor="Center")

# Création du menu paramètres de gauche
st.sidebar.header("PRESENTATION")
show_overview = st.sidebar.checkbox('Généralité')
show_data = st.sidebar.checkbox('Afficher le Dataset')


if show_overview:
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(' ')
    with col2:
        img = Image.open("mobile_money.jpg")
        st.image(img, width = 200, caption = "")
    with col3:
        st.write(' ')

    
    st.write(
            "* Orange money est le service de transfert d'argent et de paiement mobile du groupe Orange, proposé dans la majorité des pays d'Afrique où l'opérateur est présent. L'utilisateur peut envoyer et recevoir des fonds ou payer des services à partir de son téléphone portable sans avoir besoin d'un compte bancaire traditionnel. Il peut également passer par des agents enregistrés pour déposer des fonds (cash-in) ou transférer des fonds vers d'autres comptes et recevoir des fonds en échange (cash-out)."
            "\n \n"
            "* À mesure que ce secteur se développe, il est confronté à des risques accrus liés à la fraude. En 2020, près de $4 milliards a été perdue en raison de fraudes et d'escroqueries, un chiffre qui devrait augmenter avec le temps car les fraudeurs adoptent des méthodes de plus en plus sophistiquées."
            
            "\n \n"
            "* Les types les plus courants de fraude à l'argent mobile consistent à prendre le contrôle du téléphone portable d'un utilisateur par hameçonnage via des appels vocaux (vishing) ou des messages SMS (smishing). Une fois que les escrocs ont accès à l'appareil, ils peuvent effectuer une fraude par échange de carte SIM en demandant au fournisseur de services téléphoniques de transférer le numéro vers l'une de leurs propres cartes SIM"
            "\n"
            )


if show_data:
    st.header("Dataset")
    st.dataframe(df.head(7))
    
   
st.sidebar.header("DATA VISUALIZATION")
options_plots = st.sidebar.selectbox('Select Plots', ['', 'Count Plot', 'Pie Plot'])
if (options_plots == 'Count Plot'): 
    st.header("Count Plot")
    fig_0 = plt.figure(figsize=(10,8))
    sns.countplot(x = "type", hue="isFraud", data = df)
    plt.title('Countplot of different types of transaction (nonFraud and Fraud)')
    st.pyplot(fig_0)
if (options_plots == 'Pie Plot'):
    st.header("Pie Plot")
    type = df['type'].value_counts()
    transaction = type.index
    count = type.values
    fig_1 = px.pie(df['type'], type, labels=transaction)
    st.plotly_chart(fig_1)


st.sidebar.header("DATA PREPARATION FOR ML")
status_model = st.sidebar.selectbox("ML type : ", ('', 'Unsupervised', 'Supervised'))
if (status_model  == 'Unsupervised'):
    payment = df[df['type']=="PAYMENT"]
    cash_in = df[df['type']=='CASH_IN']
    df_unsupervised = df.loc[(df["type"] == "PAYMENT") | (df["type"] == "CASH_IN") | (df["type"] == "DEBIT")]
    type = df_unsupervised['type'].value_counts()
    select = st.sidebar.radio('Type of Chart', ['Bar plot', 'Pie chart', 'Correlation', 'Count Plot', 'Box Plot1', 'Box Plot2'])
    if select == 'Pie chart':
        st.header("Pie Plot")
        transaction = type.index
        count = type.values
        plt.figure(figsize=(8,8))
        fig_2 = px.pie(df_unsupervised, count, labels=transaction)
        st.plotly_chart(fig_2)
    if select == 'Bar plot':
        st.header("Bar plot")
        col1, col2 = st.columns(2)
        bins = 80
        fig_3 = plt.figure(figsize=(10, 8))
        sns.distplot(payment['amount'], bins = 70)
        col1.pyplot(fig_3)
        
        fig_4 = plt.figure(figsize=(10, 8))
        sns.distplot(cash_in['amount'], bins = 70)
        col2.pyplot(fig_4)
    if select == 'Correlation':
        st.header("Correlation")
        df_unsupervised = df_unsupervised.drop(['isFraud','isFlaggedFraud'], axis=1)
        fig_5 = plt.figure(figsize=(10,7))
        sns.heatmap(df_unsupervised.corr(), annot = True, fmt='.1g')
        st.write(fig_5)
    if select == 'Count Plot':
        st.header("Count of transaction type Payments")
        fig_6, ax = plt.subplots(figsize=(9, 9))
        # plt.figure(figsize=(10,5))
        sns.countplot(x='type',data=df_unsupervised)
        st.pyplot(fig_6)
    if select == 'Box Plot1':
        st.header("Box Plot")
        fig_7 = plt.figure(figsize=(15,8))
        sns.boxplot(data=df_unsupervised, orient="h", palette="Set2")
        st.pyplot(fig_7)
    if select == 'Box Plot2':
        st.header("Boxplot for the Amount spend in transaction types")
        fig_7 = plt.figure(figsize=(15,8))
        sns.boxplot(x=df_unsupervised.type, y=df_unsupervised.amount)
        st.pyplot(fig_7)
    
if (status_model  == 'Supervised'):
    df_supervised   = df.loc[(df["type"] == "TRANSFER") | (df["type"] == "CASH_OUT")]

    df_supervised = encode_df(df_supervised)
    select_sup = st.sidebar.radio('Type of Chart', ['Correlation', 'Box Plot1'])
    if select_sup == 'Correlation':
        st.header("Correlation")
        fig_9 = plt.figure(figsize=(10,7))
        sns.heatmap(df_supervised.corr(), annot = True, fmt='.1g')
        st.write(fig_9)
    if select_sup == 'Box Plot1':
        st.header("Box Plot")
        fig_7 = plt.figure(figsize=(15,8))
        sns.boxplot(data=df_supervised, orient="h", palette="Set2")
        st.pyplot(fig_7)

st.sidebar.header("PREDICTION")
status_result = st.sidebar.selectbox("Choose model : ", ('', 'RandomForest'))

if (status_result  == 'RandomForest'):
    st.title("Résultats de prédiction à l'aide du RandomForest \n ")
    st.info('Note: La classe 0 correspond à une transaction non frauduleuse et la classe 1 correspond à une transaction frauduleuse')
    filename = 'best_baseline_model.sav'
    # joblib.dump(clf2, filename)
    loaded_model = joblib.load(filename)
    test_data = pd.read_csv("test_data.csv" , encoding = "ISO-8859-1" , sep = "," , nrows=20)
    result = loaded_model.predict(test_data)
    st.table(result)