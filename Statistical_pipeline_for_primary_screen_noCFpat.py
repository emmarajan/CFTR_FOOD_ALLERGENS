# ## Statistical pipeline for HTS primary screen
# 
#     1. Total unique patients, gender distribution (male/female), age distribution  
#     2. Total unique samples; gender distribution (male/female); age distribution  
#     3. Input from departments samples  
#     4. CI pirate plot or similar for samples  
#     5. A. Histogram with average ODs from three highest concentrations in two colours, Colour 1- samples
#     5. B. Reversed histogram with index samples and patients
#     6. Hits vs age, hits vs gender
#     7. Feature ranking (for high-level and low-level codes) in ICD-10 space- show top most upregulated ICD-10 codes 
#         - Chi-square test +/- Bonferroni correction
#     8. Correlogramm 
#         - Most important hit/non-hit distinguishing features
#     9. Correlogramm 
#        - Feature ranking
#     10. Chord plot
#     11. Sample repetitions


# ### Implementation 


# #### Module import


%matplotlib inline
# Import packages
import warnings; 
import pyodbc
import pandas as pd
import numpy as np
import scipy
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.sandbox.stats.multicomp import multipletests

from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
import matplotlib.pyplot as plt
import bokeh
import holoviews as hv
from holoviews import opts, dim
from bokeh.sampledata.les_mis import data
from math import floor, log10
import datetime as dt  
import os

import ptitprince as pt

import pyensae
from pyensae.graphhelper import Corrplot
from IPython.display import Image
warnings.simplefilter('ignore')
#sns.set_style("white")
sns.set(style="ticks", color_codes=True)
sns.set_style({'axes.spines.top': False})
sns.set_style({'axes.spines.right': False})
colour_palette = 'plasma'

# #### Database connections
# Define connections to SQL databases

Connstr = "..."
Connstr_exp = "..."
Connstr_icd = "..."

connection = pyodbc.connect('Trusted_Connection=yes', 
                                driver = '{SQL Server}', 
                                server = '...', 
                                database = '...')
Cursor = connection.cursor();
connection_icds = pyodbc.connect('Trusted_Connection=yes', 
                                driver = '{SQL Server}', 
                                server = '...', 
                                database = '...')
Cursor_icds = connection_icds.cursor();

# Get table for a specific target


def get_table (target):
    if target=='IQR006':
        table = 'IQR006_data_Temp' 
         
        # Update table
    table = '...' + table
    return table



# #### Define target


TARGET = 'IQR006' 
TABLE = get_table (TARGET) 
print (TABLE)

PATH_SAVE_IMG = '...'

# #### Patients
# Total unique patients, gender distribution (male/female), age distribution


def count_patients (table):
    # Create db query
    db_query = (" SELECT COUNT(DISTINCT HashID_KSIM) as Patients FROM dbo.UniquePatients t1 " 
                + " JOIN dbo.Patients t2 "
                + " ON t2.PatientID = t1.SampleID "
                + " JOIN " + table + " t3 "
                + " ON t3.PatientIDList = t2.PatientIDList ")
    # Get number of unique patients
    count_patients =  pd.read_sql(db_query, pyodbc.connect(Connstr_icd))['Patients'][0] 
    return count_patients

# Pyramid age - gender 
# Inspired from https://github.com/afolaborn/Python_Jupyter_Notebook/blob/master/Population-Pyramid/Population_Pyramid_Final.ipynb 
def create_pyramid_graph (df, title):
    # Age group labels
    labels = ['0-5', '5-10', '10-15', '15-20', '20-25', '25-30', '30-35', '35-40', '40-45', '45-50', '50-55', '55-60', '60-65', '65-70', 
              '70-75', '75-80', '80-85', '85-90', '90-95', '95-100', '100+' ]
    # Revert labels order
    reversed_labels = labels[::-1]
    # Define age group index range
    range_index = [i for i in range(0, 21)]
    age_grop_female = []
    age_grop_male = []
    step_age = 5
    for i in range_index:
        count_F = 0
        count_M = 0
        if i <20:
            count_F = len(df[(df['Gender'] == 'Female') & (df['Age'] > i*step_age) & (df['Age'] <= i*step_age + 5)])
            count_M = len(df[(df['Gender'] == 'Male') & (df['Age'] > i*step_age) & (df['Age'] <= i*step_age + 5)])
        else:
            count_F = len(df[(df['Gender'] == 'Female') & (df['Age'] > i*step_age)])
            count_M = len(df[(df['Gender'] == 'Male') & (df['Age'] > i*step_age)])
        age_grop_female.append (count_F)
        age_grop_male.append (-1*count_M)
    pyramid_Data = pd.DataFrame ({'AgeGroup': labels, 'Female':age_grop_female, 'Male':age_grop_male}) # 'Female', 'Male'
    #Rotate the population pyramid by ordering ..
    plt.figure (figsize=(6,8))

    ax = sns.barplot(x="Female",y="AgeGroup", label="Female",data = pyramid_Data, order =reversed_labels,alpha=.5, 
                     color = '#5302a3') #'mediumorchid'
    ax = sns.barplot(x="Male",y="AgeGroup", label="Male",data = pyramid_Data, order =reversed_labels, alpha=.7, 
                     color = '#febd2a' )
    ax.legend()
    ax.set_title(title, weight='bold').set_fontsize('13')
    ax.set_xlabel('Population', weight='bold').set_fontsize('12')
    ax.set_ylabel('AgeGroup [Years]', weight='bold').set_fontsize('12')
    plt.savefig(PATH_SAVE_IMG+'\\patients_distribution' + '.png', dpi=300, bbox_inches='tight')
    plt.savefig(PATH_SAVE_IMG+'\\patients_distribution' + '.eps', dpi=300, bbox_inches='tight')   

# #### 1. Total number of unique patients, gender distribution (male/female), age distribution  
# Total number of unique patients
number_patients = count_patients (TABLE)
print ('Total unique patients:', number_patients)

# Patients gender and age distribution
# Create query
db_query = (" SELECT  Distinct t3.HashID_KSIM, "
            + " min(year(t2.Registration_date)- t4.YearBirth  ) as Age,  min(t4.Gender) as Gender "
            + " FROM " + TABLE +  " t1 "
            + " JOIN dbo.Patients t2 "
            + " ON t2.PatientIDList = t1.PatientIDList "
            + " JOIN dbo.UniquePatients t3 "
            + " ON t2.PatientID  = t3.SampleID "
            + " JOIN dbo.PatientsInfo t4 "
            + " ON t4.PatientID = t2.PatientID "
            + " GROUP BY t3.HashID_KSIM ")
# Get data
df = pd.read_sql(db_query, pyodbc.connect(Connstr_icd))
df.Gender.replace (['W', 'M'], ['Female', 'Male'], inplace = True)
df.to_csv ('...')
df.drop (['HashID_KSIM'], axis=1, inplace = True)

create_pyramid_graph (df,  "Population Pyramid (Patients)")
plt.savefig(PATH_SAVE_IMG+'\\population_pyramid' + '.png', dpi=300, bbox_inches='tight')
plt.savefig(PATH_SAVE_IMG+'\\population_pyramid' + '.eps', dpi=300, bbox_inches='tight') 
plt.show()

# #### 2. Total number of unique samples; gender distribution (male/female); age distribution  
# Total unique samples
def count_samples (table):
    # Create db query
    db_query = (" SELECT COUNT(Distinct PatientIDList) as Samples FROM " + TABLE )
    # Get number of unique samples
    count_patients =  pd.read_sql(db_query, pyodbc.connect(Connstr_icd))['Samples'][0] 
    return count_patients

