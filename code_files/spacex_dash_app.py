# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


launch_sites=spacex_df['Launch Site'].drop_duplicates().to_list()
label_dicts=[]
for launch_site in launch_sites:
    label_dict={'label':launch_site,"value":launch_site}
    label_dicts.append(label_dict)

site_options = [{'label': 'All Sites', 'value': 'ALL'},*label_dicts]
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                html.Div([
                                        html.Label("Select Launch Site:"),
                                        dcc.Dropdown(
                                            id='site-dropdown',
                                            options=site_options,
                                            value='ALL',
                                            placeholder='Select Launch Site',
                                            searchable=True,
                                            style={'width': '80%', 'padding': '3px', 'font-size': 20,'textAlign': 'center' }
                                        )]
                                        ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                        marks={0: '0', 10000: '10000'},
                                    value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        data=spacex_df[spacex_df['class']==1]
        data=data.groupby('Launch Site')['Flight Number'].count().reset_index().rename(columns={'Flight Number':'Number of Successful Flights'})
        fig = px.pie(data, values='Number of Successful Flights', 
        names='Launch Site', 
        title='Number of Successful Flights for each Launch Site')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
        filtered_data=filtered_df.groupby('class')['Flight Number'].count().reset_index().rename(columns={'Flight Number':'Number of Flights'})
        # return the outcomes piechart for a selected site
        filtered_data['class']=filtered_data['class'].map({0: "Unsuccessful", 1: 'Successful'})
        fig = px.pie(filtered_data, values='Number of Flights', 
        names='class', 
        title='Number of Successful and Unsuccessful  Flights')
        return fig



# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'),
             Input(component_id='payload-slider', component_property='value'))
def get_scatter_plot(entered_site,payload_range):
    max_payload=payload_range[1]
    min_payload=payload_range[0]
    if entered_site == 'ALL':
        data=spacex_df[((spacex_df['Payload Mass (kg)']>min_payload) & (spacex_df['Payload Mass (kg)']<max_payload))]
        fig = px.scatter(data, x='Payload Mass (kg)', y='class', color="Booster Version Category",
        title='Payload and Success Chart')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
        data=filtered_df[((filtered_df['Payload Mass (kg)']>min_payload) & (filtered_df['Payload Mass (kg)']<max_payload))]
        fig = px.scatter(data, x='Payload Mass (kg)', y='class', color="Booster Version Category",
        title='Payload and Success Chart')
        return fig
    
    


# Run the app
if __name__ == '__main__':
    app.run_server()
