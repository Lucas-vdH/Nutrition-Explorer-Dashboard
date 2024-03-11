# Nutrition Tracker Dashboard
With the aim of learning how to build a data dashboard with ```Plotly Dash``` and deploy it on the cloud and having some interest in sport science, I decided to build a nutritional dashboard. In it, I wanted the user to select all the food items and amounts consumed in a day and the web page would load different visualizations showcasing energy, macros, mineral and vitamin consumption. Additionally, I wanted another, more exploratory, tool for the user, to find the richest foods in a certain nutritional attribute (most proteic foods, for example), along with some control over other features. In what follows below you may find an overview of the build of the project and the code snippets.

### Data extraction
Having decided on the project, I now had to find a trustworthy data set containing a large list of common foods and products along with their nutritional values. Finally, I found the FoodData Central API from the U.S. Department of Agriculture. To extract the data, I looped through a requests get command to load all the pages and store the json data in a list.
<details>
<summary>Click to see the code snippet</summary>
  
```python
    apikey='***'
    food_list=[]
    maxpagenumber=30
    for pagenumber in range(1, maxpagenumber+1):
        food=requests.get(f'https://api.nal.usda.gov/fdc/v1/foods/list?'
                        f'dataType=Foundation,Survey%20%28FNDDS%29&pageSize=200&pageNumber={pagenumber}&api_key={apikey}')
        print(f'Status code of get request for page number {pagenumber} is {food.status_code}')
        food_list.append(food.json())

    food_list=[fooditem for listitem in food_list for fooditem in listitem]
```
</details>

### Data transformation
Now, the list of json data is converted into a pandas dataframe and the relevant information extracted. However, the resulting dataframe contained a lot of information I did not wish for, missing values and was in the wrong format. Hence, the data frame was processed to put it into the proper format and with the desired information only. Finally, the resulting dataframe was saved as a csv. Note that in the code below, the same dataframe for some more mainstream foods is created, but opted out of using it in the dashboard. 
<details>
<summary>Click to see the code snippet</summary>

