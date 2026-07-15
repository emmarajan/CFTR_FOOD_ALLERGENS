# Generated from: For_ Marc_Medication analysis (1).ipynb
# Converted at: 2026-07-13T20:55:39.489Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

import warnings; 
import pyodbc
import pandas as pd
from datetime import datetime
from collections import Counter
import scipy
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.sandbox.stats.multicomp import multipletests
from math import floor, log10

Connstr = "..."
Connstr_exp = "..."
Connstr_icd = "..."
connection = pyodbc.connect('Trusted_Connection=yes', 
                            driver = '{SQL Server}', 
                            server = '...', 
                            database = '...')
cursor = connection.cursor();

def get_table (target):
    if target=='Tau-K18':
        table = 'TAU_data_Temp'  
    if target=='IQR006':
        table = 'IQR006_data_Temp' 
    if target=='IQR007':
        table = 'IQR007_data_Temp'
    if target=='IQR008':
        table = 'IQR008_data_Temp'
    if target=='PrP':
        table = 'PrP_data_Temp' 
    if target=='pTDP403':
        table = 'pTDP403_data_Temp'
    if target=='pTDP409':
        table = 'pTDP409_data_Temp'
    if target=='pyroAB':
        table = 'pyroAB_data_Temp'
    if target=='ApoE4':
        table = 'ApoE4_data_Temp'        
    if target=='ApoE3':
        table = 'ApoE3_data_Temp'   
    if target=='hApoE4nd':
        table = 'hApoE4nd_data_Temp'
    if target=='VCAM1':
        table = 'VCAM1_data_Temp' 
    if target=='Lag3':
        table = 'Lag3SecondaryScreen'
    if target=='LN211':
        table = 'LN211_data_Temp' 
    if target=='AGTR1':
        table = 'AGTR1_data_Temp'
    if target=='TREM2aa19-174':
        table = 'TREM2aa19_174_data_Temp'
    if target=='TREM2aa135-174':
        table = 'TREM2aa135_174_data_Temp'
    if target=='S100A8':
        table = 'S100A8_data_Temp'
    if target=='S100A8-A9':
        table = 'S100A8-A9_data_Temp'
    if target=='S100A8-A9':
        table = 'S100A8A9_data_Temp'
    if target=='ASC-C-his':
        table = 'ASC_C_his_data_Temp'
    if target=='GP96':
        table = 'GP96_data_Temp'
    if target=='SV2':
        table = 'SV2_data_Temp'  
    if target=='Spike_IgG':
        table = 'Spike_IgG_data_Temp'
    if target=='RBD_IgG':
        table = 'RBD_IgG_data_Temp' 
    if target=='NC_IgG':
        table = 'NC_IgG_data_Temp' 
    # Update table
    table = '...' + table
    
    return table
TARGET = 'S100A8-A9'
TABLE = get_table (TARGET) 

MEDICATION_TABLE = "dbo.Medication_indiv"

def get_medication (type_hits):
    db_query = (" SELECT t3.PatientID, t3.Medication FROM " + TABLE + " t1 "
                + " JOIN dbo.Patients t2 "
                + " ON t1.PatientIDList = t2.PatientIDList "
                + " JOIN " + MEDICATION_TABLE + " t3 "
                + " ON t2.PatientID = t3.PatientID "
                + " WHERE hits = '" + type_hits + "'")
    df_med =  pd.read_sql(db_query, pyodbc.connect(Connstr))
    return df_med

def count_medication (df):
    all_medication = []
    for index, row in df.iterrows():
        all_medication = all_medication + [row['Medication']]
    return Counter(all_medication)

def process_medication (type_hits):
    df = get_medication (type_hits)
    counter = count_medication (df) 

    medication = []
    counts = []
    for i in counter:
        medication.append (i)
        counts.append (counter[i])
    df = pd.DataFrame ({'medication':medication, 'counts':counts})
    return df

def calc_no_patients (type_hits):
    db_query = (" SELECT COUNT(*) as TotalNo FROM " + TABLE 
                + " WHERE hits =  '" + type_hits + "' ")
    df =  pd.read_sql(db_query, pyodbc.connect(Connstr))
    return df

df_pos = process_medication ('positive')
df_pos.head()

df_neg = process_medication ('negative')
df_neg.head()

no_pos = calc_no_patients ('positive')
no_neg = calc_no_patients ('negative')

df_pos_count_old = df_pos.copy()
df_neg_count_old = df_neg.copy()

df_pos['perc'] = (df_pos['counts']*100)/no_pos['TotalNo'].iloc[0]
df_pos.sort_values(by='counts', ascending=False)[:5] 

df_neg['perc'] = (df_neg['counts']*100)/no_neg['TotalNo'].iloc[0]
df_neg.sort_values(by='counts', ascending=False) [:5]

name = []
pos_perc = []
neg_perc = []
pos_no = []
neg_no = []
for med in df_pos['medication'].tolist():
    name.append (med)
    pos_perc.append (df_pos[df_pos['medication']==med]['perc'].iloc[0]) 
    pos_no.append (df_pos[df_pos['medication']==med]['counts'].iloc[0]) 
    if len(df_neg[df_neg['medication']==med]) > 0:
        neg_perc.append (df_neg[df_neg['medication']==med]['perc'].iloc[0])
        neg_no.append (df_neg[df_neg['medication']==med]['counts'].iloc[0])
    else:
        neg_perc.append (0)
        neg_no.append (0)
    
df_comp = pd.DataFrame ({'medication':name, 'pos_perc':pos_perc, 'pos_no':pos_no, 'neg_perc':neg_perc, 'neg_no':neg_no})
df_comp.sort_values(by='pos_perc', ascending=False) [:5]

# Calculate significance hits
def process_pvalue(p_value):
    exponent = [int(floor(log10(abs(i)))) for i in p_value]
    coeff = [round(i/float(10**j),2) for i,j in zip(p_value,exponent)]
    p_val_format = [r"{}e{}".format(i, j)  if int(j)!=0 else r"{}".format(i) for i,j in zip(coeff,exponent)]
    return p_val_format

df_comp_val = df_comp[(df_comp['pos_no'] >=5) & (df_comp['neg_no'] >= 5)]
p_value = []
for index, row in df_comp_val.iterrows ():
    obs = [[row['pos_no'], row['neg_no']],[no_pos['TotalNo'].iloc[0]-row['pos_no'],no_neg['TotalNo'].iloc[0]-row['neg_no']]]
    chi2, p_chi, dof, expected = stats.chi2_contingency (obs)
    p_value.append (p_chi)
df_comp_val['p value'] = p_value
df_comp_val.head()

# Adjust for multiple comparisons
df_comp_val = df_comp_val.sort_values (['p value'], ascending=True)
methods = ['bonferroni'] # 'holm'
alpha = 0.01 
for method in methods:
    p_adjusted = multipletests(df_comp_val['p value'].tolist(), alpha = alpha, method=method)
    df_comp_val[method]=p_adjusted[1]
    df_comp_val['significant ' +method]=p_adjusted[0]
    
df_comp_val['pos_perc'] = [round(i,2) for i in df_comp_val['pos_perc']] 
df_comp_val['neg_perc'] = [round(i,2) for i in df_comp_val['neg_perc']]  
df_comp_val['p value'] = process_pvalue(df_comp_val['p value'].tolist())
df_comp_val[method] = process_pvalue(df_comp_val[method].tolist())
    
df_comp_val.to_csv ('...')
df_comp_val[df_comp_val['significant bonferroni']==True]