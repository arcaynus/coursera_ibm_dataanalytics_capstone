# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Build dropdown options
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())
]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                    options= site_options,
                                    value='ALL',
                                    placeholder='Select a Launch Site',
                                    clearable=False
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                               min=min_payload,
                                               max=max_payload,
                                               step=1000,
                                               value=[min_payload, max_payload],
                                               marks={int(m): f'{int(m):,}kg' for m in range(int(min_payload), int(max_payload)+1, 2000)} | {int(max_payload): f'{int(max_payload):,}kg'}
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Get the sum of the successes for all sites
        df_all_sites = (spacex_df.groupby('Launch Site', as_index=False)['class']
                        .sum()
                        .rename(columns={'class': 'Success'}))
        pie_figure = px.pie(
                            df_all_sites,
                            names='Launch Site',
                            values='Success',
                            title='Total Successful Launches by Site'
        )
    else:
        # Display the successes for the selected site
        df_launch_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        # Successes are the sum of the launch site class column since class is a number
        # with 1 for each row is a success and 0 for failure
        num_successes = int(df_launch_site['class'].sum())
        # Failures are represented by 0 so since we got the sum we can subtract that by the number
        # of records for the site to get the failures (those records which had '0' values for class)
        num_failures = int(len(df_launch_site) - num_successes)
        # Create a new dataframe to hold the successes and failures
        pie_df = pd.DataFrame({
            'Result': ['Success', 'Failure'],
            'Count' : [num_successes, num_failures]
        })
        pie_figure = px.pie(
                            pie_df,
                            names='Result',
                            values='Count',
                            title=f"Success vs Failures for: {selected_site}"
        )
    return pie_figure

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    #store the range range info
    # fallback if value is None
    if not payload_range:
        low, high = min_payload, max_payload
    else:
        low, high = payload_range
    # Filter the dataframe by the payload range
    # Create the mask first
    filter_mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    df_filtered = spacex_df[filter_mask]

    # Now filter by selected site if neccessary
    if selected_site != 'ALL':
        df_filtered = df_filtered[df_filtered['Launch Site'] == selected_site]
    
    scatter_figure = px.scatter(
        df_filtered,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site', 'Booster Version Category'],
        title=('Payload vs Success (All)' if selected_site== 'ALL'
                else f"Payload vs Success ({selected_site})") 
    )

    return scatter_figure
# Run the app
if __name__ == '__main__':
    app.run()