number_samples = count_samples (TABLE)
print ('Total unique samples:', number_samples)

# Samples gender and age distribution


# Create query
db_query = (" SELECT  Age, Gender= (CASE WHEN  Gender= 'M' THEN 'Male' ELSE 'Female' END), PatientIDList FROM " + TABLE)

# Get data
df = pd.read_sql(db_query, pyodbc.connect(Connstr_icd)) 
create_pyramid_graph (df,  "Population Pyramid (Samples)")
plt.savefig(PATH_SAVE_IMG+'\\population_pyramid_samples' + '.png', dpi=300, bbox_inches='tight') 
plt.savefig(PATH_SAVE_IMG+'\\population_pyramid_samples' + '.eps', dpi=300, bbox_inches='tight') 

df.to_csv ('C:\\Users\\emmar\\Downloads\\df_samples_age_gender.csv')

# ####  3. Departments samples  
# Departments - all samples   
# Get departments that provided the samples for HTS experiments in all samples and positive samples.

# percentages
def get_departments (type_hits):
    db_query = (" SELECT Distinct t1.PatientIDList, t3.Erstelldat, Orgfa, " 
                + " Age, Gender FROM " + TABLE +" t1 "
                + " JOIN dbo.Patients t2   "
                + " ON t1.PatientIDList = t2.PatientIDList    "
                + " JOIN dbo.Diagnosis t3   "
                + " ON t3.PatientID = t2.PatientID    "
                + "  WHERE t3.Erstelldat = (select max(Erstelldat)  "
                + " FROM dbo.Diagnosis as f where f.PatientID = t2.PatientID)  "
                + " AND hits IN (" + type_hits + ")AND Orgfa != 'nan'  "
                + " ORDER BY t1.PatientIDList ")
    df = pd.read_sql(db_query, pyodbc.connect(Connstr_icd)) 
    df_name = pd.read_sql("SELECT * FROM Patients_Experiments", pyodbc.connect(Connstr_icd)) 
    #print (df_name)
    dept_name_list = []
    for index, row in df.iterrows():
        #print (row['Orgfa'])
        dept_code = int(float(row['Orgfa']))
        if len(df_name[df_name['Code'] == dept_code]) > 0:
            dept_name = df_name[df_name['Code'] == dept_code].iloc[0]['Dept']
            dept_name_list.append (dept_name)
        else:
            dept_name_list.append ('NA')
    df['Dept'] = dept_name_list
    return df

def process_department_data (df_orgfa):
    # Count departments
    df_orgfa_all= df_orgfa.groupby(['Dept']).count()
    # Drop columns
    df_orgfa_all.drop (['Erstelldat','Orgfa','Age','Gender'], axis=1, inplace=True)
    # Rename column 
    df_orgfa_all.rename(columns={'PatientIDList':'Counts'}, inplace=True)
    # Count all department occurences
    orgfa_all = sum(df_orgfa_all['Counts'])
    # Calculate percentage for each departmnet
    df_orgfa_all['Percentage'] = [round(100*i/orgfa_all,2) for i in df_orgfa_all['Counts'].tolist()]
    # Sort data frame values by percentage
    df_orgfa_all.sort_values (['Percentage'], inplace=True, ascending=False)
    return df_orgfa_all

# Get samples for all (positive and negative) samples
df_orgfa = get_departments ("'positive' , 'negative'")
df_orgfa_all = process_department_data (df_orgfa)
df_orgfa_all['type'] = ['all' for i in range(0, len(df_orgfa_all))]
# Plot
fig = plt.figure (figsize=(15,6))
plt.subplot(121)  # Subplot 1
ax = sns.barplot(x='Percentage', y=df_orgfa_all.index.values, data=df_orgfa_all, palette=colour_palette)
ax.set_title('Departments all samples', weight='bold').set_fontsize('13')
ax.set_xlabel ('Percentage %', weight='bold').set_fontsize('12')
ax.set_ylabel ('Departments', weight='bold').set_fontsize('12')
               
# Get samples for positive  samples
df_orgfa = get_departments ("'positive'")
df_orgfa_all_pos = process_department_data (df_orgfa)
df_orgfa_all_pos['type'] = ['positive' for i in range(0, len(df_orgfa_all_pos))]
# Plot
plt.subplot(122) 
ax = sns.barplot(x='Percentage', y=df_orgfa_all_pos.index.values, data=df_orgfa_all_pos, palette=colour_palette)
ax.set_ylabel ('Departments', weight='bold').set_fontsize('12')
ax.set_xlabel ('Percentage %', weight='bold').set_fontsize('12')
ax.set_title('Departments only positive samples', weight='bold').set_fontsize('13')

plt.subplots_adjust(top=1,bottom=0.1,left=0.10,right=1,hspace=0.4,wspace=0.35)
plt.savefig(PATH_SAVE_IMG+'Departments_all' + '.png', dpi=300, bbox_inches='tight')
plt.savefig(PATH_SAVE_IMG+'Departments_all' + '.tiff', dpi=300, bbox_inches='tight')
plt.savefig(PATH_SAVE_IMG+'Departments_all' + '.eps', dpi=300, bbox_inches='tight')
plt.show()


result = pd.concat([df_orgfa_all, df_orgfa_all_pos])
result['Department'] = result.index
result.index = [i for i in range(0, len(result))]
plt.figure(figsize=(15,6))
plt.subplot(121)  # Subplot 1
ax = sns.barplot(x='Percentage', y='Department', data=result, hue='type',palette=colour_palette) # colour_palette
ax.set_ylabel ('Departments', weight='bold').set_fontsize('12')
ax.set_xlabel ('Percentage %', weight='bold').set_fontsize('12')
ax.set_title ('Enriched departments', weight='bold').set_fontsize('13')

plt.subplot(122)  # Subplot 1
dept_list = []
ratio_list = []
for i in result.Department.unique():
    df_dept = result[result['Department'] == i]
    if len(df_dept) == 2:
        dept_list.append (i) 
        ratio_list.append (df_dept[df_dept['type']=='positive']['Counts'].iloc[0]/df_dept[df_dept['type']=='all']['Counts'].iloc[0])
df_dept_ratio = pd.DataFrame ({'Department':dept_list,'Ratio':ratio_list})
df_dept_ratio.sort_values(by='Ratio', ascending=False, inplace=True)
ax = sns.barplot(x='Ratio', y='Department', data=df_dept_ratio,  palette=colour_palette) #'GnBu_d'
ax.set_ylabel ('Departments', weight='bold').set_fontsize('12')
ax.set_xlabel ('Ratio P/R', weight='bold').set_fontsize('12')
ax.set_title ('Ratio positive/received', weight='bold').set_fontsize('13')
plt.subplots_adjust(top=1,bottom=0.1,left=0.10,right=1,hspace=0.4,wspace=0.35)
plt.savefig(PATH_SAVE_IMG+'Departments_enriched' + '.png', dpi=300, bbox_inches='tight')
plt.savefig(PATH_SAVE_IMG+'Departments_enriched' + '.tiff', dpi=300, bbox_inches='tight')
plt.savefig(PATH_SAVE_IMG+'Departments_enriched' + '.eps', dpi=300, bbox_inches='tight')
plt.show()

# #### 4. CI pirate plot or similar for samples
# Box plot overlapped with a strip plot for defined targets.

