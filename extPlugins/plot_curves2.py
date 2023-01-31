import requests
from operator import itemgetter
import datetime

from PIL import Image
import io

import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio


async def searchIt(searchQuery: str) -> dict | int:
    # Here we define our query as a multi-line string
    query = '''
query ($id: Int, $search: String) { # Define which variables will be used in the query (id)
    Media (id: $id, search: $search, type: ANIME, sort: POPULARITY_DESC) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
        id
        title {
            english
            romaji
        }
        averageScore
        startDate {
            year
            month
            day
        }
        endDate {
            year
            month
            day
        }
        coverImage {
            large
        }
        status

    }
}

    '''

    # Define our query variables and values that will be used in the query request
    variables = {
        'search': searchQuery
    }

    url = 'https://graphql.anilist.co'

    # Make the HTTP Api request
    response = requests.post(url, json={'query': query, 'variables': variables})
    if response.status_code == 200:
        print("Successfull connection")
        data = response.json()['data']['Media']
        id = data['id']
        name = data['title']['english'] or data['title']['romaji']
        # print(f"\n\nSeries is {name}\n\n")
        # print(data)
        lower_limit = datetime.datetime(data['startDate']['year'], data['startDate']['month'], data['startDate']['day'], 0, 0)
        if datetime.datetime.now() < lower_limit:
            print("Unaired stuff sir")
        lower_limit = lower_limit - datetime.timedelta(days=7)
        if data['endDate']['year']:
            upper_limit = datetime.datetime(data['endDate']['year'], data['endDate']['month'], data['endDate']['day'], 0, 0) + datetime.timedelta(days=7)
        else:
            upper_limit = datetime.datetime.now()

    else:
        print(response.json()['errors'])
        return response.status_code

    '''Fetching the trend values '''
    req = requests.Session()
    # id = input("Enter id. ")
    trend_score = []
    flag = True
    counter = 1 

    while flag:    
        query = '''
        query ($id: Int, $page: Int, $perpage: Int, $date_greater: Int, $date_lesser: Int) {
        Page (page: $page, perPage: $perpage) { 
            pageInfo {
                total
                hasNextPage
            }
            mediaTrends (mediaId: $id, date_greater: $date_greater, date_lesser: $date_lesser) {
            mediaId
            date
            trending
            averageScore
            episode
            }
            }
        }
        '''
        
        variables = {
            "id": id
            , "page" : counter
            , "perpage": 50
            , "date_greater": lower_limit.timestamp() 
            , "date_lesser": int(upper_limit.timestamp())
        }

        response = req.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})
        # print(response.json())
        
        
        
    # response.json()['data']['Page']['mediaTrends']
        if response.status_code == 200:
            # print(response.json())
            if not response.json()['data']['Page']['pageInfo']['hasNextPage']:
                flag=False
            else:
                counter = counter + 1
            
            for item in response.json()['data']['Page']['mediaTrends']:
                trend_score.append(item)
        else: 
            # print("ERROR")
            print(response.json()['errors'])
            return response.status_code
            break

    '''Parsing the values'''
    # from datetime import datetime

    dates = []
    trends = []
    scores = []

    episode_entries = []
    trends2 = []
    dates2 = []

    for value in trend_score:
        if value['episode']:
            episode_entries.append(value)

    for value in sorted(episode_entries, key=itemgetter("date")):
        # dates.append(datetime.fromtimestamp(value['date']))
        trends2.append(value['trending'])
        dates2.append(datetime.datetime.fromtimestamp(value['date']))
            
    for value in sorted(trend_score, key=itemgetter("date")):
        dates.append(datetime.datetime.fromtimestamp(value['date']))
        trends.append(value['trending'])
        if value['averageScore']:
            scores.append(value['averageScore'])

    # print(scores[0:5])

    '''Creating the plots'''

    # Create random data with numpy
    

    pio.renderers.default = "notebook"

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])


    x_axis = np.array(dates)

    y_axis = np.array(trends)

    # scores_np = np.array(scores)

    # Create traces
    # fig = go.Figure()
    go.Figure
    return dict(name = name, data = [dates, trends, dates2, trends2, dates[-len(scores): ], scores])
    #     # "name": name,
    #     # "data": [dates, trends, dates2, trends2, dates[-len(scores): ], scores]
        
    # fig.add_trace(go.Scatter(x=x_axis, y=y_axis,
    #                     mode='lines',
    #                     name='Trends',
    #                     line = dict(color='MediumTurquoise', width=2.5,)))

    # fig.add_trace(go.Scatter(x=dates2, y=trends2,
    #                     mode='markers',
    #                     name='Episodes',
    #                     line = dict(color ='DarkTurquoise', width=2.5,)))

    # fig.add_trace(
    #     go.Scatter(x=dates[-len(scores): ], y=scores, line=dict(color="DeepPink"),name="Scores", mode='lines', line_shape='spline'),
    #     secondary_y=True,
    # )

    # fig.update_layout(title=f'Series Trends: {name}',
    #                 xaxis_title='Dates',
    #                 yaxis_title='Trend Value',
    #                 template="plotly_dark")

    # fig.update_yaxes(title_text="Score", secondary_y=True)
    # # print(type(fig) == go.Figure)
    # return fig
    # plotly.graph_objects


if __name__ == "__main__":
    img_bytes = graphit(input("Enter query. \n>")).to_image(format="png")
        # img_bytes = fig.to_image(format="png")

    Image.open(io.BytesIO(img_bytes)).show()