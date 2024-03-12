#This sript is to be run once to create and fill a table in Google Cloud MySQL database

from google.cloud.sql.connector import Connector
import sqlalchemy
import os
import pandas as pd

# Your Google Cloud SQL database credentials
connection_name = 'amiable-parser-411713:us-central1:foodnutritionalvaluesdatabase'
database_name = 'foods'
user = 'root'
password = ':Tk)Q>dZLaIRX^:5'

key_path = '/Users/lucasvanderhorst/Downloads/amiable-parser-411713-a74922a346c3.json'  # Replace with the actual path
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