# TARGETS = ['IQR006']
def get_nmlogEC50_data(table, target):
    db_query = "SELECT mlogEC50, hits FROM "+ table 
    df = pd.read_sql(db_query, pyodbc.connect(Connstr_icd)) 
    df['Target'] = [target for i in range(0, len(df))]
    return df

def process_data_nmlogEC50_targets():
    frames = []
    for target in TARGETS:
        table = get_table (target)
        frame = get_nmlogEC50_data(table, target)
        frames.append (frame)
    df = pd.concat(frames)
    df = df[df['mlogEC50']>=0]
    df['Target'] = ['nAra h 2' if (x=='IQR006') else x for x in df['Target']] 
    return df

def plot_nmlogEC50_targets(df):
    plt.figure(figsize=(12,8))
    sns.stripplot(data=df, x='Target', y='mlogEC50',jitter=True,color='black', alpha=.2, size=1.2)
    ax=sns.boxplot(x='Target', y='mlogEC50',data=df,palette=colour_palette) #,palette=['#BBBBBB','#DDDDDD'])
    ax.set_ylabel ('-logEC50', weight='bold').set_fontsize('12')
    ax.set_xlabel ('Target', weight='bold').set_fontsize('12')
    ax.set_title ('Reactivity swarm box-plot per target', weight='bold').set_fontsize('13')
    plt.savefig(PATH_SAVE_IMG+'\\Reactivity_boxplot_all' + '.tiff', dpi=300, bbox_inches='tight')
    plt.savefig(PATH_SAVE_IMG+'\\Reactivity_boxplot_all' + '.png', dpi=300, bbox_inches='tight')
    plt.savefig(PATH_SAVE_IMG+'\\Reactivity_boxplot_all' + '.eps', dpi=300, bbox_inches='tight') 
    plt.show()
df = process_data_nmlogEC50_targets()
plot_nmlogEC50_targets(df)

TARGETS = ['IQR006']

from ptitprince import PtitPrince as pt
def get_nmlogEC50_data(table, target):
    db_query = "SELECT mlogEC50, hits FROM "+ table
    df = pd.read_sql(db_query, pyodbc.connect(Connstr_icd)) 
    df['Target'] = [target for i in range(0, len(df))]
    return df

def process_data_nmlogEC50_targets():
    frames = []
    for target in TARGETS:
        table = get_table (target)
        frame = get_nmlogEC50_data(table, target)
        frames.append (frame)
    df = pd.concat(frames)
    df = df[df['mlogEC50']>=0]
    df['Target'] = ['nAra h 2' if (x=='IQR006') else x for x in df['Target']] 
    return df
df = process_data_nmlogEC50_targets()
f, ax = plt.subplots(figsize=(3, 11))

dy = "mlogEC50"; dx = "Target"; ort = "v"
# Draw a violinplot with a narrower bandwidth than the default
ax=pt.half_violinplot(data = df, color='#B03C97', bw=.2,  linewidth=1,cut=0.,\
                   scale="area", width=.6, inner=None,orient=ort,x=dx,y=dy)
ax=sns.stripplot(data=df[df['hits']=='positive'], color='black',edgecolor="white",size=4,orient=ort,\
                 x=dx,y=dy,jitter=1,zorder=0)
ax=sns.stripplot(data=df[df['hits']=='negative'], color='#B03C97' ,edgecolor="white",size=2, alpha=0.5, orient=ort,\
                 x=dx,y=dy,jitter=1,zorder=0)
ax=sns.boxplot(data=df, color="black",orient=ort,width=.15,  fliersize=0,x=dx,y=dy,zorder=10,\
              showcaps=True,boxprops={'facecolor':'none', "zorder":10},\
               showfliers=True,whiskerprops={'linewidth':2, "zorder":10},saturation=1)
ax.set_ylabel ('-logEC50').set_fontsize('12')
ax.set_xlabel ('', weight='bold').set_fontsize('12')

sns.despine(left=True)
plt.savefig(PATH_SAVE_IMG+'Reactivity_boxplot_three' + '.pdf', dpi=300, bbox_inches='tight')
plt.savefig(PATH_SAVE_IMG+'Reactivity_boxplot_three' + '.tif', dpi=300, bbox_inches='tight') 

plt.show()


df.to_csv ('...')

def plot_violin_nmlogEC50_targets(df):
    plt.figure(figsize=(12,8))
    ax=sns.violinplot(data=df, x='Target', y='mlogEC50',jitter=True,palette=colour_palette)
    ax.set_ylabel ('-logEC50', weight='bold').set_fontsize('12')
    ax.set_xlabel ('Target', weight='bold').set_fontsize('12')
    ax.set_title ('Reactivity violin plot per target', weight='bold').set_fontsize('13')
    plt.savefig(PATH_SAVE_IMG+'Reactivity_violin_all' + '.png', dpi=300, bbox_inches='tight')
    plt.savefig(PATH_SAVE_IMG+'Reactivity_violin_all' + '.eps', dpi=300, bbox_inches='tight')
    plt.show()
    
plot_violin_nmlogEC50_targets(df)

def reactivity_target ():
    reactivity = []
    for target in TARGETS:
        table = get_table (target)
        dd = pd.read_sql(" SELECT * FROM "+ table, pyodbc.connect(Connstr_icd)) 
        reactivity.append(round(len(dd[dd['hits']=='positive'])*100/len(dd),2))
    df_reactivity = pd.DataFrame ({'Target':TARGETS, 'Reactivity %':reactivity})    
    return df_reactivity
df_reactivity = reactivity_target ()
df_reactivity['Target'] = ['nAra h 2' if (x=='IQR006') else x for x in df_reactivity['Target']] 
df_reactivity

# Data distribution


def get_best_distribution(data):
    dist_names = ["gamma", "lognorm", "erlang", "expon", "beta","norm", "exponweib", "weibull_max", "weibull_min", "pareto", 
                  "genextreme"]
    #dist_names = ['norm','lognorm','expon','pareto']
    dist_results = []
    params = {}
    for dist_name in dist_names:
        dist = getattr(scipy.stats, dist_name)
        param = dist.fit(data)

        params[dist_name] = param
        # Applying the Kolmogorov-Smirnov test
        D, p = scipy.stats.kstest(data, dist_name, args=param)
        print("p value for "+dist_name+" = "+str(p))
        dist_results.append((dist_name, p))

    # select the best fitted distribution
    best_dist, best_p = (max(dist_results, key=lambda item: item[1]))
    # store the name of the best fit and its p value

    print("Best fitting distribution: "+str(best_dist))
    print("Best p value: "+ str(best_p))
    print("Parameters for the best fit: "+ str(params[best_dist]))

    return best_dist, best_p, params[best_dist]
df_target = df.copy()
df_target = df_target[df_target['Target']==TARGET]
df_target.head()
y = df_target['mlogEC50']
get_best_distribution(df['mlogEC50'])


def get_target_name ():
    if TARGET =='IQR006':
        target_name = 'nAra h 2'
    else:
        target_name = TARGET
    return  target_name        
target_name = get_target_name ()
df_2 = df[(df['mlogEC50']>=2) & (df['Target']==target_name) & (df['hits']=='positive')]
gg = create_ggplot (df_2, "swarm_plot_target.png", 0.04, 300, 500)
gg = create_ggplot (df_2, "swarm_plot_target.eps", 0.04, 300, 500)
gg.plot() 
grdevices.dev_off()


