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

food_df=pd.read_csv('Food_df.csv')

#food_df.drop('id', axis='columns', inplace=True)
food_df.rename(columns={'Fats_monounsaturated': 'Fats, monounsaturated', 'Fats_polyunsaturated': 'Fats, polyunsaturated',
                'Fats_saturated': 'Fats, saturated', 'VitaminB_12': 'Vitamin B-12', 'VitaminB_6': 'Vitamin B-6',
                'VitaminC': 'Vitamin C', 'VitaminE': 'Vitamin E', 'VitaminK': 'Vitamin K'}, inplace=True) 

connector.close()
# ---


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


app = dash.Dash(__name__)
# server=app.server
app.layout=html.Div([
    html.Div([
        html.H1(
            'Consumed Food Nutritional Analysis', 
            style={'color': 'rgb(47, 79, 79)', 'textAlign': 'center', 'margin': 'auto', 'fontFamily': 'Tahoma'}),

        html.Div([
            html.Button(
                'i',
                id='informationbutton',
                n_clicks=0,
                style={'color': textcolor,
                       'borderColor': colorpalette[2], 
                       'backgroundColor': backgroundcolor,
                       'boxShadow': 'none',
                       'borderStyle': 'solid',
                       'borderWidth': '2px',
                       'fontSize': 17,
                       'fontFamily': 'Tahoma', 
                       'borderRadius': 20}),

            dmc.Modal(
                title="Behind the scenes",
                id='informationmodal',
                size='60%',
                style={'color': textcolor, 'fontFamily': 'Tahoma'},
                children=[
                    dmc.Text('Write extra information here',
                             style={'color': textcolor, 'fontFamily': 'Tahoma'})])],
            
            style={'textAlign': 'right', 'verticalAlign': 'top'})],
        
        style={'display': 'flex', 'width': '100%', 'marginBottom': '5%', 'marginTop': '3%'}),
    
    html.Div([
        html.Div([
            html.P(
                'Select the type of visualization',
                style={'width': '100%', 'height': '20%', 'margin': 0, 'marginBottom': '3%', 'color': textcolor, 'fontFamily': 'Tahoma'}),
            
            dcc.RadioItems(
                options=['Macros distribution', 'Nutritional values', 'Food exploration'],
                value='Food exploration',
                id='typegraph',
                # inline=True,
                style={'width': '100%', 'height': '77%', 'textAlign': 'top', 'color': textcolor, 'fontFamily': 'Tahoma'})],
            
            style={'width': '20%'}),
            
        html.Div([
            html.Div([
                html.Div([
                    html.P(
                        'Select exploratory attribute',
                        style={'width': '35%', 'textAlign': 'Center', 'margin': 0, 'marginRight': '1%', 'color': textcolor, 'fontFamily': 'Tahoma'}),
                    
                    html.Div(
                        dcc.Dropdown(
                            id='explorationattribute',
                            options=attributes,
                            value=attributes[rd.randint(0, len(attributes)-1)],
                            clearable=False,
                            style={'color': textcolor, 'fontFamily': 'Tahoma'}),

                        style={'width': '65%'})],

                    style={'display': 'flex',  'width': '100%', 'alignItems': 'Center'}),

                html.Div([
                    html.P(
                        'Color by',
                        style={'width': '35%', 'textAlign': 'Center', 'margin': 0, 'marginRight': '1%', 'color': textcolor, 'fontFamily': 'Tahoma'}),

                    html.Div(
                        dcc.Dropdown(
                           id='explorationcolorby',
                           options=attributes,
                           value=attributes[rd.randint(0, len(attributes)-1)],
                           style={'color': textcolor, 'fontFamily': 'Tahoma'}),

                        style={'width': '65%'})],
                              
                    style={'display': 'flex', 'width': '100%', 'alignItems': 'Center'})],
                            
                style={'width': '57%', 'marginRight': '3%'}),
                    
            html.Div([
                html.P(
                    'Sort',
                    style={'height': '20%', 'margin': 0, 'marginBottom': '3%', 'color': textcolor, 'fontFamily': 'Tahoma'}),
                  
                dcc.RadioItems(
                   id='explorationsorting',
                   options=['Ascending', 'Descending'],
                   value='Descending',
                   style={'width': '100%', 'height': '77%', 'margin': 0, 'color': textcolor, 'fontFamily': 'Tahoma'})],
                        
                style={'width': '15%', 'marginRight': '3%'}),
                    
            html.Div([
                html.P(
                    'Limit results by',
                    style={'width': '100%', 'height': '20%', 'margin': 0, 'marginBottom': '3%', 'color': textcolor, 'fontFamily': 'Tahoma'}),
                                           
                dcc.Input(
                   id='explorationlimit',
                   type='number',    
                   value=200,               
                   min=0,
                   max=len(food_df),                        
                   style={'width': '80%', 'height': '30%', 'margin': 0, 'textAlign': 'Left', 'color': textcolor, 'fontFamily': 'Tahoma'})],
                      
                style={'width': '22%'})],

            id='explorationsettings',
            style={})],
        
        style={'width': '100%', 'margin': 0, 'display': 'flex'}),
                 
    html.Div([
        html.Div([
            html.Button(
                'New food',
                id='newfoodbutton', 
                n_clicks=1, 
                style={}),

            html.Button(
                'Delete food',
                id='deletefoodbutton',
                n_clicks=0,
                style={})],
            
            style={'width': '15%', 'marginRight': '1%', 'marginTop': '1.5%'}),

        html.Div([
            html.Div([
                html.P(
                    'Select food item 1 and its amount in grams',
                    style={'color': textcolor, 'fontFamily': 'Tahoma'}),
                
                dcc.Dropdown(
                    id={'type': 'dropdown', 'index': 1},
                    options=food_df['description'],
                    value=food_df.loc[rd.randint(0, len(food_df)-1), 'description'],
                    clearable=False,
                    optionHeight=45,
                    style={'color': textcolor, 'fontFamily': 'Tahoma'}),
                
                dmc.NumberInput(
                    id={'type': 'input', 'index': 0},
                    type='number', 
                    value=rd.randint(1, 10)*100,
                    min=0,
                    rightSection='g',
                    style={'color': textcolor, 'fontFamily': 'Tahoma'})],
                                
                style={'width': '31%', 'display': 'inline-block', 'marginRight': '2%', 'marginBottom': '2%'})],

            id='choosingfoodsdropdowns',
            style={})],
        
        style={}),
    
    html.Div(
        id='figures',
        style={'width': '100%'}),
    
    html.Div([
        html.Button(
            'Give Feedback',
            id='feedbackbutton',
            n_clicks=0,
            style={'color': textcolor,
                   'borderColor': colorpalette[2], 
                   'backgroundColor': backgroundcolor,
                   'boxShadow': 'none',
                   'borderStyle': 'solid',
                   'borderWidth': '2px',
                   'fontSize': 17,
                   'fontFamily': 'Tahoma', 
                   'borderRadius': 10}),

        dmc.Modal(
            title="Feedback form",
            id='feedbackmodal',
            size='60%',
            style={'color': textcolor, 'fontSize': 22, 'fontFamily': 'Tahoma'},
            children=[
                dmc.Text('Please write below any suggestions, bugs encountered or others you would like the developer to see',
                         style={'color': textcolor, 'fontSize': 17, 'fontFamily': 'Tahoma'}),

                dmc.Textarea(
                    id='feedbacktext',
                    placeholder='Write your feedback here :)',
                    autosize=True,
                    minRows=2,
                    style={'color': textcolor, 'fontFamily': 'Tahoma', 'marginTop': '3%'}),
                
                html.Div([
                    html.Button(
                        'Submit feedback',
                        id='submitfeedbackbutton',
                        n_clicks=0,
                        style={'color': textcolor,
                            'borderColor': colorpalette[2], 
                            'backgroundColor': backgroundcolor,
                            'boxShadow': 'none',
                            'borderStyle': 'solid',
                            'borderWidth': '2px',
                            'fontSize': 17,
                            'fontFamily': 'Tahoma', 
                            'borderRadius': 10})],
                    
                    style={'textAlign': 'Right',
                           'verticalAlign': 'Bottom',
                           'marginTop': '3%'})])],

        style={'textAlign': 'Right'}),

        dmc.Modal(
            id='feedbacksubmittedmodal',
            size='50%',
            style={'color': textcolor, 'fontSize': 22, 'fontFamily': 'Tahoma'},
            children=[
                dmc.Text(id='feedbacksubmittedtext',
                         style={'color': textcolor, 'fontSize': 17, 'fontFamily': 'Tahoma'})])],
    
    style={}
)


