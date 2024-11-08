from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import pandas as pd
import os
import signal

app = Dash(__name__)

colors = {
    'background': '#FFFFFF',
    'text': '#241251'
}

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})


# Functions
# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

# Functions
def divide_chunks(l, n):
    
    # looping till length l
    for i in range(0, len(l), n): 
        yield l[i:i + n]


transcript = ['SomeAnnouncer', 'This', 'is', 'an', 'intense', 'debate', 'between', 'two', 'fellas.', "Let's", 'us', 'see', 'what', 'they', 'have', 'to', 'say', 'about', 'politics.', 'Fella', '1', 'I', 'am', 'right,', 'and', 'you', 'are', 'wrong.', 'Fella', '2', 'No!', "You're", 'fake', 'news.', 'I', 'am', 'real', 'news!!!', 'Fella', '1', 'Come', 'on,', 'man!', "Don't", 'be', 'a', 'dumdum.', 'Fella', '2', 'Fake', 'news!', 'Fake', 'news!', "You're", 'fake', 'news!']
wordSections = list(divide_chunks(transcript, 5))

chunks = []


textdf = pd.DataFrame({
    "Chunk": [1,2,3, 6, 7, 8, 9],
    "Word": ["Fraud","Fraud","Fraud", "abortion", "abortion", "abortion", "abortion"],
    "Amount": [2, 5, 3, 1, 4, 7, 3]

})
# textdf = textdf[textdf.Word != "Fraud"]


words = []


fig = px.bar(df, x="Amount", y="Fruit", color="City", barmode="relative")

# wordFig = px.bar( x=range(len("WordSections")), barmode="relative")
wordFig = px.bar(textdf, x = "Chunk", y="Amount", color="Word", barmode="relative")

wordFig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text'],
    yaxis = dict(range=[-10,10],),
    xaxis = dict(range=[0,10],)
)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div(id='my-output'),
    
    html.Div(children=[
        html.Label('Multi-Select Dropdown'),
        dcc.Dropdown(transcript,
                     id="dropdown",
                     multi=True),

        html.Br(),
    ], style={'padding': 10, 'flex': 1}),

    html.H1(
        children='Title',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Dash: A web application framework for your data.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='example-graph-2',
        figure=wordFig
    )
])

@callback(
    Output(component_id='my-output', component_property='children'),
    Input(component_id='dropdown', component_property='value')
)
def update_output_div(input_value):
    print(textdf)
    return f'Output: {input_value}'

def update_words(input_value):
    words.append(input_value)
    return words

# app.layout = html.Div([
#     html.Div(children=[
#         html.Label('Dropdown'),
#         dcc.Dropdown(['New York City', 'Montréal', 'San Francisco'], 'Montréal'),

#         html.Br(),
#         html.Label('Multi-Select Dropdown'),
#         dcc.Dropdown(['New York City', 'Montréal', 'San Francisco'],
#                      ['Montréal', 'San Francisco'],
#                      multi=True),

#         html.Br(),
#         html.Label('Radio Items'),
#         dcc.RadioItems(['New York City', 'Montréal', 'San Francisco'], 'Montréal'),
#     ], style={'padding': 10, 'flex': 1}),

#     html.Div(children=[
#         html.Label('Checkboxes'),
#         dcc.Checklist(['New York City', 'Montréal', 'San Francisco'],
#                       ['Montréal', 'San Francisco']
#         ),

#         html.Br(),
#         html.Label('Text Input'),
#         dcc.Input(value='MTL', type='text'),

#         html.Br(),
#         html.Label('Slider'),
#         dcc.Slider(
#             min=0,
#             max=9,
#             marks={i: f'Label {i}' if i == 1 else str(i) for i in range(1, 6)},
#             value=5,
#         ),
#     ], style={'padding': 10, 'flex': 1})
# ], style={'display': 'flex', 'flexDirection': 'row'})


if __name__ == '__main__':
    app.run(debug=True)
    #os.kill(os.getpid(), signal.SIGTERM)