# #### 5. Optical densities
# Extract samples and their first nth highest optical density points. Each sample processed by the HTS platform should have exactly 8 optical densities points for one experiments and one target. Manual experiments can have multiple points.  
# The experiments data (concentration, volume, and signal) are in table 'Experiments', Experiments database.

def optical_densities (npoints):
    # npoints - first nth highest optical density points 
    # Create query
    db_query = ( " SELECT t2.PatientIDList as PatientID, t4.Signal, t1.mlogEC50 " 
                + " FROM " + TABLE + " t1 "
                + " JOIN dbo.Patients t2 "
                + " ON t1.PatientIDList = t2.PatientIDList "
                + " JOIN dbo.PlatePatients t3 "
                + " ON t2.PatientID = t3.PatientID "
                + " JOIN dbo.Experiments t4 "
                + " ON t3.PlatePatientID = t4.PlatePatientID "
                + " WHERE t3.ExperimentTag = 1 AND t3.QCuser = 1 AND t3.Target = '" + TARGET + "'"
                + " AND t2.PatientIDList like 'J%' and t3.Sample = 's' "
                + " ORDER BY t2.PatientIDList, t4.Signal DESC")

    # Get data
    data_frame = pd.read_sql(db_query, pyodbc.connect(Connstr_icd)) 
    # Clean data - remove patients with more than 8 OD points 
    patient_ids = optical_densities_not_standardized ()
    if len(patient_ids) >0:
        for patient in patient_ids:
            data_frame = data_frame[data_frame['PatientID'] != patient]
    return data_frame

# Get the patients that have more than 8 OD points per measurmenets. These values or either wrong or from a manual experiment and will not be included in subsequent analyses.
def optical_densities_not_standardized ():
    # Create query
    db_query = ( " SELECT DISTINCT t2.PatientIDList "
                + " FROM " + TABLE + " t1 "
                + " JOIN dbo.Patients t2 "
                + " ON t1.PatientIDList = t2.PatientIDList "
                + " JOIN dbo.PlatePatients t3 "
                + " ON t2.PatientID = t3.PatientID "
                + " JOIN dbo.Experiments t4 "
                + " ON t3.PlatePatientID = t4.PlatePatientID "
                + " WHERE t3.ExperimentTag = 1 AND t3.QCuser = 1 AND t3.Target = '" + TARGET + "'"
                + " AND t2.PatientIDList like 'J%' and t3.Sample = 's' "
                + " GROUP BY t2.PatientIDList " 
                + " HAVING COUNT(t4.Concentration) !=8 ")      

    # Get data
    data_frame = pd.read_sql(db_query, pyodbc.connect(Connstr_icd)) 
    return data_frame['PatientIDList']

# Plot two figures: a) distribution of average values of the 3 highest OD points and b) sorted average values of the 3 highest OD points.
n_points = 3
data_frame_ODs = pd.DataFrame ()
data_frame_ODs = optical_densities (3)

sns.despine()
# Number of unique patients
no_patients = len(data_frame_ODs)/8

# Add new column
signal = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8']
signal_all = []
for i in range(0,int(no_patients)):
    signal_all = signal_all + signal
data_frame_ODs['Types'] = signal_all
data_frame_ODs.head()

# Pivot table
df_ODs = data_frame_ODs.pivot (index = 'PatientID', columns = 'Types', values = 'Signal')

# Calculate average 
df_ODs['Average_OD'] = (df_ODs['S1'] + df_ODs['S2'] + df_ODs['S3'])/n_points

# Sort values 
df_ODs.sort_values(by='Average_OD', ascending=True, inplace=True) 

x_range = [i for i in range(0,len(df_ODs))]
df_ODs['Index_sample'] = x_range
df_ODs.head()

# Plot
fig,axes = plt.subplots(nrows=1,ncols=2,figsize=(10,5))
ind_fig = 0
for i, ax in enumerate(axes.flatten()):
    if i == 0:
        sns.distplot(df_ODs['Average_OD'], hist = True, label = 'Average 3 ODs', ax=ax, color = '#5302a3', kde=False, rug=False)
        ax.set_title ('Distribution of average values of the 3 highest OD points', weight='bold').set_fontsize('13')
        ax.set_ylabel ('Sample', weight='bold').set_fontsize('12')  
        ax.set_xlabel ('Average OD', weight='bold').set_fontsize('12')
    if i == 1:
        sns.regplot(y='Average_OD',x='Index_sample', data=df_ODs, color='#5302a3',  fit_reg=False) # 'royalblue'
        ax.set_title ('Sorted average values of the 3 highest OD points', weight='bold').set_fontsize('13')
        ax.set_xlabel ('Index sample', weight='bold').set_fontsize('12')  
        ax.set_ylabel ('Average OD', weight='bold').set_fontsize('12')
        
plt.savefig(PATH_SAVE_IMG+'Average_OD_histo_index' + '.pdf', dpi=300, bbox_inches='tight')
plt.savefig(PATH_SAVE_IMG+'Average_OD_histo_index' + '.tif', dpi=300, bbox_inches='tight')         
        
fig.tight_layout() 

data_frame_ODs.sort_values (['PatientID'], inplace=True)
list_logvalues = data_frame_ODs['mlogEC50'].tolist()
list_patients = data_frame_ODs['PatientID'].tolist()
neglog_values = [list_logvalues[i*8] for i in range(0, int(no_patients))]
list_patients = [list_patients[i*8] for i in range(0, int(no_patients))]
data_frame_ODs[:20]
df_ODs.sort_index (axis=0, inplace=True)

df_ODs['negLogEC50'] = neglog_values
df_ODs['list_patients'] = list_patients

plt.figure(figsize=(5,5))
ax = sns.regplot(y='negLogEC50',x='Average_OD', data=df_ODs, color='#5302a3', fit_reg=True)  # alpha=0.5,
ax.set_ylabel ('-logEC50') 

x = df_ODs['negLogEC50']
y = df_ODs['Average_OD']
slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
ax.set_title ('-logEC50 vs average of the 3 highest OD points, r2=' +str(round(r_value*r_value,2)) +'\n', weight='bold').set_fontsize('13') 
ax.set_ylabel ('-logEC50', weight='bold').set_fontsize('12') 
ax.set_xlabel ('Average OD', weight='bold').set_fontsize('12')

plt.savefig(PATH_SAVE_IMG+'pEC50_vs_average_OD' + '.pdf', dpi=300, bbox_inches='tight')
plt.savefig(PATH_SAVE_IMG+'pEC50_vs_average_OD' + '.tif', dpi=300, bbox_inches='tight')     

df_ODs_th = df_ODs[df_ODs['negLogEC50']>=1.7]
plt.figure(figsize=(5,5))
ax = sns.regplot(y='negLogEC50',x='Average_OD', data=df_ODs_th, color='#5302a3',   fit_reg=True)  #alpha=0.5,
ax.set_ylabel ('-logEC50', weight='bold').set_fontsize('12')  
ax.set_xlabel ('Average OD', weight='bold').set_fontsize('12')  
x = df_ODs_th['negLogEC50']
y = df_ODs_th['Average_OD']
slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
ax.set_title ('-logEC50 (>=1.7) vs average of the 3 highest OD points, r2=' +str(round(r_value*r_value,2))+'\n', weight='bold').set_fontsize('13')

plt.savefig(PATH_SAVE_IMG+'pEC50_17_vs_average_OD' + '.pdf', dpi=300, bbox_inches='tight')
plt.savefig(PATH_SAVE_IMG+'pEC50_17_vs_average_OD' + '.tif', dpi=300, bbox_inches='tight')  

