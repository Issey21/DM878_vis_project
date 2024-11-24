from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
from IPython.display import display, HTML
import pandas as pd
import os
import signal

app = Dash(__name__)

colors = {
    'background': '#FFFFFF',
    'text': '#241251'
}

# Functions
def divide_chunks(l, n):
    
    # looping till length l
    for i in range(0, len(l), n): 
        yield l[i:i + n]


transcript = ['SomeAnnouncer', 'This', 'is', 'an', 'intense', 'debate', 'between', 'two', 'fellas.', "Let's", 'us', 'see', 'what', 'they', 'have', 'to', 'say', 'about', 'politics.', 'Fella', '1', 'I', 'am', 'right,', 'and', 'you', 'are', 'wrong.', 'Fella', '2', 'No!', "You're", 'fake', 'news.', 'I', 'am', 'real', 'news!!!', 'Fella', '1', 'Come', 'on,', 'man!', "Don't", 'be', 'a', 'dumdum.', 'Fella', '2', 'Fake', 'news!', 'Fake', 'news!', "You're", 'fake', 'news!']
wordSections = list(divide_chunks(transcript, 5))


# textdf = pd.DataFrame({
#     "Chunk": [1,2,3, 6, 7, 8, 9],
#     "Word": ["Fraud","Fraud","Fraud", "abortion", "abortion", "abortion", "abortion"],
#     "Amount": [2, 5, 3, 1, 4, 7, 3]

# })


app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[   
    dcc.Dropdown(transcript,
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
    dff = df[df['Word'].isin(words_selected)]

    fig = px.bar(dff, x = "Chunk", y="Amount", color="Word", barmode="relative")

    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        yaxis = dict(range=[-10,10],),
        xaxis = dict(range=[0,10],)
    )

    return fig


if __name__ == '__main__':
    app.run(debug=True)
    #os.kill(os.getpid(), signal.SIGTERM)

