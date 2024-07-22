
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import requests

# Function to clean each element
def clean_data(element):
    if isinstance(element, list):
        return [clean_data(sub_element) for sub_element in element]
    elif isinstance(element, dict):
        return {key: clean_data(value) for key, value in element.items()}
    elif isinstance(element, str):
        return element.replace(',', '').strip()
    else:
        return element

def render_socials(socials):
    social_links = []
    if socials == {}:  # If no valid social links were found, show a placeholder
        social_links.append(html.P("No social links available"))
    else:
        for network, url in socials.items():
            social_links.append(html.A(network, href=url, style={'margin-right': '10px'}))

    return html.Div(social_links)

# Load the data from the URL
url = "https://raw.githubusercontent.com/kosher247/canary_mission/main/canary.json"
response = requests.get(url)
data = response.json()

# Clean the data
cleaned_data = [clean_data(item) for item in data]

# Flatten the cleaned JSON data
df = pd.json_normalize(cleaned_data,max_level=0)


# Extract unique university-employer values
unique_universities = sorted(set(element for sublist in df['university-employer'] for element in sublist))


# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the Dash app
app.layout = html.Div([
    html.H1("Canary Mission Members Dashboard"),

    # Dropdown for filtering by university-employer
    dcc.Dropdown(
        id='filter-dropdown',
        options=[
            {'label': i, 'value': i} for i in unique_universities
        ],
        multi=True,
        placeholder='Filter by University-Employer'
    ),

    # Div to display filtered data
    html.Div(id='members-display')
])

# Callback to update the displayed members based on filter selection
@app.callback(
    Output('members-display', 'children'),
    [Input('filter-dropdown', 'value')]
)

def update_members(selected_universities):
    if selected_universities:
        filtered_df = df[df['university-employer'].apply(lambda x: any(uni in x for uni in selected_universities))]
    else:
        filtered_df = df

    members = []
    for _, row in filtered_df.iterrows():
        members.append(html.Div([
            html.Img(src=row['image'], style={'height':'100px'}),
            html.P(f"Name: {row['name']}"),
            html.A("Profile", href=row['url']),
            render_socials(row['socials']),
        ], style={'border':'1px solid #ddd', 'padding':'10px', 'margin':'10px', 'background': '#ddd'}))

    return members

# Run the app without debug mode
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