# #### 6. Hits vs age, hits vs gender
# Create graphical representation for age and gender distribution.
# - Median age test all targets
# - Chi sqaure gender test all targets
# - Scatter plot: age vs -logEC50  
# - Age histogram all hits  
# - Age distribution of hit males and females: density plots  
# - -logEC50 distribution of hit males and females


# **Median age test in all targets from HTS screen**


def get_age_target (table, type_hits):
    db_query = "SELECT Age FROM "+ table + " WHERE hits = '" + type_hits + "'"
    data_frame = pd.read_sql(db_query, pyodbc.connect(Connstr_icd)) 
    age_list = data_frame['Age'].tolist()
    return age_list

def median_test_age (targets):
    median_age_hits = []
    median_age_non_hits = []
    p_val = []
    p_value_format = []
    no_hits = []
    no_non_hits = []
    for target in targets:
        table = get_table (target)
        age_hits = get_age_target (table, 'positive')
        no_hits.append (len(age_hits))
        age_non_hits = get_age_target (table, 'negative')
        no_non_hits.append (len(age_non_hits))
        stat, p_value, med, tbl = scipy.stats.median_test(age_hits, age_non_hits)
        median_age_hits.append (np.median(age_hits))
        median_age_non_hits.append (np.median(age_non_hits))
        p_val.append (p_value)
        exponent = int(floor(log10(abs(p_value))))
        coeff = round(p_value / float(10**exponent), 2)
        p_value_f = r"{}e{}".format(coeff, exponent) 
        p_value_format.append (p_value_f)
        
    df = pd.DataFrame ({'Target':targets, 'Median hits':median_age_hits, 'Median non hits':median_age_non_hits, 'P value':p_val,
                       '# hits':no_hits, '# non hits':no_non_hits})
        
    #Bonferroni correction
    alpha = 0.01
    lista = []
    p_adjusted = multipletests(df['P value'].tolist(), alpha = alpha,  method='bonferroni')
    exponent = [int(floor(log10(abs(i)))) for i in p_adjusted[1]]
    coeff = [round(i/float(10**j),2) for i,j in zip(p_adjusted[1],exponent)]
    p_val_format = [r"{}e{}".format(i, j)  if int(j)!=0 else r"{}".format(i) for i,j in zip(coeff,exponent)]
    df['Bonferroni'] = p_val_format
    df['Signif'] = p_adjusted[0]
    df['P value'] = p_value_format 
    return df

df = median_test_age (TARGETS)
df['Target'] = ['Arah2' if (x=='IQR006') else x for x in df['Target']] 

significance = []
for pvalue in df['Bonferroni'].tolist():
    if float(pvalue) > 0.01:
        significance.append ('ns')
    else:
        if float(pvalue) <= 0.0001:
            significance.append ('****')   
        elif float(pvalue) <= 0.001:
            significance.append ('***')  
        elif float(pvalue) <= 0.01:
            significance.append ('**')    
        elif float(pvalue) <= 0.05:
            significance.append ('*')   
df['significance'] = significance
df.to_csv ('...')
df

# **Chi square gender test in all targets from HTS screen**
def gender_perc (target):
    # get table for target
    table = get_table (target) 
    # Screened females
    df_female = pd.read_sql("SELECT * FROM " + table + " WHERE  Gender = 'W'", pyodbc.connect(Connstr_icd))
    # Hit females
    df_hits_female = pd.read_sql("SELECT * FROM " + table + " WHERE hits = 'positive' AND Gender = 'W'", pyodbc.connect(Connstr_icd))   
    # Screened males
    df_male = pd.read_sql("SELECT * FROM " + table + " WHERE  Gender = 'M'", pyodbc.connect(Connstr_icd)) 
    # Hit males
    df_hits_male = pd.read_sql("SELECT * FROM " + table + " WHERE hits = 'positive' AND Gender = 'M'", pyodbc.connect(Connstr_icd))   
    df_hits = pd.read_sql("SELECT * FROM " + table + " WHERE hits = 'positive'", pyodbc.connect(Connstr_icd))   
    df_nonhits = pd.read_sql("SELECT * FROM " + table + " WHERE hits = 'negative'", pyodbc.connect(Connstr_icd))   
 
    # Calculate percentage    
    perc_male = 100*len(df_male)/len(df_nonhits)
    perc_male_hits = 100*len(df_hits_male)/len(df_hits)
    perc_female = 100*len(df_female)/len(df_nonhits)
    perc_female_hits = 100*len(df_hits_female)/len(df_hits)
   
    obs=[[len(df_female), len(df_male)], [len(df_hits_female), len(df_hits_male)]]
    chi2, p_chi, dof, expected = stats.chi2_contingency (obs)
    return perc_male, perc_male_hits, perc_female, perc_female_hits, p_chi

p_values = []
perc_male_hits_list = []
perc_female_hits_list = []
perc_male_list = []
perc_female_list = []
for target in TARGETS:
    perc_male, perc_male_hits, perc_female, perc_female_hits, p_chi = gender_perc (target)
    perc_male_hits_list.append (round(perc_male_hits,2))
    perc_female_hits_list.append (round(perc_female_hits,2))
    perc_male_list.append (round(perc_male,2))
    perc_female_list.append (round(perc_female,2))
    p_values.append (p_chi)
df_gender = pd.DataFrame ({'Target':TARGETS, 'P_values':p_values})

#Bonferroni correction
alpha = 0.01
lista = []
p_adjusted = multipletests(df_gender['P_values'].tolist(), alpha = alpha,  method='bonferroni')
exponent = [int(floor(log10(abs(i)))) for i in p_adjusted[1]]
coeff = [round(i/float(10**j),2) for i,j in zip(p_adjusted[1],exponent)]
p_val_format = [r"{}e{}".format(i, j)  if int(j)!=0 else r"{}".format(i) for i,j in zip(coeff,exponent)]

df_gender['Bonferroni'] =  p_val_format
df_gender['Signif'] = p_adjusted[0]
df_gender['Target'] = ['Arah2' if (x=='IQR006') else x for x in df_gender['Target']] 
df_gender['Perc male hits'] = perc_male_hits_list
df_gender['Perc female hits'] = perc_female_hits_list
df_gender['Perc male nonhits'] = perc_male_list
df_gender['Perc female nonhits'] = perc_female_list

significance = []
for pvalue in df_gender['Bonferroni'].tolist():
    if float(pvalue) > 0.05:
        significance.append ('ns')
    else:
        if float(pvalue) <= 0.0001:
            significance.append ('****')   
        elif float(pvalue) <= 0.001:
            significance.append ('***')  
        elif float(pvalue) <= 0.01:
            significance.append ('**')    
        elif float(pvalue) <= 0.05:
            significance.append ('*')   
df_gender['significance'] = significance
df_gender.to_csv ('...')
df_gender

