from dash import Dash, dcc, html, Input, Output, State, dash_table, callback, Patch, ctx
from dash.exceptions import PreventUpdate
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

# nltk.download('stopwords')
excludedWords = stopwords.words('english')
extraWords = ['he\'s', 'we\'re', 'they\'re', 'that\'s', 'i\'m']
for word in extraWords:
    excludedWords.append(word)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

colors = {
    'background': '#313131',
    'text': '#FFFFFF'
}

speakers, words, speaker = ext.extract("Vis project/Transcripts/trump_harris_debate.txt")
wordDF = pd.DataFrame({'Word': [word for word in words if word not in excludedWords]})
sortedDF = wordDF.value_counts().reset_index().rename(columns={'index': 'Word', 'A': 'Count'})
words = [(words[i], speaker[i]) for i in range(len(words))]

# Functions
def divide_chunks(l, n):
    
    # looping till length l
    for i in range(0, len(l), n): 
        yield l[i:i + n]

def genCol(word):
    sum1 = 1
    sum2 = 1
    sum3 = 1
    for i, letter in enumerate(word):
        sum1 = (sum1 * (i+2) + ord(letter)) % 255
        sum2 = (sum2 + ord(letter) * (i+2)) % 255
        sum3 = (sum3 + ord(letter) ** (i+2)) % 255
        # print(sum1)
        # print(sum2)
        # print(sum3)
        # print()
    
    # print('#%02X%02X%02X' % (sum1, sum2, sum3))
    # print()
    return '#%02X%02X%02X' % (sum1, sum2, sum3)



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
                        dbc.Col(html.P(), md=12),
                            dbc.Row([
                                dbc.Col([
                                    dcc.Dropdown(
                                        [person for person in speakers],
                                        id="speakers1",
                                        multi=True,
                                        value=[list(speakers)[0]]
                                        )
                                    ],
                                    md=6
                                ),
                                dbc.Col([
                                    dcc.Dropdown(
                                        [person for person in speakers],
                                        id="speakers2",
                                        multi=True,
                                        value=[list(speakers)[1]]
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
    "Chunk Count:",
    dcc.Input(id="chunks", type="number", value=30, min=1, max=len(words), debounce=True),
    dcc.Slider(id="slider", min=1, max=100, value=30, step=1),
    dbc.Row([
        dbc.Col([
            dcc.Input(id="filter",
                      placeholder="Filter...",
                      className="ag-theme-alpine-dark",
                      )
            ],
            md=1,
            align='center'
        ),
        dbc.Col([
            dcc.Dropdown(
                options=list(sortedDF['Word'].values),
                multi=True,
                maxHeight = 0,
                value=sortedDF.head(n=3)['Word'].values,
                searchable=False,
                id="dropfilter",
                className="ag-theme-alpine-dark"),
            ],
            md=11
        ),
    ]),
    
    
    dag.AgGrid(
        id="table",
        className="ag-theme-alpine-dark",
        columnDefs=columnDefs,
        rowData=sortedDF.to_dict("records"),
        selectedRows=sortedDF.head(n=3).to_dict("records"),
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
    Output("chunks", "value"),
    Output("slider", "value"),
    Input("slider", "value"),
    Input("chunks", "value"),
)
def updateChunks(slider, chunks):
    if (not chunks):
        raise PreventUpdate
    count = chunks if ctx.triggered_id == 'chunks' else slider
    return count, count


@callback(
    Output("table", "dashGridOptions"),
    Input("filter", "value"),
)
def update_filter(filter_value):
    gridOptions_patch = Patch()
    gridOptions_patch["quickFilterText"] = filter_value
    return gridOptions_patch


@callback(
        Output('dropfilter', 'value'),
        Output('table', 'selectedRows'),
        Input('dropfilter', 'value'),
        Input('table', 'selectedRows')
)
def update_filter_list(dropdownList, tableList):
    if (ctx.triggered_id == 'table'):
        dropdownList = [row['Word'] for row in tableList]
    elif (ctx.triggered_id == 'dropfilter'):
        tableList = sortedDF[sortedDF['Word'].isin(dropdownList)].to_dict("records")

    return dropdownList, tableList


@callback(
        Output('textdf', 'data'),
        Input('table', 'selectedRows'),
        Input('slider', 'value')
)
def update_data(input_value, chunkCount):
    chunkSize = math.floor(len(words)/chunkCount)
    wordSections = list(divide_chunks(words, chunkSize))
    
    newWords = [row['Word'] for row in input_value]
    df = pd.DataFrame()
    
    for word in newWords:
        for i, chunk in enumerate(wordSections):
            for wordSpeaker in speakers:
                speakerWords = [speakerWord[0] for speakerWord in chunk if speakerWord[1] == wordSpeaker]
                amount = speakerWords.count(word)
                
                if amount != 0:
                    row = pd.Series({'Chunk': i+1, 'Word': word, 'Amount': amount, 'Speaker': wordSpeaker, 'Colour': genCol(word) }).to_frame().T
                    df = pd.concat([df, row], ignore_index=True)

    return df.to_dict('records')



@callback(
    Output('word-graph', 'figure'),
    Input('table', 'selectedRows'),
    Input('textdf', 'data'),
    Input('speakers1', 'value'),
    Input('speakers2', 'value'),
    Input('slider', 'value')

)
def update_figure(words_selected, input_data, speaker1, speaker2, chunkCount):
    
    df = pd.DataFrame(input_data)
    
    if (not input_data):
        return {}
    
    words = [row['Word'] for row in words_selected]
    colourDict = {word: genCol(word) for word in words}
    
    df = df[df['Word'].isin(words)]
    df = df.loc[df['Speaker'].isin(speaker1+speaker2)]
    df.loc[df.Speaker.isin(speaker2), "Amount"] = -df[df.Speaker.isin(speaker2)].Amount.values
    fig = px.bar(df, x = "Chunk", y="Amount", color="Word", hover_name="Word", color_discrete_map=colourDict,
                hover_data={'Chunk':False, 
                            #  'Chunk ':df["Chunk"].apply(lambda x:f' {x}'),
                                'Word':False,
                                'Amount':False, 
                                'Amount ':df["Amount"].abs().apply(lambda x:f' {x}')}, 
                                barmode="relative",
                                range_x=(0,chunkCount+1)).update_traces(width = 0.7)

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