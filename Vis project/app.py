from dash import Dash, dcc, html, Input, Output, callback, Patch, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import dash_ag_grid as dag
import pandas as pd
import textExtraction as ext
import math
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud

# nltk.download('stopwords')
excludedWords = stopwords.words('english')
extraWords = ['he\'s', 'we\'re', 'they\'re', 'that\'s', 'i\'m', 'i\'ve', 'there\'s', 'can\'t', 'they\'ve', 'we\'ve', 'let\'s']
for word in extraWords:
    excludedWords.append(word)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

colors = {
    'background': '#FFFFFF',
    'text': '#000000'
}

speakers, words, speaker = ext.extract("Vis project/Transcripts/trump_harris_debate.txt")
wordDF = pd.DataFrame({'Word': [word for word in words if word not in excludedWords]})
sortedDF = wordDF.value_counts().reset_index().rename(columns={'index': 'Word', 'A': 'Count'})
words = [(words[i], speaker[i]) for i in range(len(words))]
wordDF = pd.DataFrame(words, columns=['Word', 'Speaker'])

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

def color_funcion(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return genCol(word)

def plotly_wordcloud():
    """A wonderful function that returns figure data for three equally
    wonderful plots: wordcloud, frequency histogram and treemap"""

    text = [word[0] for word in words]
    text = " ".join(list(text))

    word_cloud = WordCloud(stopwords=set(excludedWords), max_words=100, max_font_size=90, color_func=color_funcion)
    word_cloud.generate(text)

    word_list = []
    freq_list = []
    fontsize_list = []
    position_list = []
    orientation_list = []
    color_list = []

    for (word, freq), fontsize, position, orientation, color in word_cloud.layout_:
        word_list.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        position_list.append(position)
        orientation_list.append(orientation)
        color_list.append(color)

    # get the positions
    x_arr = []
    y_arr = []
    for i in position_list:
        x_arr.append(i[0])
        y_arr.append(i[1])

    # get the relative occurence frequencies
    new_freq_list = []
    for i in freq_list:
        new_freq_list.append(i * 80)

    trace = go.Scatter(
        x=x_arr,
        y=y_arr,
        textfont=dict(size=new_freq_list, color=color_list),
        hoverinfo="text",
        textposition="top center",
        hovertext=["{0} - {1}".format(w, f) for w, f in zip(word_list, freq_list)],
        mode="text",
        text=word_list,
    )

    layout = go.Layout(
        {
            "xaxis": {
                "showgrid": False,
                "showticklabels": False,
                "zeroline": False,
                "automargin": True,
                "range": [-100, 250],
            },
            "yaxis": {
                "showgrid": False,
                "showticklabels": False,
                "zeroline": False,
                "automargin": True,
                "range": [-100, 450],
            },
            "margin": dict(t=20, b=20, l=10, r=10, pad=4),
            "hovermode": "closest",
            "plot_bgcolor": colors['background'],
            "paper_bgcolor": colors['background'],
            "font_color": colors['text'],
        }
    )

    wordcloud_figure_data = {"data": [trace], "layout": layout}

    return wordcloud_figure_data

columnDefs = [
    {
        "field": "Word",
        "checkboxSelection": True,
        "headerCheckboxSelection": True,
        "headerCheckboxSelectionFilteredOnly": True
    },
    {
        "field": "count",
        "sort": 'desc',
        "sortingOrder": ['desc', 'asc', None],
    },
    {
        "field": "Speaker 1",
        "sortingOrder": ['desc', 'asc', None],
    },
    {
        "field": "Speaker 2",
        "sortingOrder": ['desc', 'asc', None],
    }
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
                                        value=[list(speakers)[0]],
                                        )
                                    ],
                                    md=6
                                ),
                                dbc.Col([
                                    dcc.Dropdown(
                                        [person for person in speakers],
                                        id="speakers2",
                                        multi=True,
                                        value=[list(speakers)[1]],
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
    dcc.Tabs(
        id="tabs",
        children=[
            dcc.Tab(
                label="Bar chart",
                children=[
                    dcc.Loading(
                        id="graph-loading",
                        children=[
                            dcc.Graph(
                                id='word-graph',
                            ),
                        ],
                        type="default",
                    ),
                ],
            ),
            dcc.Tab(
                label="Area graph",
                children=[
                    dcc.Loading(
                        id="stream-loading",
                        children=[
                            dcc.Graph(
                                id='stream-graph',
                            ),
                        ],
                        type="default",
                    ),
                ],
            ),
            dcc.Tab(
                label="Wordcloud",
                children=[
                    dcc.Loading(
                        id="loading-wordcloud",
                        children=[
                            dcc.Graph(id="wordcloud",
                                      figure=plotly_wordcloud()
                                      ),
                        ],
                        type="default",
                    )
                ],
            ),
        ],
    ),

    "Chunk Count:",
    dcc.Input(id="chunks", type="number", value=30, min=1, max=len(words)),
    dcc.Slider(id="slider", min=1, max=100, value=30, step=1, marks={i: '{}'.format(i) for i in range(0, 101, 10)}),
    dbc.Row([
        dbc.Col([
            dcc.Input(id="filter",
                      placeholder="Filter...",
                    #   className="ag-theme-alpine-dark",
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
                className="ag-theme-alpine-dark",
                )
            ],
            md=11
        ),
    ]),
    
    dag.AgGrid(
        id="table",
        # className="ag-theme-alpine-dark",
        columnDefs=columnDefs,
        # rowData=sortedDF.to_dict("records"),
        # selectedRows=[sortedDF.head(n=3).to_dict("records")],
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
    Input("slider", "drag_value"),
    Input("chunks", "value"),
)
def updateChunks(sliderVal, sliderDrag, chunks):
    if ctx.triggered_id == 'chunks':
        return chunks, chunks
    else:
        return sliderDrag, sliderVal


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
        Input('slider', 'value')
)
def update_data(input_value, chunkCount):

    if (not chunkCount):
        raise PreventUpdate

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
    Output('table', 'rowData'),
    Output('table', 'selectedRows'),
    Output('dropfilter', 'value'),
    Input('speakers1', 'value'),
    Input('speakers2', 'value'),
    Input('table', 'rowData'),
    Input('table', 'selectedRows'),
    Input('dropfilter', 'value'),

)
def update_selection_table(speaker1, speaker2, data, tableSelected, dropSelected):  
    myDF = pd.DataFrame(data)
    if (tableSelected == None):
        myDF = pd.DataFrame(sortedDF)  
        tableSelected = myDF.head(3).to_dict("records")
    
    if (ctx.triggered_id == 'speakers1' or ctx.triggered_id == 'speakers2' or not data):
        myDF = pd.DataFrame(sortedDF) 
        wordCountDF = wordDF.groupby(["Speaker", "Word"]).size()
        selected = [row['Word'] for row in tableSelected]
        if speaker1:
            speaker1DF = pd.DataFrame(pd.concat([wordCountDF[person] for person in speaker1]), columns=['Speaker 1'])
            myDF = myDF.merge(speaker1DF.groupby('Word').sum(), how='left', on='Word')
        if speaker2:
            speaker2DF = pd.DataFrame(pd.concat([wordCountDF[person] for person in speaker2], keys=['Word']), columns=['Speaker 2'])
            myDF = myDF.merge(speaker2DF.groupby('Word').sum(), how='left', on='Word')
        dropSelected = selected
        tableSelected = myDF[myDF['Word'].isin(selected)].to_dict("records")
    elif (ctx.triggered_id == 'table'):
        dropSelected = [row['Word'] for row in tableSelected]
    elif (ctx.triggered_id == 'dropfilter'):
        tableSelected = myDF[myDF['Word'].isin(dropSelected)].to_dict("records")

    return myDF.to_dict("records"), tableSelected, dropSelected


@callback(
    Output('word-graph', 'figure'),
    Output('stream-graph', 'figure'),
    Input('table', 'selectedRows'),
    Input('textdf', 'data'),
    Input('speakers1', 'value'),
    Input('speakers2', 'value'),

)
def update_figure(words_selected, input_data, speaker1, speaker2):

    df = pd.DataFrame(input_data, columns=['Chunk', 'Word', 'Amount', 'Speaker', 'Colour'])
    
    words = [row['Word'] for row in words_selected]
    colourDict = {word: genCol(word) for word in words}
    
    df = df[df['Word'].isin(words)]
    df = df.loc[df['Speaker'].isin(speaker1+speaker2)]
    df.loc[df.Speaker.isin(speaker2), "Amount"] = -df[df.Speaker.isin(speaker2)].Amount.values
    wordFig = px.bar(df, x = "Chunk", y="Amount", color="Word", hover_name="Word", color_discrete_map=colourDict,
                hover_data={'Chunk':False, 
                            #  'Chunk ':df["Chunk"].apply(lambda x:f' {x}'),
                                'Word':False,
                                'Amount':False, 
                                'Amount ':df["Amount"].abs().apply(lambda x:f' {x}')}, 
                                barmode="relative",
                                )

    wordFig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        transition_duration=500,
        yaxis={"showticklabels": False}
    )

    streamDF = pd.DataFrame(df)
    streamDF['Amount'] = streamDF['Amount'].abs()

    streamFig = px.area(streamDF, x = "Chunk", y="Amount", color="Word", line_group="Speaker", color_discrete_map=colourDict)
    for i in range(len(streamFig['data'])):
        streamFig['data'][i]['line']['width']=0
        streamFig['data'][i]['fillcolor'] = streamFig['data'][i]['line']['color']
    
    streamFig.update_layout(
        font={"family": "Balto"},
        xaxis={
            "ticklen": 4, 
            "showgrid": False, 
            "showline": True, 
            "tickfont": {"size": 11},      
            "showticklabels": True
        }, 
        yaxis={
            "ticklen": 4, 
            "showgrid": False, 
            "showline": True, 
            "tickfont": {"size": 11}, 
            "showticklabels": True
        },
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        transition_duration=500,
    )

    return wordFig, streamFig


if __name__ == '__main__':
    app.run(debug=True)
    #os.kill(os.getpid(), signal.SIGTERM)