# **Hits vs age and hits vs gender per target**
# Create query 
db_query = (" SELECT Gender, Age, mlogEC50 FROM " + TABLE + " WHERE hits= 'positive'" ) 
# Dataframe
data_frame = pd.read_sql(db_query, pyodbc.connect(Connstr_icd)) 
data_frame.Gender.replace (['W', 'M'], ['Female', 'Male'], inplace =  True)
data_frame.dropna(inplace=True)
# Define colour palette
cmap = ['dodgerblue', 'mediumorchid']
# Create figure with subplots
fig,axes = plt.subplots(nrows=2,ncols=2,figsize=(12,8))
ind_fig = 0
for i, ax in enumerate(axes.flatten()):
    # Subplot 1
    if i == 0:
        ax=sns.regplot(x='Age',y= 'mlogEC50', data=data_frame, color='dodgerblue', ax=ax, fit_reg=False) 
        ax.set_ylabel ('-logEC50')
        ax.set_title("-logEC50 versus age of all hits");
        plt.setp(ax.artists, alpha=.7)
    # Subplot 2
    if i == 3:
        ax=sns.boxplot(y='Gender', x='mlogEC50', data=data_frame.dropna(), whis=np.inf, orient='h', palette=cmap)
        ax=sns.swarmplot(y='Gender', x='mlogEC50', data=data_frame.dropna(), ax=ax, color='black', edgecolor='gray', orient= 'h')
        ax.set_xlabel ('-logEC50')
        ax.set_title('-logEC50 distribution of hit males and females');
        plt.setp(ax.artists, alpha=.7)
    # Subplot 3
    if i == 1:
        ax=sns.distplot(data_frame['Age'], bins=7,  ax=ax, hist=True, kde=False, rug=False)
        ax.set_title ('Age histogram in all hits')
    # Subplot 4
    if i ==2:
        data_frame_g = data_frame[data_frame['Gender']=='Female']
        sns.distplot(data_frame[data_frame['Gender']=='Male']["Age"], ax=ax,hist = False, label = 'Male',
                     kde_kws={'color': 'dodgerblue', 'shade':True, 'lw': 2})
        sns.distplot(data_frame[data_frame['Gender']=='Female']['Age'], ax=ax, hist = False, label = 'Female',
                     kde_kws={'color': 'mediumorchid', 'shade':True, 'lw': 2})
        ax.set_title ('Age distribution of hit males and females')
    ind_fig = ind_fig + 1
fig.savefig(PATH_SAVE_IMG+'age_gender' + '.png', dpi=300, bbox_inches='tight')
fig.savefig(PATH_SAVE_IMG+'age_gender' + '.eps', dpi=300, bbox_inches='tight')
fig.tight_layout()

# #### 7. Feature ranking
# Calculate the occurence of all ICD codes in negative and positive patient samples. Select the first description fro ICD description table as the ICD code description. This notebook is using high evel diagnoses codes (A40, A41, ..).
def common_codes_positive_negative_noCF (type_patients, table):
    # Create query
    db_query = (" SELECT d.ICDCode FROM dbo.Diagnosis_ICDs_level d " # Diagnosis_ICDs_level
                + " JOIN dbo.Patients p  ON p.PatientID = d.PatientID "
                + " JOIN " + table + " dat "
                + " ON dat.PatientIDList= p.PatientIDList "
                + " Inner JOIN " 
                + " (SELECT distinct PatientID "
                + " FROM dbo.Diagnosis_ICDs_level " 
                + " WHERE PatientID NOT IN ( "
                + " SELECT PatientID "
                + " FROM dbo.Diagnosis_ICDs_level " 
                + " Where ICDCode=('2675'))) TableNoCF "
                + " ON p.PatientID = TableNoCF.PatientID "
                + " WHERE dat.hits = '" 
                + type_patients + "' ")
    # Execute query and get all codes
    list_codes = pd.read_sql(db_query, pyodbc.connect(Connstr_icd))['ICDCode'].tolist() 
    # Select unique counts
    unique_list_codes = set (list_codes)
    count_appearance_list = []
    unique_id_codes = []
    for unique_code in unique_list_codes:
        count_appearance_list.append (list_codes.count(str(unique_code)))
        unique_id_codes.append (unique_code)
    df_occ = pd.DataFrame ({'code':unique_id_codes, 
                            'occurrence':count_appearance_list}).sort_values(['occurrence'], ascending=False)
    # Get ICD code description 
    code = []
    description = []
    group = []
    indexes_list = []
    for index, row in df_occ.iterrows():
        indexes_list.append (index)
        db_query = (" SELECT TOP (1) t1.ICDCode, t2.ICDDescription, t1.ICDGroup "
                    + " FROM dbo.ICDs t1  " 
                    + " JOIN ICD_Description t2 " 
                    + " ON t2.IcdID = t1.IcdID "
                    + " WHERE t1.IcdID = " + (row['code']) )
        Cursor_icds.execute (db_query)
        for row_sql in Cursor_icds:
            code.append (row_sql[0])
            description.append (row_sql[1])
            group.append (row_sql[2])            
    df_occ['code_name'] = code
    df_occ['description'] = description
    df_occ['group'] = group
    # Return data frame
    return df_occ.sort_values(["occurrence"],ascending=False)  

# Get the total number of positive/negative sample for a specific ICD code.
def get_patients_codeNoCF (type_patients, code, no_patients):
    # Create query
    db_query =( " SELECT COUNT (*) FROM dbo.Diagnosis_ICDs_level  d " # Diagnosis_ICDs_level
           + " JOIN dbo.Patients p "
           + " ON p.PatientID = d.PatientID "
           + " JOIN " + TABLE + " dat "
           + " ON dat.PatientIDList= p.PatientIDList "
           + " Inner JOIN " 
           + " (SELECT distinct PatientID "
           + " FROM dbo.Diagnosis_ICDs_level " 
           + " WHERE PatientID NOT IN ( "
           + " SELECT PatientID "
           + " FROM dbo.Diagnosis_ICDs_level " 
           + " Where ICDCode=('2675'))) TableNoCF "
           + " ON p.PatientID = TableNoCF.PatientID "  
           + " WHERE  d.ICDCode = " + code + " AND dat.hits = '" + type_patients + "' ") 
    Cursor.execute (db_query)
    # Get no codes
    for row in Cursor:
        no_code =  row[0]
    # Create array codes
    list_pos = [1 for i in range(0,int(no_code))]
    list_neg = [0 for i in range(0,no_patients - int(no_code))]
    list_values_code = list_pos + list_neg
    return list_values_code , no_code

# Calculate the significance of each ICD code in positive versus negative samples based on p value computed using a chi square test.  
# Observations:  
# Chiq-square test Python  
# *obs = [[no of positive patient samples with the ICD code (N1), no of positive patient samples with the ICD code (N2)],    
#        [total number of positive patients - N1,total number of negative patients - N2]]*  
# Test:  
# *chi2, p_chi, dof, expected = stats.chi2_contingency (obs)*