```python
food_df=pd.json_normalize(food_list)[['fdcId', 'description', 'foodNutrients']]
df=pd.concat([pd.DataFrame(dict)[['name', 'amount', 'unitName']] for dict in food_df['foodNutrients']],
            keys=food_df['description']).reset_index().drop('level_1', axis='columns')

df=df[~df.duplicated(subset=['description', 'name'], keep=False)].reset_index(drop=True)
df2=df.pivot(index='description', columns='name', values='amount').reset_index()
df3=df.pivot(index='description', columns='name', values='unitName').reset_index()

for currentname in df3.columns:
    if currentname=='description':
        continue
    df3.rename(columns={currentname: currentname+' unit'}, inplace=True)

df4=df2.merge(df3, how='inner', on='description')

attrlist=['Energy', 'Protein', 'Carbohydrate, by difference', 'Fatty acids, total monounsaturated',
        'Fatty acids, total polyunsaturated', 'Fatty acids, total saturated', 'Sugars, total including NLEA', 
        'Magnesium, Mg', 'Iron, Fe', 'Vitamin B-12', 'Vitamin B-6', 
        'Vitamin C, total ascorbic acid', 'Vitamin E (alpha-tocopherol)', 'Vitamin K (phylloquinone)']
attributeslist=['description']
for attribute in attrlist:
    attributeslist.append(attribute)
    attributeslist.append(attribute+' unit')


deletefoodscontaining=[' with', 'restaurant', 'toddler', ' and ']
for deletefood in deletefoodscontaining:
    mask=~df4['description'].str.contains(deletefood, regex=False, case=False)
    df4=df4[mask].reset_index(drop=True)


food_df=df4[attributeslist]
food_df.dropna(inplace=True)
food_df.reset_index(inplace=True)

print(food_df.shape)
print(food_df.columns)

mainfoods=[]
for food in food_df['description'].replace(to_replace=' ', value=',', regex=True):
    mainfood=food.split(',')[0]
    if mainfood not in mainfoods:
        mainfoods.append(mainfood)

aggdict=[]
for attribute in attributeslist:
    if 'unit' in attribute or attribute=='description':
        aggdict.append((attribute, 'first'))
    else: 
        aggdict.append((attribute, 'mean'))
aggdict=dict(aggdict)

mainfoods_df=food_df.copy(deep=True)
for mainfood in mainfoods:
    mainfoods_df.replace(f'^{mainfood}.*', mainfood, regex=True, inplace=True)

mainfoods_df=mainfoods_df.groupby('description').agg(aggdict).reset_index(drop=True)

nonmainfoods=['Textured', 'Restaurant', 'Alcoholic', 'Antipasto', 'Animal', 'Asian', 'Baked', 'Barbacue', 'Beer', 'Big',
            'Bitter', 'Black', 'Blood', 'Blue', 'Brains', 'Buffalo', 'Caesar', 'Canadian', 'Champagne', 'Chewing', 
            'Chinese', 'Classic', 'Club', 'Cocktail', 'Cuban', 'Danish', 'Dark', 'Dessert', 'Dulce', 'Fat', 'Fluid',
            'Fried', 'Frito', 'General', 'Green', 'Hard', 'Head', 'Hot', 'Huevos', 'Imitation', 'Industrial', 'Infant', 
            'Instant', 'Irish', 'Italian', 'Korean', 'Liqueur', 'Liquid', 'Lo', 'Martini', 'McDouble', 'Mexican', 'Mimosa',
            'Multiple', 'Multigrain', 'Nutrition', 'Old', 'Other', 'Pickled', 'Roll', 'Russian', 'Romaine', 'Rum',
            'Salsify', 'Screwdriver', 'Scotch', 'Seeds', 'Shortening', 'Sloppy', 'Spanish', 'Split', 'Sun-dried', 'Swedish',
            'Swiss', 'Table', 'Tequila', 'Turnover', 'Trail', 'Topping', 'Vegan', 'Vegetarian', 'Vodka', 'Whiskey', 'Wild', 
            'Wine', 'Winter', 'Whooper']
mask=~mainfoods_df['description'].isin(nonmainfoods)
mainfoods_df=mainfoods_df[mask]
print(mainfoods_df.shape)

# # ----- Printing the available nutritional attributes for future reference -----
for column in df2.columns:
    print(column)

columnmapping={'Carbohydrate, by difference': 'Carbohydrates', 'Fatty acids, total monounsaturated': 'Fats, monounsaturated',
               'Fatty acids, total polyunsaturated': 'Fats, polyunsaturated', 'Fatty acids, total saturated': 'Fats, saturated',
               'Sugars, total including NLEA': 'Sugars', 'Magnesium, Mg': 'Magnesium', 'Iron, Fe': 'Iron',
               'Vitamin C, total ascorbic acid': 'Vitamin C', 'Vitamin E (alpha-tocopherol)': 'Vitamin E',
               'Vitamin K (phylloquinone)': 'Vitamin K'}

food_df.rename(columns=columnmapping, inplace=True)
mainfoods_df.rename(columns=columnmapping, inplace=True)

food_df.loc[:, ['Vitamin B-12', 'Vitamin K']]/=1000
food_df.loc[:, ['Vitamin B-12 unit', 'Vitamin K (phylloquinone) unit']]='MG'

mainfoods_df.loc[:, ['Vitamin B-12', 'Vitamin K']]/=1000
mainfoods_df.loc[:, ['Vitamin B-12 unit', 'Vitamin K (phylloquinone) unit']]='MG'


food_df.to_csv('/Users/lucasvanderhorst/FoodDashboard/Food_df.csv')
mainfoods_df.to_csv('/Users/lucasvanderhorst/FoodDashboard/MainFoods_df.csv')
```
  
</details>

### Data loading into cloud SQL database
While building the dashboard and thinking about deployment, I realized I could not have the program access my local computer, from where I was previously loading the csv into a dataframe. Thus came the need to load the csv file into the cloud and have the program access that instead. After studying the available providers for this and the web deployment, I chose Google Cloud for the services included in the free tier. So, after creating an account and setting the database with MySQL to be loaded, I wrote the code below and stored the dataframe into a Google Cloud SQL database.
<details>
<summary>Click to see the code snippet</summary>

