import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load processed data
data = pd.read_csv('data/processed/processed_data.csv')

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

# Define app layout
app.layout = html.Div(children=[
    html.H1("Airbnb New York Listings Dashboard", 
            style={'text-align': 'center', 'backgroundColor': '#FF5A5F', 'color': 'white', 'padding': '10px', 'margin-bottom': '0'}),

    # First row for Price Range Slider
    html.Div([
        html.Label('Price Range:', style={'color': 'white'}),
        dcc.RangeSlider(
            id='price-slider',
            min=data['price'].min(),
            max=data['price'].max(),
            step=10,
            marks={i: {'label': f'${i}', 'style': {'color': 'white'}} for i in range(int(data['price'].min()), 
                                                                                     int(data['price'].max()), 
                                                                                     100)},
            value=[data['price'].min(), data['price'].max()],
        )
    ], style={'backgroundColor': '#FF5A5F', 'padding': '10px'}),

    # Second row for the rest of the filters/widgets
    html.Div([
        # Neighborhood dropdown
        html.Div([
            html.Label('Select Neighborhood:', style={'color': 'white'}),
            dcc.Dropdown(
                id='neighborhood-dropdown',
                options=[{'label': i, 'value': i} for i in data['neighbourhood'].unique()],
                value=data['neighbourhood'].unique()[0],
                style={'color': 'black', 'width': '100%'}
            ),
        ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '25%'}),

        # Room Type dropdown
        html.Div([
            html.Label('Select Room Type:', style={'color': 'white'}),
            dcc.Dropdown(
                id='room-type-dropdown',
                options=[{'label': i, 'value': i} for i in data['room_type'].unique()],
                value=data['room_type'].unique()[0],
                style={'color': 'black', 'width': '100%'}
            ),
        ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '25%'}),

        # Minimum Nights dropdown
        html.Div([
            html.Label('Select Minimum Nights:', style={'color': 'white'}),
            dcc.Dropdown(
                id='minimum-nights-dropdown',
                options=[{'label': i, 'value': i} for i in sorted(data['minimum_nights'].unique())],
                value=sorted(data['minimum_nights'].unique())[0],
                style={'color': 'black', 'width': '100%'}
            ),
        ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '25%'}),

        # Number of Reviews dropdown
        html.Div([
            html.Label('Select Number of Reviews:', style={'color': 'white'}),
            dcc.Dropdown(
                id='number-reviews-dropdown',
                options=[{'label': i, 'value': i} for i in range(0, data['number_of_reviews'].max()+1, 5)],
                value=0,
                style={'color': 'black', 'width': '100%'}
            ),
        ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '25%'}),
    ], style={'backgroundColor': '#FF5A5F', 'padding': '20px', 'display': 'flex', 'justifyContent': 'space-between'}),


    # Main content section for maps and charts
    html.Div([
        # Map
        html.Div(id='interactive-map-container', 
                 style={'width': '40%', 
                        'display': 'inline-block', 
                        'padding': '10px'}),

        # Donut Chart
        html.Div(id='listings-by-neighborhood-chart-container', 
                 style={'width': '30%', 
                        'display': 'inline-block', 
                        'padding': '10px'}),

        # Bar Chart for Average Price Distribution by Room Type
        html.Div(id='avg-price-distribution-chart-container', 
                 style={'width': '30%', 
                        'display': 'inline-block', 
                        'padding': '10px'}),
    ], style={'display': 'flex', 
              'justifyContent': 'space-between', 
              'alignItems': 'flex-start', 
              'margin-top': '30px', 
              'margin-bottom': '0'}),
], style={'maxWidth': '100vw', 
          'overflow': 'hidden'})

# Callback for Interactive Map
@app.callback(
    Output('interactive-map-container', 'children'),
    [Input('price-slider', 'value'),
     Input('neighborhood-dropdown', 'value'),
     Input('room-type-dropdown', 'value'),
     Input('minimum-nights-dropdown', 'value'),
     Input('number-reviews-dropdown', 'value')])
def update_map(price_range, neighborhood, room_type, minimum_nights, number_reviews):
    # Filter data based on inputs
    filtered_data = data[(data['price'] >= price_range[0]) & 
                         (data['price'] <= price_range[1]) & 
                         (data['neighbourhood'] == neighborhood) &
                         (data['room_type'] == room_type) &
                         (data['minimum_nights'] <= minimum_nights) &
                         (data['number_of_reviews'] >= number_reviews)]

    # Generate map
    fig = px.scatter_mapbox(filtered_data, lat='latitude', lon='longitude', 
                            hover_name='name', hover_data=['price', 'room_type'], 
                            color='price', zoom=10)
    fig.update_layout(mapbox_style='open-street-map')
    return dcc.Graph(figure=fig)

# Callback for Number of Listings by Neighborhood Group as Donut Chart
@app.callback(
    Output('listings-by-neighborhood-chart-container', 'children'),
    [Input('price-slider', 'value'),
     Input('room-type-dropdown', 'value'),
     Input('minimum-nights-dropdown', 'value')])
def update_listings_chart(price_range, room_type, minimum_nights):
    # Filter data based on inputs
    filtered_data = data[(data['price'] >= price_range[0]) & 
                         (data['price'] <= price_range[1]) & 
                         (data['room_type'] == room_type) &
                         (data['minimum_nights'] <= minimum_nights)]

    # Data for donut chart
    count_by_neighborhood_group = filtered_data.groupby('neighbourhood_group').size().reset_index(name='count')

    # Generate donut chart
    fig = px.pie(count_by_neighborhood_group, names='neighbourhood_group', values='count', hole=0.3,
                 title='Number of Listings by Neighborhood Group')
    return dcc.Graph(figure=fig)

# Callback for Average Price Distribution by Room Type
@app.callback(
    Output('avg-price-distribution-chart-container', 'children'),
    [Input('neighborhood-dropdown', 'value'),
     Input('minimum-nights-dropdown', 'value'),
     Input('number-reviews-dropdown', 'value')])
def update_price_by_room_type_chart(neighborhood, minimum_nights, number_reviews):
    # Filter data based on inputs
    filtered_data = data[
        (data['neighbourhood'] == neighborhood) &
        (data['minimum_nights'] <= minimum_nights) &
        (data['number_of_reviews'] >= number_reviews)
    ]

    # Data for price distribution by room type chart
    avg_price_by_room_type = filtered_data.groupby('room_type').agg({'price': 'mean'}).reset_index()

    # Generate bar chart
    fig = px.bar(avg_price_by_room_type, x='room_type', y='price', title='Average Price Distribution by Room Type')
    return dcc.Graph(figure=fig)

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