def calc_codes_significanceNoCF (df_occ_pos, df_occ_neg, type_hits, table):
    # Get screened patients
    db_query = (" SELECT * FROM " + table + " t "
                + " JOIN (select PatientID, PatientIDList FROM dbo.Patients) p "
                + " ON t.PatientIDList = p.PatientIDList "
                + " Inner JOIN " 
                + " (SELECT distinct PatientID "
                + " FROM dbo.Diagnosis_ICDs_level " 
                + " WHERE PatientID NOT IN ( "
                + " SELECT PatientID "
                + " FROM dbo.Diagnosis_ICDs_level " 
                + " Where ICDCode =('2675'))) TableNoCF "
                + " ON p.PatientID = TableNoCF.PatientID ")
    
    data_frame = pd.read_sql(db_query, pyodbc.connect(Connstr_icd)) 
    df_codes = df_occ_pos
    
    hits_codes =  df_codes["code"].tolist()
    hits_codes_names = df_codes["code_name"].tolist()
    hits_description = df_codes["description"].tolist() 
    ind = 0
    p_value_list = []
    t_value_list = []
    code_list = []
    code_list_desc = []
    n_code_1_list = []
    n_code_2_list = []
    perc_pos = []
    perc_neg = []
    for code in  hits_codes:
        if ind < len(hits_codes):
           
            pos_patients, no_code1 = get_patients_codeNoCF ("positive",code,len(data_frame[data_frame['hits']=='positive']))
            neg_patients, no_code2 = get_patients_codeNoCF ("negative",code,len(data_frame[data_frame['hits']=='negative']))
            obs = [[sum(pos_patients), sum(neg_patients)],[len(pos_patients)-sum(pos_patients),len(neg_patients)-sum(neg_patients)]]
            #print ( hits_codes_names[ind], obs)
            chi2, p_chi, dof, expected = stats.chi2_contingency (obs)
            table = [[sum(pos_patients),sum(neg_patients)],[len(pos_patients)-sum(pos_patients),len(neg_patients)-sum(neg_patients)]]
            oddsratio, p_chi = scipy.stats.fisher_exact(table, alternative='two-sided') 
            p_value_list.append (p_chi) #(float("%0.4f" % (p_chi)))  
            code_list.append ( hits_codes_names[ind])
            code_list_desc.append (hits_description[ind])
            n_code_1_list.append (no_code1)
            n_code_2_list.append (no_code2)
            perc_pos.append (round(sum(pos_patients)*100/len(pos_patients),2))
            perc_neg.append (round(sum(neg_patients)*100/len(neg_patients),2))
            ind = ind + 1
    # Create data frame
    df_rank_codes = pd.DataFrame ({'code':code_list, 'description':code_list_desc, 
                                   'p value':p_value_list, 'no hits':n_code_1_list, 
                                   'no non hits':n_code_2_list,
                                   'perc hits': perc_pos,
                                   'perc non hits': perc_neg})
    
    # Adjust for multiple comparisons
    df_rank_codes = df_rank_codes.sort_values (['p value'], ascending=True)
    methods = ['bonferroni']  
    alpha = 0.01 
    for method in methods:
        p_adjusted = multipletests(df_rank_codes['p value'].tolist(), alpha = alpha, method=method)
        df_rank_codes[method]=p_adjusted[1]
        df_rank_codes['significant ' +method]=p_adjusted[0]
    return df_rank_codes


# Select all ICD codes for negative and positive patients. Use a threshold for a minimum no of observations for each ICD code. Many statistical tests require at least 5 observations per sample.
def get_ranked_codes (table):
    # Extract code for positive and negative 
    df_occ_pos = common_codes_positive_negative_noCF ("positive", table)
    df_occ_neg = common_codes_positive_negative_noCF ("negative", table)
    # Minimum number of codes 
    min_codes = 5
    # Select ICD codes which appear at least e.g. min_codes = 5 times
    df_occ_pos = df_occ_pos[df_occ_pos['occurrence'] >=min_codes]
    df_occ_neg = df_occ_neg[df_occ_neg['occurrence'] >= min_codes]
    return df_occ_pos, df_occ_neg

df_occ_pos = common_codes_positive_negative_noCF ("positive", TABLE)

# Calculate significance hits
def process_pvalue(p_value):
    exponent = [int(floor(log10(abs(i)))) for i in p_value]
    coeff = [round(i/float(10**j),2) for i,j in zip(p_value,exponent)]
    p_val_format = [r"{}e{}".format(i, j)  if int(j)!=0 else r"{}".format(i) for i,j in zip(coeff,exponent)]
    return p_val_format

df_occ_pos, df_occ_neg = get_ranked_codes (TABLE)
df_rank_codes = calc_codes_significanceNoCF (df_occ_pos, df_occ_neg, 'positive', TABLE)
df_rank_codes['p value'] = process_pvalue(df_rank_codes['p value'].tolist())
df_rank_codes['bonferroni'] = process_pvalue(df_rank_codes['bonferroni'].tolist())

significance = []
for pvalue in df_rank_codes['bonferroni'].tolist():
    if float(pvalue) > 0.05:
        significance.append ('ns')
    else:
        if float(pvalue) <= 0.0001:
            significance.append ('****')   
        elif float(pvalue) <= 0.001:
            significance.append ('***')  
        elif float(pvalue) <= 0.01:
            significance.append ('**')    
        elif float(pvalue) <= 0.05:
            significance.append ('*')   
df_rank_codes['significance'] = significance
df_rank_codes.head()

df_rank_codes

df_rank_codes[df_rank_codes['significant bonferroni']==True]['description']

df_rank_codes.to_csv ('...')

# Calculate significance non hits
df_rank_codes_neg = calc_codes_significance (df_occ_pos, df_occ_neg, 'negative', TABLE)
df_rank_codes_neg = df_rank_codes_neg[df_rank_codes_neg['p value']<0.01]
df_rank_codes_neg = df_rank_codes_neg[df_rank_codes_neg['perc hits']<df_rank_codes_neg['perc non hits']]
df_rank_codes_neg.head()

# Show data frame with ICD codes and their significance.
# An implementation of correlation plotting tools (corrplot). This class requires scipy. Inspired from http://www.xavierdupre.fr/app/pyensae.    
# Documentation and examples here:  
# http://www.xavierdupre.fr/app/pyensae/helpsphinx/notebooks/example_corrplot.html?highlight=corr  


def plot_p_signif_codes(data, df_rank_codes):
    # Prepare data: ICD codes + age + gender
    cols = ['Age', 'Gender'] + df_rank_codes['code'].tolist()
    drop_cols = []
    for col in data.columns.values:
        if col not in cols: 
            drop_cols.append (col)
    data_pr = data.drop(drop_cols, axis=1)     
    # Correlogramm
    c = Corrplot(data_pr)
    # Plot
    c.plot(figsize=(10,10),fontsize='large', cmap = 'plasma')        

# Get ICD codes from TABLE for patients screened against TARGET 


def get_all_icd_codes (TABLE):
    # Create query
    db_query = (" SELECT DISTINCT t4.IcdID, t4.ICDCode " 
                + " FROM Diagnosis_ICDs_level t1 "
                + " JOIN Patients t2 "
                + " ON t1.PatientID = t2.PatientID "
                + " JOIN " + TABLE + " t3 "
                + " ON t3.PatientIDList = t2.PatientIDList " 
                + " JOIN dbo.ICDs t4 "
                + " ON t4.IcdID = t1.ICDCode "
                + " ORDER By t4.ICDCode " )
    # Get data
    data_frame_codes = pd.read_sql(db_query, pyodbc.connect(Connstr)) 
    return data_frame_codes

# Create matrix with all ICD codes   
# Patient1 = [Code1 Code2 Code3 ... Coden], *0 - no, 1 - yes*   
# Patient2 = [Code1 Code2 Code3 ... Coden], *0 - no, 1 - yes*   


def create_matrix_matrix (icd_codes, df):
    no_patients = len(df)
    df_codes = pd.DataFrame ()
    df_codes['Patients'] = df['PatientID']
    list_empty = [0 for value in range(0,no_patients)]
    for index, row in icd_codes.iterrows():
        name_column = row['ICDCode']
        df_codes[name_column] = list_empty
    return df_codes

# Select ICD codes for patient samples


