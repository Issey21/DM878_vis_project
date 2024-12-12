from dash import Dash, dcc, html, Input, Output, dash_table, callback, Patch
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import dash_ag_grid as dag
from IPython.display import display, HTML
import pandas as pd
import textExtraction as ext
import math
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')
excludedWords = stopwords.words('english')
extraWords = ['he\'s', 'we\'re', 'they\'re', 'that\'s', 'i\'m']
for word in extraWords:
    excludedWords.append(word)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

colors = {
    'background': '#313131',
    'text': '#FFFFFF'
}

# Functions
def divide_chunks(l, n):
    
    # looping till length l
    for i in range(0, len(l), n): 
        yield l[i:i + n]

speakers, words, speaker = ext.extract("Vis project/Transcripts/trump_harris_debate.txt")
chunkSize = 500
chunkCount = math.floor(len(words)/chunkSize)

wordDF = pd.DataFrame({'Word': [word for word in words if word not in excludedWords]})

sortedDF = wordDF.value_counts().reset_index().rename(columns={'index': 'Word', 'A': 'Count'})

# words = ['SomeAnnouncer', 'This', 'is', 'an', 'intense', 'debate', 'between', 'two', 'fellas.', "Let's", 'us', 'see', 'what', 'they', 'have', 'to', 'say', 'about', 'politics.', 'Fella', '1', 'I', 'am', 'right,', 'and', 'you', 'are', 'wrong.', 'Fella', '2', 'No!', "You're", 'fake', 'news.', 'I', 'am', 'real', 'news!!!', 'Fella', '1', 'Come', 'on,', 'man!', "Don't", 'be', 'a', 'dumdum.', 'Fella', '2', 'Fake', 'news!', 'Fake', 'news!', "You're", 'fake', 'news!']
words = [(words[i], speaker[i]) for i in range(len(words))]
wordSections = list(divide_chunks(words, chunkSize))

# df = pd.DataFrame({
#     "Chunk": [1,2,3, 6, 7, 8, 9],
#     "Word": ["Fraud","Fraud","Fraud", "abortion", "abortion", "abortion", "abortion"],
#     "Amount": [2, 5, 3, 1, 4, 7, 3]
# })

columnDefs = [
    {
        "field": "Word",
        "checkboxSelection": True,
        "headerCheckboxSelection": True,
        "headerCheckboxSelectionFilteredOnly": True
    },
    {"field": "count"},
]


app.layout = html.Div(style={'backgroundColor': colors['background'], 'color': colors['text']}, children=[
    dcc.Store(id='textdf'),
    # dbc.CardHeader(html.H5("Comparison of bigrams for two companies")),
    dbc.CardBody(
        [
            dcc.Loading(
                id="loading-bigrams-comps",
                children=[
                    dbc.Alert(
                        "Something's gone wrong! Give us a moment, but try loading this page again if problem persists.",
                        id="no-data-alert-bigrams_comp",
                        color="warning",
                        style={"display": "none"},
                    ),
                    dbc.Row(
                        [
                        dbc.Col(html.P("Choose speakers to compare:"), md=12),
                            dbc.Row([
                                dbc.Col([
                                    dcc.Dropdown(
                                        [person for person in speakers ],
                                        id="speakers1",
                                        multi=True,
                                        className="ag-theme-alpine-dark",
                                        )
                                    ],
                                    md=6
                                ),
                                dbc.Col([
                                    dcc.Dropdown(
                                        [person for person in speakers ],
                                        id="speakers2",
                                        multi=True
                                        )
                                    ],
                                    md=6
                                ),
                            ]),
                        ]
                    ),
                ],
                type="default",
            )
        ],
        style={"marginTop": 0, "marginBottom": 0},
    ),  

    dcc.Graph(
        id='word-graph',
    ),
    dcc.Input(id="filter", placeholder="Filter...", className="ag-theme-alpine-dark",),
    dag.AgGrid(
        id="table",
        className="ag-theme-alpine-dark",
        columnDefs=columnDefs,
        rowData=sortedDF.to_dict("records"),
        columnSize="sizeToFit",
        defaultColDef={"filter": True},
        dashGridOptions={
            "rowSelection": "multiple",
            "rowMultiSelectWithClick": True,
            "pagination": True,
            "paginationAutoPageSize": True,
            "animateRows": False,
        },
    ),
])

@callback(
    Output("table", "dashGridOptions"),
    Input("filter", "value"),
)
def update_filter(filter_value):
    gridOptions_patch = Patch()
    gridOptions_patch["quickFilterText"] = filter_value
    return gridOptions_patch


@callback(
        Output('textdf', 'data'),
        Input('table', 'selectedRows'),
        Input('textdf', 'data')
)
def update_data(input_value, input_data):

    # print(input_value)
    
    df = pd.DataFrame(input_data)

    if (not input_value):
        return input_data
    
    words = [row['Word'] for row in input_value]
    # print(words)

    # if (df.empty == False and word in df["Word"].values):
    #     return input_data

    if (not df.empty):
        words = set(words)-set(df['Word'])

    for word in words:
        for i, chunk in enumerate(wordSections):
            for wordSpeaker in speakers:
                speakerWords = [speakerWord[0] for speakerWord in chunk if speakerWord[1] == wordSpeaker]
                amount = speakerWords.count(word)
                
                if amount != 0:
                    row = pd.Series({'Chunk': i+1, 'Word': word, 'Amount': amount, 'Speaker': wordSpeaker }).to_frame().T
                    df = pd.concat([df, row], ignore_index=True)

    return df.to_dict('records')


# @callback(
#     Output('dropdown', 'value'),
#     Input('dropdown', 'value'),
#     Input('table', 'cellClicked')
# )
# def update_dropdown(words_selected, input_value):
#     print(f'Words selected: {words_selected}')
#     print(f'Input value: {input_value}')


#     if (not input_value):
#         return words_selected
#     if (not words_selected):
#         return [input_value['value']]

#     words_selected.append(input_value['value'])
#     words_selected = list(set(words_selected))

#     print(words_selected)
#     return words_selected

@callback(
    Output('word-graph', 'figure'),
    Input('table', 'selectedRows'),
    Input('textdf', 'data')
)
def update_figure(words_selected, input_data):

    
    df = pd.DataFrame(input_data)
    
    if (not input_data):
        return {}
    
    words = [row['Word'] for row in words_selected]
    
    df = df[df['Word'].isin(words)]
    df = df.loc[df['Speaker'].isin(['BIDEN', 'TRUMP']) ]
    df.loc[df.Speaker == 'BIDEN', "Amount"] = -df[df.Speaker == 'BIDEN'].Amount.values
    print(df)
    fig = px.bar(df, x = "Chunk", y="Amount", color="Word", barmode="relative", range_x=(0,chunkCount+1)).update_traces(width = 0.7)

    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        transition_duration=500,
        yaxis={"showticklabels": False}
    )

    return fig


if __name__ == '__main__':
    app.run(debug=True)
    #os.kill(os.getpid(), signal.SIGTERM)