```python
#This sript is to be run once to create and fill a table in Google Cloud MySQL database

from google.cloud.sql.connector import Connector
import sqlalchemy
import os
import pandas as pd

# Your Google Cloud SQL database credentials
connection_name = 'amiable-parser-411713:europe-west9:foodnutritionalvaluesdatabase'
database_name = 'foods'
user = 'root'
password = '***'

key_path = '***'  # Replace with the actual path
# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path


connector = Connector()
def getconn():
    conn = connector.connect(
        connection_name,
        "pymysql",
        user=user,
        password=password,
        db=database_name)
    
    return conn

# create connection pool
pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn)

def CreateFillFoodTable(connection):
    food_df=pd.read_csv('Food_df.csv')
    food_df=food_df.loc[:, ~food_df.columns.str.contains('unit')]

    connection.execute(sqlalchemy.text('DROP TABLE IF EXISTS FoodsTable;'))

    sqlquery1='''
    CREATE TABLE IF NOT EXISTS FoodsTable (
    id INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(255) NOT NULL,\n'''

    transtable=str.maketrans(',-', '__', ' ')
    attributes=list(food_df.columns[2:])
    attributes=[i.translate(transtable) for i in attributes]

    for attribute in attributes[1:]:
        if attribute==attributes[-1]:
            sqlquery1+=f'''  {attribute} FLOAT NOT NULL'''

        else:
            sqlquery1+=f'''  {attribute} FLOAT NOT NULL,\n'''

    sqlquery1+=');\n\n'
    connection.execute(sqlalchemy.text(sqlquery1))

    queryattributes=', '.join(attributes)
    for i in range(len(food_df)):
        row=list(food_df.iloc[i][2:])
        insertrowquery=f'INSERT INTO FoodsTable ({queryattributes}) VALUES ('
        insertrowquery+=', '.join([f'''"{str(value).replace('"', '')}"''' if i==0 else str(value) for i, value in enumerate(row)])
        insertrowquery+=''');\n'''
        connection.execute(sqlalchemy.text(insertrowquery))

    result=connection.execute(sqlalchemy.text('SELECT * FROM FoodsTable LIMIT 50'))
    for row in result:
        print(row)
    
    # connection.execute(sqlalchemy.text('DROP TABLE IF EXISTS FoodsTable;'))
    
    # commit transaction (SQLAlchemy v2.X.X is commit as you go)
    connection.commit()

with pool.connect() as db_conn:
    CreateFillFoodTable(db_conn)
    
    food_dforiginal=pd.read_csv('Food_df.csv')

    food_df=pd.read_sql('FoodsTable', db_conn)
    food_df.drop('id', axis='columns', inplace=True)
    print(food_df.head(10))
    print(food_dforiginal.head(10))

connector.close()
```
  
</details>

### Building the Dash app
Finally, it was time to build the dashboard. First, I had to load the data from the SQL database in Google Cloud and put it into a pandas dataframe, as well as define some main colors and formating functions.
<details>
<summary>Click to see the code snippet</summary>

```python
# ----- Importing Packages -----

import pandas as pd
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
import random as rd
# import warnings
# warnings.filterwarnings("ignore")

import dash
from dash import dcc, html, ALL
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_mantine_components as dmc

# ---
from google.cloud.sql.connector import Connector
import sqlalchemy
# import os


def OpenGCloudMySQLConnection():

    connection_name = 'amiable-parser-411713:europe-west9:foodnutritionalvaluesdatabase'
    database_name = 'foods'
    user = 'root'
    password = '***'

    # key_path = '***'  # Replace with the actual path
    # # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path

    connector = Connector()
    def getconn():
        conn = connector.connect(
            connection_name,
            "pymysql",
            user=user,
            password=password,
            db=database_name)
        
        return conn

    # create connection pool
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn)
    
    return pool.connect(), connector

poolconnect, connector=OpenGCloudMySQLConnection()
with poolconnect as db_conn:    
    food_df=pd.read_sql('FoodsTable', db_conn)

food_df.drop('id', axis='columns', inplace=True)
food_df.rename(columns={'Fats_monounsaturated': 'Fats, monounsaturated', 'Fats_polyunsaturated': 'Fats, polyunsaturated',
                'Fats_saturated': 'Fats, saturated', 'VitaminB_12': 'Vitamin B-12', 'VitaminB_6': 'Vitamin B-6',
                'VitaminC': 'Vitamin C', 'VitaminE': 'Vitamin E', 'VitaminK': 'Vitamin K'}, inplace=True) 

connector.close()
# ---
```
```python
colorpalette=['rgb(229, 255, 204)', 'rgb(255, 255, 204)',
              'rgb(255, 229, 204)', 'rgb(255, 204, 204)', 'rgb(229, 204, 255)', 'rgb(204, 229, 255)']
textcolor='rgb(51, 51, 51)'
backgroundcolor='rgb(250, 250, 245)'

maxlabellength=18
truncatelabels=lambda x: x[:maxlabellength] + '...' if len(x) > maxlabellength else x

breaklength=25
breaklabels=lambda description: '-<br>'.join([description[i:i+breaklength] for i in range(0, len(description), breaklength)])

superscript=lambda text: text.translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))

attributes=list(food_df.columns)[1:]
DRVattributes=[2000, 56, 275, 37, 16, None, None, 325, 11, 0.0024, 1.3, 80, 15, 0.1] #From various sources. Broad reference values. In same units as their corresponding attributes

```
  
</details>