@app.callback([Output('newfoodbutton', 'style'),
               Output('deletefoodbutton', 'style')],
               [Input('typegraph', 'value'),
                Input('newfoodbutton', 'n_clicks'),
                Input('deletefoodbutton', 'n_clicks')])

def StyleButtons(typegraph, n_clicks_add, n_clicks_delete):
    if typegraph in ['Macros distribution', 'Nutritional values']:
        buttonstyle={'color': textcolor,
                     'borderColor': colorpalette[(n_clicks_add-n_clicks_delete-1)%len(colorpalette)], 
                     'backgroundColor': backgroundcolor,
                     'boxShadow': 'none',
                     'borderStyle': 'solid',
                     'borderWidth': '2px',
                     'fontSize': 20,
                     'fontFamily': 'Tahoma', 
                     'width': '100%', 
                     'height': '50%',
                     'borderRadius': 10}
    else:
        buttonstyle={'display': 'none'}
    
    return buttonstyle, buttonstyle


@app.callback([Output('choosingfoodsdropdowns', 'children'),
               Output('choosingfoodsdropdowns', 'style')],
              [Input('typegraph', 'value'),
               Input('newfoodbutton', 'n_clicks'),
               Input('deletefoodbutton', 'n_clicks')], 
              State('choosingfoodsdropdowns', 'children'))