def get_codes_matrix (df):
    patientID_list = df['PatientID']
    ind = 0
    print ('loading ...')
    for patientID in patientID_list:
        ind = ind + 1
        db_query = (" SELECT t4.IcdID, t4.ICDCode FROM Diagnosis_ICDs_level t1 "
                    + " JOIN Patients t2 "
                    + " ON t1.PatientID = t2.PatientID "
                    + " JOIN " + TABLE + " t3 "
                    + " ON t3.PatientIDList = t2.PatientIDList "
                    + " JOIN ICDs t4 "
                    + " ON t4.IcdID = t1.ICDCode "
                    + "  WHERE t2.PatientID  = " + str(patientID) ) 
        df_code_patient = pd.read_sql(db_query, pyodbc.connect(Connstr)) 
        index_val = df_codes[df_codes['Patients']==patientID].index[0]
        for code_name in df_code_patient['ICDCode'].tolist():
            df_codes.loc[index_val][code_name] = 1            
    print (' finish loading ...')
    return df_codes

# Get demographic data (age, gender) for positive and negative patient samples 
def get_demographic (TABLE):    
    db_query = (" SELECT DISTINCT t2.PatientIDList, t2.PatientID, age, gender, hits "
                + " FROM Diagnosis_ICDs_level t1 "
                + " JOIN Patients t2 "
                + " ON t1.PatientID = t2.PatientID "
                + " JOIN " + TABLE + " t3 "
                + " ON t3.PatientIDList = t2.PatientIDList ")
    data_frame =  pd.read_sql(db_query, pyodbc.connect(Connstr)) 
    return data_frame

# #### 8. Correlogramm - Feature ranking
# Get demographic data
df = get_demographic (TABLE)  

# Get demographic data
icd_codes = get_all_icd_codes (TABLE) 

# Prepare empty matrix
df_codes = create_matrix_matrix (icd_codes, df) 

# Prepare data, fill empty matrix
df_codes_final = get_codes_matrix (df)
df_codes_final['Age'] =df['age']
df_codes_final['Class']  = [1 if x == 'positive' else 0 for x in df['hits'].tolist()]
df_codes_final['Gender']  = [1 if x == 'W' else -1 for x in df['gender'].tolist()]
y = df_codes_final['Class'].tolist()

# Remove 'Class', 'Patients' columns for correlogramm
data = df_codes_final.drop(columns=['Class', 'Patients'])

# Plot correlogram for the most significant features determined based on p -values *see above*).

plot_p_signif_codes(data, df_rank_codes[df_rank_codes['significant bonferroni']==True])  

# #### 9. Correlogramm - Most important hit/non-hit distinguishing features
def feature_ranking (data, y):
    ## feature extraction
    data = (data - data.mean()) / (data.std()) 
    X = data
    cols = X.columns.values
    model = RandomForestClassifier(random_state=145)#RandomForestClassifier (123) #
    model.fit(data, y)
   
    importances = model.feature_importances_
    std = np.std([tree.feature_importances_ for tree in model.estimators_],
                 axis=0)
    indices = np.argsort(importances)[::-1]   
   
    # Plot the feature importances of the forest
    plt.figure()
    plt.title("Feature importances")
    no_features = 10
    plt.bar(range(no_features), importances[indices[0:no_features]],
           color="r", yerr=std[indices[0:no_features]], align="center")
    plt.xticks(range(no_features), cols[indices])
    plt.xlim([-1,  no_features])
    plt.show()
    return importances[indices], indices,  cols[indices]

importances, indices, description = feature_ranking (data, y)
df_features_rank = pd.DataFrame ()
df_features_rank['importances'] = importances
df_features_rank['indices'] = indices
df_features_rank['decription'] = description
drop_cols = df_features_rank[df_features_rank['importances']<0.004]['indices'].tolist() #0.0001
desc_cols = df_features_rank[df_features_rank['importances']<0.004]['decription'].tolist()
data_pr = data.drop(data.columns[drop_cols], axis=1) 

def plot_correlation (no_features, df_features_rank, data):
    drop_cols = df_features_rank[no_features:len(df_features_rank)]['indices'].tolist()
    data_pr = data.drop(data.columns[drop_cols], axis=1) 
    c = Corrplot(data_pr)
    c.plot(figsize=(10,10),fontsize='large', cmap = 'plasma')
plot_correlation (30, df_features_rank, data)    

# #### 10. Chord plot


icd_codes = df_rank_codes[df_rank_codes['significant bonferroni']==True]['code'].tolist()

def count_common_patients (target, code1, code2):
    table = get_table (target)
    db_query = (" SELECT Distinct r1.PatientIDList "
                + " FROM  " + TABLE + " r1 "
                + " JOIN dbo.Patients r2  ON r1.PatientIDList = r2.PatientIDList "  
                + " JOIN dbo.Diagnosis_ICDs_level  r3  ON r3.PatientID = r2.PatientID "  
                + " JOIN ICDs r4 ON r4.IcdID = r3.ICDCode"
                + " WHERE r4.ICDCode IN  ('" + code1 + "') AND " 
                +"  r1.hits = 'positive' AND "
                + " EXISTS ( "
                + " SELECT DISTINCT t1.PatientIDList FROM " + table + " t1 " 
                + " JOIN dbo.Patients t2 ON t1.PatientIDList = t2.PatientIDList "
                + " JOIN dbo.Diagnosis_ICDs_level t3  ON t2.PatientID = t3.PatientID "  
                + " JOIN ICDs t4  ON t4.IcdID = t3.ICDCode "  
                + " WHERE t4.ICDCode IN  ('" + code2 + "') "  
                + " AND t1.PatientIDList = r1.PatientIDList) "  
                + " AND r1.PatientIDList like 'J%' " )

    df = pd.read_sql(db_query, pyodbc.connect(Connstr_icd)) 
    return len(df)
    
def create_matrix_codes (target):
    matrix_codes = np.zeros([len(icd_codes), len(icd_codes)])
    i = 0
    j = 0
    for code1 in icd_codes:
        j = 0
        for code2 in icd_codes:
            if code1 != code2:
                #print (i,j)
                no_patients = count_common_patients (target, code1, code2) 
                matrix_codes[i][j] = no_patients
            j = j + 1
        i = i +1 
    return matrix_codes
 
def get_source_data():
    matrix_codes = create_matrix_codes (TARGET) 
    i = 0
    nodes = []
    for row in matrix_codes:
        nodes.append({'name': icd_codes[i],'group': i})
        i = i + 1
        
    i = 0
    j = 0
    count = 0
    links = []
    for row in matrix_codes:
        j = 0
        for col in matrix_codes:
            if j>=i:
                #print (i,j)
                links.append({'source': i, 'target': j, 'value': int(matrix_codes[i][j])})
                count = count + 1
            j = j + 1
        i = i + 1

    nodes_df = pd.DataFrame(nodes)
    links_df = pd.DataFrame(links)

    source_data = links_df.merge(nodes_df, how='left', left_on='source', right_index=True)
    source_data = source_data.merge(nodes_df, how='left', left_on='target', right_index=True)
    return source_data, nodes_df, links_df, nodes, links

source_data, nodes_df, links_df, nodes, links = get_source_data()

nodes1 = hv.Dataset(pd.DataFrame(nodes), 'index')

#source_data =  source_data[source_data["value"] !=0]
data_new = pd.DataFrame ({"source":source_data["target"].tolist(), 
                          "target":source_data["source"].tolist(),
                          "value":source_data["value"].tolist()} )
 
links = data_new #links_df[links_df["value"]!=0]
chord = hv.Chord((links, nodes1))#.select(value=(10, None))
chord

hv.extension('bokeh')
hv.output(size=200)
chord.opts(
    opts.Chord(cmap='Colorblind', edge_cmap='Colorblind', edge_color=dim('source').str(), 
               labels='name', node_color=dim('index').str()))

# Close connection 
connection_icds.close()
