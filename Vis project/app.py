from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
from IPython.display import display, HTML
import pandas as pd
import os
import signal
import textExtraction as ext
import math

app = Dash(__name__)

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
chunkSize = 50
chunkCount = math.floor(len(words)/chunkSize)

print(speakers)


# words = ['SomeAnnouncer', 'This', 'is', 'an', 'intense', 'debate', 'between', 'two', 'fellas.', "Let's", 'us', 'see', 'what', 'they', 'have', 'to', 'say', 'about', 'politics.', 'Fella', '1', 'I', 'am', 'right,', 'and', 'you', 'are', 'wrong.', 'Fella', '2', 'No!', "You're", 'fake', 'news.', 'I', 'am', 'real', 'news!!!', 'Fella', '1', 'Come', 'on,', 'man!', "Don't", 'be', 'a', 'dumdum.', 'Fella', '2', 'Fake', 'news!', 'Fake', 'news!', "You're", 'fake', 'news!']
wordSections = list(divide_chunks(words, chunkSize))


# textdf = pd.DataFrame({
#     "Chunk": [1,2,3, 6, 7, 8, 9],
#     "Word": ["Fraud","Fraud","Fraud", "abortion", "abortion", "abortion", "abortion"],
#     "Amount": [2, 5, 3, 1, 4, 7, 3]

# })


app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[   
    dcc.Dropdown(list(set(words)),
                     id="dropdown",
                     multi=True),
    dcc.Graph(
        id='word-graph'
        
    ),
    dcc.Store(id='textdf')
])

@callback(
        Output('textdf', 'data'),
        Input('dropdown', 'value'),
        Input('textdf', 'data')
)
def update_data(input_value, input_data):
    
    df = pd.DataFrame(input_data)

    if (not input_value):
        return input_data
    
    word = input_value[len(input_value)-1]

    if (df.empty == False and word in df["Word"].values):
        return input_data

    

    for i, chunk in enumerate(wordSections):
        amount = chunk.count(word)
        if amount != 0:
            row = pd.Series({'Chunk': i+1, 'Word': word, 'Amount': amount}).to_frame().T
            df = pd.concat([df, row], ignore_index=True)

    return df.to_dict('records')

@callback(
    Output('word-graph', 'figure'),
    Input('dropdown', 'value'),
    Input('textdf', 'data')
)
def update_figure(words_selected, input_data):

    df = pd.DataFrame(input_data)
    
    if (not input_data):
        return {}
    
    df = df[df['Word'].isin(words_selected)]

    fig = px.bar(df, x = "Chunk", y="Amount", color="Word", barmode="relative", range_x=(0,chunkCount+1)).update_traces(width = 0.7)

    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        yaxis = dict(range=[-5,5],),
        transition_duration=500
    )

    return fig


if __name__ == '__main__':
    app.run(debug=True)
    #os.kill(os.getpid(), signal.SIGTERM)