def UpdateDropdowns(typegraph, n_clicks_add, n_clicks_delete, current_children):    
    ctx=dash.callback_context

    if ctx.triggered_id=='newfoodbutton':
    
        if not current_children:
            current_children=[]

        newdropdowns=html.Div([
            html.P(
                f'Select food item {n_clicks_add-n_clicks_delete} and its amount in grams',
                style={'color': textcolor, 'fontFamily': 'Tahoma'}),
            
            dcc.Dropdown(
                id={'type': 'dropdown', 'index': n_clicks_add},
                options=food_df['description'],
                value=food_df.loc[rd.randint(0, len(food_df)-1), 'description'],
                clearable=False,
                optionHeight=55,
                style={'color': textcolor, 'fontFamily': 'Tahoma'}),
            
            dmc.NumberInput(
                id={'type': 'input', 'index': n_clicks_add},
                type='number', 
                value=rd.randint(1, 10)*100,
                min=0,
                rightSection='g',
                style={'color': textcolor, 'fontFamily': 'Tahoma'})],
                              
            style={'width': '31%', 'display': 'inline-block', 'marginRight': '2%', 'marginBottom': '2%'})
        
        current_children.append(newdropdowns)

    elif ctx.triggered_id=='deletefoodbutton':
        current_children=current_children[:-1]

    
    if typegraph=='Food exploration':
        style={'display': 'none'}
    
    else:
        style={}

    return current_children, style


@app.callback(Output('explorationsettings', 'style'),
              Input('typegraph', 'value'))

def ShowExploratorySettings(typegraph):
    if typegraph=='Food exploration':         
        style={'width': '80%', 'display': 'flex'}
    
    else:
        style={'display': 'none'}
    
    return style


@app.callback(Output('feedbackmodal', 'opened'),
              Input('feedbackbutton', 'n_clicks'),
              Input('submitfeedbackbutton', 'n_clicks'),
              State('feedbackmodal', 'opened'),
              prevent_initial_call=True)

def OpenModal1(n_clicks1, n_clicks2, opened):
    return not opened


@app.callback(Output('feedbacksubmittedmodal', 'opened'),
              Output('feedbacktext', 'value'),
              Output('feedbacksubmittedtext', 'children'),
              Input('submitfeedbackbutton', 'n_clicks'),
              State('feedbacktext', 'value'),
              State('feedbacksubmittedmodal', 'opened'),
              prevent_initial_call=True)

def SubmitFeedbackSQL(n_clicks, feedback, opened):
    if not feedback:
        feedbacksubmittedmessage='Could not submit the feedback: nothing was written'
    elif len(feedback)<20:
        feedbacksubmittedmessage='Could not submit the feedback: its length is too short'

    else:
        poolconnect, connector=OpenGCloudMySQLConnection()
        with poolconnect as db_conn:
            createfeedbacktable='''CREATE TABLE IF NOT EXISTS FeedbackTable (
                                        id INT AUTO_INCREMENT PRIMARY KEY,
                                        feedback TEXT NOT NULL,
                                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);'''
            db_conn.execute(sqlalchemy.text(createfeedbacktable))
            
            insertrowquery=f"INSERT INTO FeedbackTable (feedback) VALUES ('{feedback}');"
            db_conn.execute(sqlalchemy.text(insertrowquery))

            result=db_conn.execute(sqlalchemy.text('SELECT * FROM FeedbackTable'))
            for row in result:
                print(row)

            db_conn.execute(sqlalchemy.text('DROP TABLE IF EXISTS FeedbackTable;')) #For development purposes

            db_conn.commit()
        connector.close()

        feedbacksubmittedmessage='Your feedback has been succesfully submitted. Thank you! :D'

    return not opened, None, feedbacksubmittedmessage


@app.callback(Output("informationmodal", "opened"),
              Input('informationbutton', 'n_clicks'),
              State("feedbackmodal", "opened"),
              prevent_initial_call=True)

def OpenModal2(n_clicks, opened):
    return not opened


@app.callback(Output('figures', 'children'),
              [Input('typegraph', 'value'),
               Input({'type': 'dropdown', 'index': ALL}, 'value'),
               Input({'type': 'input', 'index': ALL}, 'value'),
               Input('explorationattribute', 'value'),
               Input('explorationcolorby', 'value'),
               Input('explorationsorting', 'value'),
               Input('explorationlimit', 'value')],
               prevent_initial_call=True)

def Graphing(typegraph, dropdownvalues, inputvalues, explorationattribute, explorationcolorby, explorationsorting, explorationlimit):

    if typegraph=='Macros distribution':
        
        mask=food_df['description'].isin(dropdownvalues)
        df=food_df[mask]
        for food, amount in zip(dropdownvalues, inputvalues):
            df.loc[df['description']==food, attributes]*=amount/100

        df['Fats']=df['Fats, monounsaturated']+df['Fats, polyunsaturated']+df['Fats, saturated']
        df=df[['description', 'Protein', 'Carbohydrates', 'Fats']]
        df=pd.melt(df, id_vars='description', var_name='Macros', value_name='Amount')

        mapdict=[]
        for i, food in enumerate(dropdownvalues):
            mapdict.append((food, 1+0.0001*(i+1)))
        mapdict=dict(mapdict)

        df['description_id']=df['description'].map(mapdict)
        df.loc[df['Amount']==0, 'Amount']=0.0001

        df['Truncated description']=df['description'].apply(truncatelabels)
        df=df.sort_values(by='description')

        unique_descriptions=df['description'].unique()
        color_scale=[]
        for i in range(len(unique_descriptions)):
            color_scale.append(colorpalette[i%len(colorpalette)])

        # Create a dictionary to map descriptions to colors
        color_map=dict(zip(unique_descriptions, color_scale))
        df['Color']=df['description'].map(color_map)

        df['Weighted_R'] = df.apply(lambda row: int(row['Color'].split(',')[0][4:]) * row['Amount'], axis=1)
        df['Weighted_G'] = df.apply(lambda row: int(row['Color'].split(',')[1]) * row['Amount'], axis=1)
        df['Weighted_B'] = df.apply(lambda row: int(row['Color'].split(',')[2][:-1]) * row['Amount'], axis=1)

        carbohydratescolor=[
            int(df.loc[df['Macros']=='Carbohydrates', 'Weighted_R'].sum()/df.loc[df['Macros']=='Carbohydrates', 'Amount'].sum()),
            int(df.loc[df['Macros']=='Carbohydrates', 'Weighted_G'].sum()/df.loc[df['Macros']=='Carbohydrates', 'Amount'].sum()),
            int(df.loc[df['Macros']=='Carbohydrates', 'Weighted_B'].sum()/df.loc[df['Macros']=='Carbohydrates', 'Amount'].sum())]
        carbohydratescolor=f'rgb({carbohydratescolor[0]}, {carbohydratescolor[1]}, {carbohydratescolor[2]})'

        fatscolor=[
            int(df.loc[df['Macros']=='Fats', 'Weighted_R'].sum()/df.loc[df['Macros']=='Fats', 'Amount'].sum()),
            int(df.loc[df['Macros']=='Fats', 'Weighted_G'].sum()/df.loc[df['Macros']=='Fats', 'Amount'].sum()),
            int(df.loc[df['Macros']=='Fats', 'Weighted_B'].sum()/df.loc[df['Macros']=='Fats', 'Amount'].sum())]
        fatscolor=f'rgb({fatscolor[0]}, {fatscolor[1]}, {fatscolor[2]})'

        proteincolor=[
            int(df.loc[df['Macros']=='Protein', 'Weighted_R'].sum()/df.loc[df['Macros']=='Protein', 'Amount'].sum()),
            int(df.loc[df['Macros']=='Protein', 'Weighted_G'].sum()/df.loc[df['Macros']=='Protein', 'Amount'].sum()),
            int(df.loc[df['Macros']=='Protein', 'Weighted_B'].sum()/df.loc[df['Macros']=='Protein', 'Amount'].sum())]
        proteincolor=f'rgb({proteincolor[0]}, {proteincolor[1]}, {proteincolor[2]})'

        color_map['Carbohydrates']=carbohydratescolor
        color_map['Fats']=fatscolor
        color_map['Protein']=proteincolor


        fig=px.sunburst(df, path=['Macros', 'description'], values='Amount', hover_data=['Macros'])

        fig.update(layout_coloraxis_showscale=False)

        fig.update_traces(
            marker_colors=[color_map[cat] for cat in fig.data[-1].labels],

            labels=pd.concat([df['Truncated description'], pd.Series(['Carbohydrates', 'Fats', 'Protein'])]),
            
            hoverlabel=dict(
                    font_color=textcolor,
                    font_size=16,
                    font_family="Tahoma"),

            hovertemplate='Description: %{id}<br>' +
                          'Macro: %{customdata[0]}<br>' +
                          'Amount: %{value:.2f}g<br>' +
                          '<extra></extra>')
        

        
        fig.update_layout(
            font=dict(family='Tahoma', color=textcolor),
            plot_bgcolor=backgroundcolor)


        return dcc.Graph(figure=fig)

    elif typegraph=='Nutritional values':

        mask=food_df['description'].isin(dropdownvalues)
        df=food_df[mask]

        for food, amount in zip(dropdownvalues, inputvalues):
            df.loc[df['description']==food, attributes]*=amount/100
        df.loc[:, 'Vitamin B-6']*=10**2
        df.loc[:, 'Vitamin K']*=10**3
        df.loc[:, 'Vitamin B-12']*=10**4
        df.loc[:, 'Iron']*=10

        # df['description'] = pd.Categorical(df['description'], categories=dropdownvalues, ordered=True)
        df.sort_values('description', inplace=True)

        df=pd.melt(df, id_vars='description', var_name='NutritionalAttributes', value_name='Amount')
        mask2=df['NutritionalAttributes'].isin(attributes)
        df=df[mask2]
        

        df_trace1 = df[df['NutritionalAttributes'] == 'Energy']
        df_trace1['Breaked Description']=df_trace1['description'].apply(breaklabels)

        df_trace2 = df[df['NutritionalAttributes'].isin(['Protein', 'Carbohydrates', 'Fats, monounsaturated', 'Fats, polyunsaturated',
                                                         'Fats, saturated', 'Sugars'])]
        df_trace2['Breaked Description']=df_trace2['description'].apply(breaklabels)

        df_trace3 = df[df['NutritionalAttributes'].isin(['Magnesium', 'Iron'])]
        df_trace3['Breaked Description']=df_trace3['description'].apply(breaklabels)
        df_trace3['Real NutritionalAttributes']=df_trace3['NutritionalAttributes']
        df_trace3['Real Amount']=df_trace3['Amount']
        df_trace3.loc[df_trace3['Real NutritionalAttributes']=='Iron', 'Real Amount']/=10

        df_trace4=df[df['NutritionalAttributes'].isin(['Vitamin B-12', 'Vitamin B-6', 'Vitamin C', 'Vitamin E', 'Vitamin K'])]
        df_trace4['Breaked Description']=df_trace4['description'].apply(breaklabels)
        df_trace4['Real NutritionalAttributes']=df_trace4['NutritionalAttributes']
        df_trace4['Real Amount']=df_trace4['Amount']
        df_trace4.loc[df_trace4['Real NutritionalAttributes']=='Vitamin B-12', 'Real Amount']/=10**4
        df_trace4.loc[df_trace4['Real NutritionalAttributes']=='Vitamin B-6', 'Real Amount']/=10**2
        df_trace4.loc[df_trace4['Real NutritionalAttributes']=='Vitamin K', 'Real Amount']/=10**3

        
        fig1 = px.bar(df_trace1, x='NutritionalAttributes', y='Amount', color='description', color_discrete_sequence=colorpalette, hover_data=['Breaked Description'])
        fig2 = px.bar(df_trace2, x='NutritionalAttributes', y='Amount', color='description', color_discrete_sequence=colorpalette, hover_data=['Breaked Description'])
        fig3 = px.bar(df_trace3, x='NutritionalAttributes', y='Amount', color='description', color_discrete_sequence=colorpalette, hover_data=['Breaked Description', 
                                                                                                         'Real NutritionalAttributes', 'Real Amount'])
        fig4 = px.bar(df_trace4, x='NutritionalAttributes', y='Amount', color='description', color_discrete_sequence=colorpalette, hover_data=['Breaked Description', 
                                                                                                         'Real NutritionalAttributes', 'Real Amount'])



        fig1.update_xaxes(title_text='')
        fig2.update_xaxes(title_text='', tickangle=25)
        fig3.update_xaxes(title_text='', tickangle=25,
                          tickvals=[0, 1], 
                          ticktext=['Magnesium', 'Iron<br>     (x10)'])
        fig4.update_xaxes(title_text='', tickangle=25,
                          tickvals=[0, 1, 2, 3, 4], 
                          ticktext=[f'Vitamin B-12<br>     (x10{superscript("4")})', f'Vitamin B-6<br>     (x10{superscript("2")})', 'Vitamin C', 'Vitamin E', f'Vitamin K<br>     (x10{superscript("3")})'])


        fig1.update_yaxes(title_text='Amount (kcal)')
        fig2.update_yaxes(title_text='Amount (g)')
        fig3.update_yaxes(title_text='Amount (mg)')
        fig4.update_yaxes(title_text='Amount (mg)')


        labels=df_trace1['description']
        truncated_labels = list(map(truncatelabels, labels))

        legendlabels=dict([(label, truncatedlabel) for label, truncatedlabel in zip(labels, truncated_labels)])


        for trace in fig1.data:
            trace.name = ''
        
        for trace in fig2.data:
            trace.name = legendlabels.get(trace.name, trace.name)

        for trace in fig3.data:
            trace.name = ''

        for trace in fig4.data:
            trace.name = legendlabels.get(trace.name, trace.name)


        fig1.update_layout(
            legend_title_text='',
            font=dict(family='Tahoma', color=textcolor),
            plot_bgcolor=backgroundcolor)
        
        fig2.update_layout(
            legend_title_text='',
            font=dict(family='Tahoma', color=textcolor),
            plot_bgcolor=backgroundcolor)
        
        fig3.update_layout(
            legend_title_text='',
            font=dict(family='Tahoma', color=textcolor),
            plot_bgcolor=backgroundcolor) 
               
        fig4.update_layout(
            legend_title_text='',
            font=dict(family='Tahoma', color=textcolor),
            plot_bgcolor=backgroundcolor)

        fig1.add_shape(type='line', x0=-0.5, x1=0.5, y0=DRVattributes[0], y1=DRVattributes[0], line=dict(color='black', dash='dash'))

        for i, line_height in enumerate(DRVattributes[1:7]):
            if line_height==None:
                continue
            fig2.add_shape(type='line', x0=i-0.5, x1=i+0.5, y0=line_height, y1=line_height, line=dict(color='black', dash='dash'))

        for i, line_height in enumerate(DRVattributes[7:9]):
            if i==1:
                line_height*=10
            fig3.add_shape(type='line', x0=i-0.5, x1=i+0.5, y0=line_height, y1=line_height, line=dict(color='black', dash='dash'))

        for i, line_height in enumerate(DRVattributes[9:]):
            if i==0:
                line_height*=10**4
            elif i==1:
                line_height*=10**2
            if i==4:
                line_height*=10**3

            fig4.add_shape(type='line', x0=i-0.5, x1=i+0.5, y0=line_height, y1=line_height, line=dict(color='black', dash='dash'))
        

        fig1.update_traces(
            hoverlabel=dict(
                font_color=textcolor,
                font_size=16,
                font_family="Tahoma"),

            hovertemplate='Description: %{customdata[0]}<br>' + 
                          'Nutritional attribute: %{x}<br>' +
                          'Amount: %{y:.2f}kcal' +
                          '<extra></extra>')
        
        fig2.update_traces(
            hoverlabel=dict(
                font_color=textcolor,
                font_size=16,
                font_family="Tahoma"),

            hovertemplate='Description: %{customdata[0]}<br>' + 
                          'Nutritional attribute: %{x}<br>' +
                          'Amount: %{y:.2f}g' +
                          '<extra></extra>')
        
        fig3.update_traces(
            hoverlabel=dict(
                font_color=textcolor,
                font_size=16,
                font_family="Tahoma"),

            hovertemplate='Description: %{customdata[0]}<br>' + 
                          'Nutritional attribute: %{customdata[1]}<br>' +
                          'Amount: %{customdata[2]:.2f}mg' +
                          '<extra></extra>')
        
        fig4.update_traces(
            hoverlabel=dict(
                font_color=textcolor,
                font_size=16,
                font_family="Tahoma"),

            hovertemplate='Description: %{customdata[0]}<br>' + 
                          'Nutritional attribute: %{customdata[1]}<br>' +
                          'Amount: %{customdata[2]:.4f}mg' +
                          '<extra></extra>')


        return [html.Div([
                          dcc.Graph(figure=fig1, style={'width': '27%'}),
                          dcc.Graph(figure=fig2, style={'width': '73%'})],
                          style={'display': 'flex'}),

                html.Div([dcc.Graph(figure=fig3, style={'width': '33%'}),
                         dcc.Graph(figure=fig4, style={'width': '67%'})],
                         style={'display': 'flex'})]
            
    elif typegraph=='Food exploration':
        
        if explorationsorting=='Ascending':
            explorationsorting=True
        elif explorationsorting=='Descending':
            explorationsorting=False

        if explorationattribute==attributes[0]:
            attributeunit='kcal'
            
        elif explorationattribute in attributes[1:7]:
            attributeunit='g'

        elif explorationattribute in attributes[7:]:
            attributeunit='mg'

        if explorationcolorby==attributes[0]:
            hueunit='kcal'
            
        elif explorationcolorby in attributes[1:7]:
            hueunit='g'

        elif explorationcolorby in attributes[7:]:
            hueunit='mg'
        
        else:
            hueunit=None

        
        plot_df=food_df.copy(deep=True)
        plot_df=plot_df.sort_values(explorationattribute, ascending=explorationsorting).reset_index()

        if explorationlimit:
            plot_df=plot_df.head(explorationlimit)
            
        fig=px.bar(plot_df, x=plot_df.index, y=explorationattribute, color=explorationcolorby, color_continuous_scale=colorpalette[::-1], hover_data=['description', explorationattribute, explorationcolorby]) 
        
        fig.update_layout(
            yaxis_title=f'{explorationattribute} ({attributeunit})', 
            xaxis_title='Amount of food items', 
            coloraxis_colorbar_title=f'{explorationcolorby} ({hueunit})',
            plot_bgcolor=backgroundcolor)
        
        if explorationcolorby:
            fig.update_traces(
                hoverlabel=dict(
                    font_color=textcolor,
                    font_size=16,
                    font_family="Tahoma"),

                hovertemplate='Description: %{customdata[0]}<br>' +
                              'Index: %{x}<br>' +
                              f'{explorationattribute}: %{{y}}{attributeunit}<br>' +
                              f'{explorationcolorby}: %{{customdata[1]}}{hueunit}')
        
        else:
            fig.update_traces(
                hoverlabel=dict(
                    font_color=textcolor,
                    font_size=16,
                    font_family="Tahoma"),

                hovertemplate='Description: %{customdata[0]}<br>' +
                              'Index: %{x}<br>' +
                              f'{explorationattribute}: %{{y}}{attributeunit}<br>')    
        
        fig.update_layout(
            font=dict(family='Tahoma', color=textcolor))
        
        return dcc.Graph(figure=fig)


if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=8080)
