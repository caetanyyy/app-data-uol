import streamlit as st
import altair as alt
import numpy as np
import pandas as pd
import streamlit.components.v1 as components
import plotly.graph_objects as go
from urllib.request import urlopen
import json
import plotly as plt
import plotly.express as px
#from sklearn.decomposition import PCA
#from scipy.spatial.distance import pdist, squareform

def read_data(uploaded_file):
  try:
      db = pd.read_csv(uploaded_file)
  except:
      st.write('Arquivo fora do formato padrão de csv.')
  db.columns = [str(i) for i in list(db.columns)]
  return db

def generate_location_map(db, width, height):
    with urlopen('https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson') as response:
        Brazil = json.load(response) # Javascrip object notation 

    state_id_map = {}
    for feature in Brazil ['features']:
        feature['id'] = feature['properties']['name']
        state_id_map[feature['properties']['sigla']] = feature['id']
    
    db_count = db[['Estado']].value_counts().reset_index()
    db_unique = db[['Estado','Longitude','Latitude']].drop_duplicates().reset_index()
    db_count = db_count.merge(db_unique, on = 'Estado', how = 'left')

    fig = px.choropleth_mapbox(
        db_count,
        locations = 'Estado', #define the limits on the map/geography
        geojson = Brazil, #shape information
        color = 'count', #defining the color of the scale through the database
        hover_name = 'Estado', #the information in the box
        hover_data =["count","Estado","Longitude","Latitude"],
        title = "Produtivida da soja (Toneladas)", #title of the map
        mapbox_style = "carto-positron", #defining a new map style 
        center={"lat":-14, "lon": -55},#define the limits that will be plotted
        zoom = 3, #map view size
        opacity = 0.3, #opacity of the map color, to appear the background,
        color_continuous_midpoint=int(db_count['count'].max()/2),
        range_color=(0, db_count['count'].max())
    )

    fig.update_layout(
            width = width,
            height = height,
            margin={"r":0,"t":0,"l":0,"b":0}
        )

    return fig

def generate_bar_chart_2(db, field, width, height):
    field_emoji = {
        'Qual é o seu departamento?':{
            'Parcerias':'🤝', 
            'RH':'👥', 
            'Produtos Digitais':'🌐', 
            'Financeiro':'💸', 
            'Jurídico':'⚖️',
            'Conteúdo':'📝', 
            'Operações':'⚙️', 
            'Marketing':'🎯', 
            'Publicidade':'📢', 
            'Atendimento':'☎️',
            'Data & Analytics':'🎲', 
            'Segurança':'🔐', 
            'Inovação':'💡', 
            'Ingresso.com':'🍿',
            'Host':'📦', 
            'P&D':'🛍️',
            'Outro':'Outro'
        }
    }

    
    db_chart = db[field].value_counts().reset_index()
    db_chart['perc'] = (100*(db_chart['count']/db_chart['count'].sum())).astype(int).astype(str) + '%' + ' ' + db_chart[field]
    db_chart = db_chart#.head(7)
    sort = list(db_chart[field].values)
    db_chart['emoji'] = db_chart[field].map(field_emoji[field])

    bar_chart = alt.Chart(db_chart).mark_bar(
        opacity=1,
        stroke='black',
        strokeWidth=3,
        strokeOpacity=1,
        color = '#FF8000'
    ).encode(
        y = alt.Y(field).sort(sort).title(None).axis(values = []),
        x = alt.X('count').title(None),
        tooltip = ['count','emoji',field]
    ).properties(
        title = field, width = width, height = height
    )

    emoji =  alt.Chart(db_chart).mark_text(
        size = 30,
        dx = -10,
        align = 'right'
    ).encode(
        y = alt.Y(field).sort(sort).title(None),
        x = alt.X('count').axis(
                values = []
            ).title('Contagem'),
        text = 'emoji',
        tooltip = ['count','emoji',field]
    )

    percent = alt.Chart(db_chart).mark_text(
        size = 20, 
        color = '#3255E2',
        align = 'left',
        dx = 5, 
        stroke = 'black', 
        strokeOpacity=0.3, 
        strokeWidth = 0.8
    ).encode(
        y = alt.Y(field).sort(sort).title(None),
        x = alt.X('count').axis(
                values = []
            ).title(None),
        text = 'perc',
        tooltip = ['count','emoji',field]
    )

    chart = (
        bar_chart + emoji + percent
    ).configure(
        background='white'
    ).configure_view(
        strokeWidth=0
    ).configure_axis(
        domain=False
    )
    
    return chart

def generate_working_interest(db, field, width, height):
    field_colors = {
        'Qual seu turno de preferência para reuniões de trabalho?':{
            'Manhã':'#FFCE00',
            'Começo da tarde':'#FF8000',
            'Final da tarde':'#FF0024'
        },
        'Qual o seu método de comunicação preferido no trabalho?':{
            'Chat':'#3255E2',
            'E-mail':'#6C04BA',
            'Reuniões':'#83195C',
            'Telefone':'#9F2213'
        },
         'Há quanto tempo você faz parte do grupo UOL?':{
            '<1 ano':'#FFCE00',
            '1-3 anos':'#FF8000',
            '4-6 anos':'#FF0024',
            '7-10 anos':'#83195C',
            '10+ anos':'black'
        }
    }

    field_emoji = {
        'Qual seu turno de preferência para reuniões de trabalho?':{
            'Manhã':'🌅',
            'Começo da tarde':'🌞',
            'Final da tarde':'🌇'
        },
        'Qual o seu método de comunicação preferido no trabalho?':{
            'Chat':'⌨️',
            'E-mail':'📧',
            'Reuniões':'👥',
            'Telefone':'📞'
        },
        'Há quanto tempo você faz parte do grupo UOL?':{
            '<1 ano':'🥚',
            '1-3 anos':'🐥',
            '4-6 anos':'🐔',
            '7-10 anos':'🦅',
            '10+ anos':'🦖'
        },
    }

    field_sort = {
        'Qual seu turno de preferência para reuniões de trabalho?': ['Manhã','Começo da tarde','Final da tarde'],
        'Qual o seu método de comunicação preferido no trabalho?':['Chat','E-mail','Reuniões','Telefone'],
        'Há quanto tempo você faz parte do grupo UOL?':[
            '<1 ano','1-3 anos','4-6 anos','7-10 anos', '10+ anos'
        ]
    }
    
    db_chart = db[field].value_counts().reset_index()
    db_chart['perc'] = (100*db_chart['count']/db_chart['count'].sum()).astype(int).astype(str) + '%'
    
    present_domains = [domain for domain in field_colors[field].keys() if domain in db_chart[field].unique()]
    domain_scale = alt.Scale(
            domain=present_domains,
            range=[field_colors[field][domain] for domain in present_domains],
            )

    db_chart['emoji'] = db_chart[field].map(field_emoji[field])

    bar = alt.Chart(db_chart).mark_bar(
        opacity=0.9,
        stroke='black',
        strokeWidth=2,
        strokeOpacity=0.7,
    ).encode(
        x = alt.X(
                field
            ).sort(
                field_sort[field]
            ).axis(labelAngle = -50, labelFontSize = 20, labelFontStyle = 'bold',ticks = False, labelPadding = 20
            ).title(None),
        y = alt.Y('count').title(None).axis(values = []),
        color = alt.Color(field, scale = domain_scale).legend(None)
    )

    text = alt.Chart(db_chart).mark_text(
        size = 30,
        stroke = 'white', 
        strokeOpacity=0.7, 
        strokeWidth = 1,
        align = 'center',
        dy = 30
    ).encode(
        x = alt.X(field
        ).sort(field_sort[field]).axis(values = []),
        y = alt.Y('count'),
        text = 'perc',
        color = alt.Color(field, scale = domain_scale).legend(None)
    )

    emoji =  alt.Chart(db_chart).mark_text(
        align = 'center',
        dy = -30,
        size = 50
    ).encode(
        x = alt.X(field).sort(field_sort[field]).title(None),
        y = alt.Y('count').axis(
                values = []
            ),
        text = 'emoji',
        tooltip = ['count','emoji',field]
    )

    legenda = alt.Chart(db_chart).mark_text(size = 20).encode(
        y = alt.Y(field).title(None).axis(
            labelFontSize = 10, labelFontStyle = 'bold', labelColor = '#6C04BA'
        ).sort(field_sort[field]),
        text = 'emoji'
    )

    chart = (
        ((bar + text + emoji)).properties(title = field, width =  width, height = height) | legenda
    ).configure(
        background = '#0FB1A9'
    ).configure_view(
        strokeWidth=0
    ).configure_axis(
        domain=False
    )   
    return chart

def generate_working_interest_sankey(db, width, height):
    field_emoji = {
        'Manhã':'🌅',
        'Começo da tarde':'🌞',
        'Final da tarde':'🌇',
        'Chat':'⌨️',
        'E-mail':'📧',
        'Reuniões':'👥',
        'Telefone':'📞'
    }

    db_chart = db[
        ['Qual o seu método de comunicação preferido no trabalho?','Qual seu turno de preferência para reuniões de trabalho?']
    ]

    db_chart = db_chart.value_counts().reset_index()

    db_chart.head()
    
    map_id = pd.DataFrame(
        db_chart['Qual o seu método de comunicação preferido no trabalho?'
            ].unique().tolist() + db_chart['Qual seu turno de preferência para reuniões de trabalho?'].unique().tolist()
    , columns = ['node']).reset_index().rename(columns = {'index':'id'}).set_index('node').to_dict()['id']

    map_id.keys()
    
    db_chart['source'] = db_chart['Qual seu turno de preferência para reuniões de trabalho?'].map(map_id)
    db_chart['target'] = db_chart['Qual o seu método de comunicação preferido no trabalho?'].map(map_id)
    
    fig = go.Figure(go.Sankey(
        arrangement='snap',
        node = dict(
            pad = 100,
            thickness = 50,
            line = dict(color = "#6C04BA", width = 2),
            label = [field_emoji[i] for i in map_id],
            customdata = [i + ' ' + field_emoji[i] for i in map_id],
            #align='left',
            hovertemplate = '%{customdata}',
            color = '#3255E2'
        ),
        link = dict(
            arrowlen=25,
            source = db_chart['source'].values, # indices correspond to labels, eg A1, A2, A1, B1, ...
            target = db_chart['target'].values,
            value = db_chart['count'].values,
            #hovercolor = ' #FF8000',
            color = ' #FFC4A2',
            line = dict(color = "#9F2213", width = 4)
      )))

    fig.update_layout(
        title_text=None, 
        width = width,
        height = height,
        font=dict(size = 50, color = 'white'),
        plot_bgcolor='#0FB1A9',
        paper_bgcolor='#0FB1A9'
    )

    #plot_div = plot(fig, output_type='div', include_plotlyjs=False)

    return fig

def generate_department_working_interest_chart(db, width, height):
    field_emoji = {
        'Qual seu turno de preferência para reuniões de trabalho?':{
            'Manhã':'🌅',
            'Começo da tarde':'🌞',
            'Final da tarde':'🌇'
        },
        'Qual o seu método de comunicação preferido no trabalho?':{
            'Chat':'⌨️',
            'E-mail':'📧',
            'Reuniões':'👥',
            'Telefone':'📞'
        },
        'Há quanto tempo você faz parte do grupo UOL?':{
            '<1 ano':'🥚',
            '1-3 anos':'🐥',
            '4-6 anos':'🐔',
            '7-10 anos':'🦅',
            '10+ anos':'🦖'
        }
    }
    
    field = 'Há quanto tempo você faz parte do grupo UOL?'
    
    db_chart = db[
        ['Qual é o seu departamento?',field]
    ]


    db_chart = db_chart.value_counts().reset_index(
    ).sort_values(['Qual é o seu departamento?','count'], ascending = False).reset_index(drop = True)

    db_chart['rank'] = db_chart.groupby('Qual é o seu departamento?')['count'].cumcount() + 1

    db_chart = db_chart[db_chart['rank'] == 1].reset_index(drop = True)

    db_chart['emoji'] = db_chart[field].map(field_emoji[field])

    db_chart.head()

    db_chart_0 = db_chart[['Qual é o seu departamento?',field,'emoji']].assign(x_pos = 0).rename(columns = {field:'Texto'})
    
    field = 'Qual seu turno de preferência para reuniões de trabalho?'
    
    db_chart = db[
        ['Qual é o seu departamento?',field]
    ]


    db_chart = db_chart.value_counts().reset_index(
    ).sort_values(['Qual é o seu departamento?','count'], ascending = False).reset_index(drop = True)

    db_chart['rank'] = db_chart.groupby('Qual é o seu departamento?')['count'].cumcount() + 1

    db_chart = db_chart[db_chart['rank'] == 1].reset_index(drop = True)

    db_chart['emoji'] = db_chart[field].map(field_emoji[field])

    db_chart.head()

    db_chart_1 = db_chart[['Qual é o seu departamento?',field,'emoji']].assign(x_pos = 1).rename(columns = {field:'Texto'})
    
    field = 'Qual o seu método de comunicação preferido no trabalho?'

    db_chart = db[
        ['Qual é o seu departamento?',field]
    ]

    db_chart = db_chart.value_counts().reset_index(
    ).sort_values(['Qual é o seu departamento?','count'], ascending = False).reset_index(drop = True)

    db_chart['rank'] = db_chart.groupby('Qual é o seu departamento?')['count'].cumcount() + 1

    db_chart = db_chart[db_chart['rank'] == 1].reset_index(drop = True)

    db_chart['emoji'] = db_chart[field].map(field_emoji[field])

    db_chart.head()

    db_chart_2 = db_chart[['Qual é o seu departamento?',field,'emoji']].assign(x_pos = 2).rename(columns = {field:'Texto'})
    
    db_chart = pd.concat([db_chart_0, db_chart_1,db_chart_2]).reset_index(drop = True)

    emoji = alt.Chart(db_chart).mark_text(
        size = 40

    ).encode(
        y = alt.Y('Qual é o seu departamento?'
                 ).title(None
                 ).axis(ticks = False, labelFontSize = 20, labelFontStyle = 'bold', labelAlign = 'right'
        ),
        x = alt.X('x_pos:O').title(None).axis(values = []),
        text = 'emoji',
        tooltip = ['Texto','emoji','Qual é o seu departamento?']
    ).properties(
        title = "Idade x Turno x Comunicação favorita por departamento", 
        width = width, 
        height = height
    )

    legenda = alt.Chart(db_chart[['Texto','emoji']].drop_duplicates()).mark_text(size = 20).encode(
        y = alt.Y('Texto').title(None).axis(
            labelFontSize = 10, labelFontStyle = 'bold', labelColor = '#6C04BA'
        ),
        text = 'emoji'
    )

    chart = (emoji | legenda).configure_view(
        strokeWidth=0
    ).configure_axis(
        domain=False
    )
    
    return chart

def generate_bar_chart(db, field, width, height):
    field_sort = {
        'Há quanto tempo você faz parte do grupo UOL?':[
            '<1 ano','1-3 anos','4-6 anos','7-10 anos', '10+ anos'
        ],
        'Qual bebida você prefere?':[
            'Café','Suco de Frutas','Chocolate quente','Chá','Água','Leite'
        ],
        'Qual lanche você prefere?':[
            'Salada de frutas', 'Bolo', 'Fruta', 'Sanduíche', 'Pão de Queijo'
        ]
    }

    field_colors = {
        'Há quanto tempo você faz parte do grupo UOL?':{
            '<1 ano':'#0FB1A9',
            '1-3 anos':'#FFCE00',
            '4-6 anos':'#FF8000',
            '7-10 anos':'#FF0024',
            '10+ anos':'#83195C'
        },
        'Qual bebida você prefere?':{
            'Café':'black',
            'Suco de Frutas':'#4B9B4A',
            'Chocolate quente':'#9F2213',
            'Chá':'#83195C',
            'Água':'#3255E2',
            'Leite':'#FFFFFF'
        },
        'Qual lanche você prefere?':{
            'Salada de frutas':'#0FB1A9', 
            'Bolo':' #DB5B49', 
            'Fruta':'#FF8000', 
            'Sanduíche':'#9F2213', 
            'Pão de Queijo':'#FFCE00'
        }
    }

    field_emoji = {
        'Há quanto tempo você faz parte do grupo UOL?':{
            '<1 ano':'🥚',
            '1-3 anos':'🐥',
            '4-6 anos':'🐔',
            '7-10 anos':'🦅',
            '10+ anos':'🦖'
        },
        'Qual bebida você prefere?':{
            'Café':'☕',
            'Suco de Frutas':'🧃',
            'Chocolate quente':'🍫',
            'Chá':'🍵',
            'Água':'💧',
            'Leite':'🥛'
        },
        'Qual lanche você prefere?':{
            'Salada de frutas':'🥗', 
            'Bolo':'🍰', 
            'Fruta':'🍑', 
            'Sanduíche':'🥪', 
            'Pão de Queijo':'🧀'
        }
    }
    
    db_chart = db[field].value_counts().reset_index()
    db_chart['perc'] = (100*(db_chart['count']/db_chart['count'].sum())).astype(int).astype(str) + '%' + ' ' + db_chart[field]


    present_domains = [domain for domain in field_colors[field].keys() if domain in db_chart[field].unique()]
    domain_scale = alt.Scale(
            domain=present_domains,
            range=[field_colors[field][domain] for domain in present_domains],
            )

    db_chart['emoji'] = db_chart[field].map(field_emoji[field])

    bar_chart = alt.Chart(db_chart).mark_bar(
        opacity=0.7,
        stroke='black',
        strokeWidth=2,
        strokeOpacity=0.7,
    ).encode(
        y = alt.Y(field).sort(field_sort[field]).title(None).axis(values = []),
        x = alt.X('count').title(None),
        color = alt.Color(field, scale = domain_scale).legend(None)
    ).properties(
        title = field, width = width, height = height
    )

    emoji =  alt.Chart(db_chart).mark_text(
        size = 50
    ).encode(
        y = alt.Y(field).sort(field_sort[field]).title(None),
        x = alt.X('count').axis(
                values = []
            ).title('Contagem'),
        text = 'emoji',
        tooltip = ['count','emoji',field]
    )

    percent = alt.Chart(db_chart).mark_text(
        size = 20, 
        align = 'left',
        dx = 30, 
        stroke = 'black', 
        strokeOpacity=0.6, 
        strokeWidth = 0.8
    ).encode(
        y = alt.Y(field).sort(field_sort[field]).title(None),
        x = alt.X('count').axis(
                values = []
            ).title(None),
        text = 'perc',
        color = alt.Color(field, scale = domain_scale).legend(None)
    )

    chart = (
        bar_chart + emoji + percent
    ).configure(
        background='#FFC4A2'
    ).configure_view(
        strokeWidth=0
    ).configure_axis(
        domain=False
    )
    
    return chart

def generate_interest_chart(db, field, width, height):
    field_emoji = {
        'Qual seu gênero preferido de música? (Pode marcar mais de um)':{
            'Eletrônica':'🎛️',
            'Sertanejo':'🤠',
            'Pop':'🎤',
            'Rock':'🎸',
            'MPB':'🎻',
            'Jazz':'🎷' ,
            'Funk':'😈',
            'Rap':'📀',
            'Clássica':'🎼' 
        },
        'Qual seu gênero de filme preferido? (Pode marcar mais de um)':{
            'Ação':'💥',
            'Terror':'💀',
            'Drama':'🎭',
            'Ficção Científica':'🤖',
            'Documentário':'🎥',
            'Comédia':'🤣' ,
            'Romance':'💕',
            'Animação':'🎨'
        },
        'Qual hobby você prefere?':{
            'Jogos':'🎮', 
            'Leitura':'📖', 
            'Viajar':'✈️', 
            'Esportes':'🏐', 
            'Cozinhar':'🍳',
            'Assistir TV ou Cinema':'📺'
        }
    }
    
    db_chart = db[field].str.split(';').explode().value_counts().reset_index()
    sort = db_chart[field].values
    soma = db_chart['count'].sum()
    db_chart['perc'] = (
        100*db_chart['count']/soma).astype(int).astype(str) + '% ' + db_chart[field]
    db_chart['count'] = (db_chart['count']).round().astype(int)
    db_chart['contagem'] = (db_chart['count']).round().astype(int)

    db_genero = pd.DataFrame()
    for i, r in db_chart.iterrows():
        mul = pd.MultiIndex.from_product([
            [r[field]], 
            np.arange(0,r['count'] + 1)])
        db_genero_aux = pd.DataFrame(index = mul).reset_index().rename(columns = {'level_0':field,'level_1':'contagem'})
        db_genero_aux['emoji'] = db_genero_aux[field].map(field_emoji[field])
        db_genero = pd.concat([db_genero,db_genero_aux]).reset_index(drop = True)

    db_genero['contagem'] = db_genero['contagem'].astype(int)

    
    emoji = alt.Chart(db_genero).mark_text(
        size = 30
    ).encode(
        y = alt.Y(field).title(None).axis(values = []).sort(sort),
        x = alt.X('contagem:O').axis(
                values = []
            ),
        text = 'emoji',
    )

    perc = alt.Chart(db_chart).mark_text(
        size = 30, 
        align = 'left',
        dx = 30, 
        stroke = 'black', 
        color =  ' #DB5B49',
        strokeOpacity=0.6, 
        strokeWidth = 0.5
    ).encode(
        y = alt.Y(field).title(None).sort(sort),
        x = alt.X('contagem:O').axis(
                values = []
            ).title(None),
        text = 'perc',
    )

    chart = (emoji + perc).properties(
        title = "", 
        width = width,
        height = height
    ).configure(
    ).configure_view(
        strokeWidth=0
    ).configure_axis(
        domain=False
    )
    
    return chart

def generate_department_interest_hobby_chart(db, width, height):
    field_emoji = {
        'Qual seu gênero preferido de música? (Pode marcar mais de um)':{
            'Eletrônica':'🎛️',
            'Sertanejo':'🤠',
            'Pop':'🎤',
            'Rock':'🎸',
            'MPB':'🎻',
            'Jazz':'🎷' ,
            'Funk':'😈',
            'Rap':'📀',
            'Clássica':'🎼' 
        },
        'Qual seu gênero de filme preferido? (Pode marcar mais de um)':{
            'Ação':'💥',
            'Terror':'💀',
            'Drama':'🎭',
            'Ficção Científica':'🤖',
            'Documentário':'🎥',
            'Comédia':'🤣' ,
            'Romance':'💕',
            'Animação':'🎨'
        },
        'Qual hobby você prefere?':{
            'Jogos':'🎮', 
            'Leitura':'📖', 
            'Viajar':'✈️', 
            'Esportes':'🏐', 
            'Cozinhar':'🍳',
            'Assistir TV ou Cinema':'📺'
        }
    }
    
    # Hobby
    field = 'Qual hobby você prefere?'
    
    db_chart = db[
        ['Qual é o seu departamento?',field]
    ]

    db_chart[
        field
    ] = db_chart[field].str.split(';')

    db_chart = db_chart.explode(
        field
    ).value_counts().reset_index().sort_values(['Qual é o seu departamento?','count'], ascending = False).reset_index(drop = True)

    db_chart['rank'] = db_chart.groupby('Qual é o seu departamento?')['count'].cumcount() + 1

    db_chart = db_chart[db_chart['rank'] == 1].reset_index(drop = True)

    db_chart['emoji'] = db_chart[field].map(field_emoji[field])

    db_chart.head()

    db_chart_0 = db_chart[['Qual é o seu departamento?',field,'emoji']].assign(x_pos = 0).rename(columns = {field:'Texto'})
    
    # Musica
    field = 'Qual seu gênero preferido de música? (Pode marcar mais de um)'
    
    db_chart = db[
        ['Qual é o seu departamento?',field]
    ]

    db_chart[
        field
    ] = db_chart[field].str.split(';')

    db_chart = db_chart.explode(
        field
    ).value_counts().reset_index().sort_values(['Qual é o seu departamento?','count'], ascending = False).reset_index(drop = True)

    db_chart['rank'] = db_chart.groupby('Qual é o seu departamento?')['count'].cumcount() + 1

    db_chart = db_chart[db_chart['rank'] == 1].reset_index(drop = True)

    db_chart['emoji'] = db_chart[field].map(field_emoji[field])

    db_chart.head()

    db_chart_1 = db_chart[['Qual é o seu departamento?',field,'emoji']].assign(x_pos = 1).rename(columns = {field:'Texto'})
    
    # Filme
    field = 'Qual seu gênero de filme preferido? (Pode marcar mais de um)'

    db_chart = db[
        ['Qual é o seu departamento?',field]
    ]

    db_chart[
        field
    ] = db_chart[field].str.split(';')

    db_chart = db_chart.explode(
        field
    ).value_counts().reset_index().sort_values(['Qual é o seu departamento?','count'], ascending = False).reset_index(drop = True)

    db_chart['rank'] = db_chart.groupby('Qual é o seu departamento?')['count'].cumcount() + 1

    db_chart = db_chart[db_chart['rank'] == 1].reset_index(drop = True)

    db_chart['emoji'] = db_chart[field].map(field_emoji[field])

    db_chart.head()

    db_chart_2 = db_chart[['Qual é o seu departamento?',field,'emoji']].assign(x_pos = 2).rename(columns = {field:'Texto'})
    
    db_chart = pd.concat([db_chart_0, db_chart_1,db_chart_2]).reset_index(drop = True)

    emoji = alt.Chart(db_chart).mark_text(
        size = 40

    ).encode(
        y = alt.Y('Qual é o seu departamento?'
                 ).title(None
                 ).axis(ticks = False, labelFontSize = 20, labelFontStyle = 'bold', labelAlign = 'right'
        ),
        x = alt.X('x_pos:O').title(None).axis(values = []),
        text = 'emoji',
        tooltip = ['Texto','emoji','Qual é o seu departamento?']
    ).properties(
        title = "Hobby x Música x Filme favorito por departamento", 
        width = width, 
        height = height
    )

    legenda = alt.Chart(db_chart[['Texto','emoji']].drop_duplicates()).mark_text(size = 20).encode(
        y = alt.Y('Texto').title(None).axis(
            labelFontSize = 10, labelFontStyle = 'bold', labelColor = '#6C04BA'
        ),
        text = 'emoji'
    )

    chart = (emoji | legenda).configure_view(
        strokeWidth=0
    ).configure_axis(
        domain=False
    )
    
    return chart

def create_similarity_data(db):
    db_ = db[['Id','Qual seu gênero preferido de música? (Pode marcar mais de um)']]
    db_['Qual seu gênero preferido de música? (Pode marcar mais de um)'] = db_['Qual seu gênero preferido de música? (Pode marcar mais de um)'].str.split(';')
    db_ = db_.explode('Qual seu gênero preferido de música? (Pode marcar mais de um)')
    db_['valor'] = True
    db_music = db_.pivot_table(index = 'Id', columns = 'Qual seu gênero preferido de música? (Pode marcar mais de um)', values = 'valor'
                              ).fillna(False)

    db_ = db[['Id','Qual seu gênero de filme preferido? (Pode marcar mais de um)']]#
    db_['Qual seu gênero de filme preferido? (Pode marcar mais de um)'] = db_['Qual seu gênero de filme preferido? (Pode marcar mais de um)'].str.split(';')
    db_ = db_.explode('Qual seu gênero de filme preferido? (Pode marcar mais de um)')
    db_['valor'] = True
    db_movie = db_.pivot_table(index = 'Id', columns = 'Qual seu gênero de filme preferido? (Pode marcar mais de um)', values = 'valor'
                              ).fillna(False)

    db_sim = pd.concat([
        pd.get_dummies(db.set_index('Id')[[
        'Há quanto tempo você faz parte do grupo UOL?',
        'Qual lanche você prefere?',
        'Cidade',
        'Estado',
        'Qual o seu método de comunicação preferido no trabalho?',
        'Qual seu turno de preferência para reuniões de trabalho?',
        ]]), 
        db_movie, db_music
                    ], axis = 1).replace({True:1,False:0})

    pca = PCA(n_components=10)
    db_pca = pd.DataFrame(pca.fit_transform(db_sim))

    from scipy.spatial.distance import pdist,squareform
    db_sim = pd.DataFrame(1/(1+squareform(pdist(db_pca))))
    db_sim = db_sim.reset_index().melt(id_vars = 'index')
    db_sim = db_sim[db_sim['index']!=db_sim['variable']].reset_index(drop = True)
    db_sim = db_sim.rename(columns = {'index':'Id1','variable':'Id2','value' : 'similarity'})
    db_sim = db_sim[db_sim['similarity'] > db_sim['similarity'].quantile(0.7)].reset_index(drop = True)

    db_sim = db_sim.merge(db[['Id','Qual é o seu departamento?']].rename(
        columns = {'Id':'Id1','Qual é o seu departamento?':'Departamento Id1'})
                         )
    db_sim = db_sim.merge(
        db[['Id','Qual é o seu departamento?']].rename(columns = {'Id':'Id2','Qual é o seu departamento?':'Departamento Id2'})
    )

    db_sim['aux'] = db_sim.apply(lambda x: sorted([x['Id1'], x['Id2']]), axis = 1)
    db_sim = db_sim.drop_duplicates('aux').drop(columns = 'aux').reset_index(drop = True)

    return db_sim

def generate_bar_chart_similarity_department(db_chart, width, height):
    field = 'Departamento'
    field_emoji = {
        'Departamento':{
            'Parcerias':'🤝', 
            'RH':'👥', 
            'Produtos Digitais':'🌐', 
            'Financeiro':'💸', 
            'Jurídico':'⚖️',
            'Conteúdo':'📝', 
            'Operações':'⚙️', 
            'Marketing':'🎯', 
            'Publicidade':'📢', 
            'Atendimento':'☎️',
            'Data & Analytics':'🎲', 
            'Segurança':'🔐', 
            'Inovação':'💡', 
            'Ingresso.com':'🍿',
            'Host':'📦', 
            'P&D':'🛍️'
        }
    }
    
    db_chart['perc'] = (100*(db_chart['count']/db_chart['count'].sum())).astype(int).astype(str) + '%' + ' ' + db_chart[field]
    db_chart = db_chart#.head(7)
    sort = list(db_chart[field].values)
    db_chart['emoji'] = db_chart[field].map(field_emoji[field])

    bar_chart = alt.Chart(db_chart).mark_bar(
        opacity=1,
        stroke='black',
        strokeWidth=3,
        strokeOpacity=1,
        color = 'white'
    ).encode(
        y = alt.Y(field).sort(sort).title(None).axis(values = []),
        x = alt.X('count').title(None),
    ).properties(
        title = 'Similaridade entre membros dos departamentos', width = width, height = height
    )

    emoji =  alt.Chart(db_chart).mark_text(
        size = 30,
        dx = -10,
        align = 'right'
    ).encode(
        y = alt.Y(field).sort(sort).title(None),
        x = alt.X('count').axis(
                values = []
            ).title('Contagem'),
        text = 'emoji',
        tooltip = ['count','emoji',field]
    )

    percent = alt.Chart(db_chart).mark_text(
        size = 20, 
        color = '#3255E2',
        align = 'left',
        dx = 5, 
        stroke = 'black', 
        strokeOpacity=0.3, 
        strokeWidth = 0.8
    ).encode(
        y = alt.Y(field).sort(sort).title(None),
        x = alt.X('count').axis(
                values = []
            ).title(None),
        text = 'perc',
    )

    chart = (
        bar_chart + emoji + percent
    ).configure(
        background='#FF8000'
    ).configure_view(
        strokeWidth=0
    ).configure_axis(
        domain=False
    )
    
    return chart

def main():
    #db = read_data(uploaded_file)
    db = pd.read_csv('https://raw.githubusercontent.com/caetanyyy/app-data-uol/main/dados_padronizados.csv')
    db = db.rename(columns = {'ID':'Id'})
    db['Qual é o seu departamento?' ] = db['Qual é o seu departamento?'].map(
        {   'Parcerias': 'Parcerias', 
            'RH':'RH', 
            'Produtos Digitais':'Produtos Digitais', 
            'Financeiro':'Financeiro', 
            'Jurídico':'Jurídico',
            'Conteúdo':'Conteúdo', 
            'Operações':'Operações', 
            'Marketing':'Marketing', 
            'Publicidade':'Publicidade', 
            'Atendimento':'Atendimento',
            'Data & Analytics':'Data & Analytics', 
            'Segurança':'Segurança', 
            'Inovação':'Inovação', 
            'Ingresso.com':'Ingresso.com',
            'Host':'Host', 
            'P&D':'P&D'
        }
    ).fillna('Outro')
    if db is not None:
      st.subheader("Dados carregados:")
      st.write(db)
      public(db)
      coffe_break(db)
      hobby(db)
      #similarity(db)
    
def public(db):
    st.header('Como é o público do evento?')
    h_buffer = 100
    w_buffer = 200

    width = 800
    height = 400
    
    chart = generate_location_map(db, width, height)
    st.plotly_chart(chart, theme = None)
    
    width = 600
    height = 900

    field = 'Qual é o seu departamento?'
    chart = generate_bar_chart_2(db, field, width, height)
    components.html(
        chart.to_html(),
        height = height + h_buffer,
        width = width + w_buffer,
    )

    width = 600
    height = 400
    field = 'Há quanto tempo você faz parte do grupo UOL?'
    chart = generate_working_interest(db, field, width, height)
    components.html(
        chart.to_html(),
        height = height + h_buffer,
        width = width + w_buffer,
    )

    field = 'Qual seu turno de preferência para reuniões de trabalho?'
    chart = generate_working_interest(db, field, width, height)
    components.html(
        chart.to_html(),
        height = height + h_buffer,
        width = width + w_buffer,
    )

    field = 'Qual o seu método de comunicação preferido no trabalho?'
    chart = generate_working_interest(db, field, width, height)
    components.html(
        chart.to_html(),
        height = height + h_buffer,
        width = width + w_buffer,
    )


    width = 700
    height = 600
    chart = generate_working_interest_sankey(db, width, height)

    components.html(
        chart.to_html(),
        height = height + h_buffer,
        width = width + w_buffer,
    )

    width = 200
    height = 900
    chart = generate_department_working_interest_chart(db, width, height)
    components.html(
        chart.to_html(),
        height = height + h_buffer,
        width = width + w_buffer,
    )

def coffe_break(db):
    st.header('Coffee Break')
    h_buffer = 100
    w_buffer = 200

    width = 500
    height = 300
    
    field = 'Qual lanche você prefere?'#['Qual bebida você prefere?','Há quanto tempo você faz parte do grupo UOL?','Qual lanche você prefere?']
    chart = generate_bar_chart(db, field, width, height)   
    components.html(
        chart.to_html(),
        height = height+ h_buffer,
        width = width + w_buffer,
    )

    field = 'Qual bebida você prefere?'#['Qual bebida você prefere?','Há quanto tempo você faz parte do grupo UOL?','Qual lanche você prefere?']
    chart = generate_bar_chart(db, field, width, height)   
    components.html(
        chart.to_html(),
        height = height + h_buffer,
        width = width + w_buffer,
    )

def hobby(db):
    st.header('Hobby')
    h_buffer = 100
    w_buffer = 400

    width = 300
    height = 300
    
    field = 'Qual hobby você prefere?'
    chart = generate_interest_chart(db, field, width, height)
    components.html(
        chart.to_html(),
        height = height + h_buffer,
        width = width + w_buffer,
    )

    width = 300
    height = 400
    field = 'Qual seu gênero preferido de música? (Pode marcar mais de um)'
    chart = generate_interest_chart(db, field, width, height)
    components.html(
        chart.to_html(),
        height = height + h_buffer,
        width = width + w_buffer,
    )

    width = 300
    height = 400
    field = 'Qual seu gênero de filme preferido? (Pode marcar mais de um)'
    chart = generate_interest_chart(db, field, width, height)
    components.html(
        chart.to_html(),
        height = height + h_buffer,
        width = width + w_buffer,
    )

    width = 200
    height = 900
    
    chart = generate_department_interest_hobby_chart(db, width, height)
    components.html(
        chart.to_html(),
        height = height + h_buffer,
        width = width + w_buffer,
    )

def similarity(db):
    st.header('Similaridade entre participantes')
    h_buffer = 100
    w_buffer = 200

    width = 500
    height = 300
    db_sim = create_similarity_data(db)

    sim_departamento = (
        db_sim[db_sim['Departamento Id1'] == db_sim['Departamento Id2']].groupby('Departamento Id1')['Id1'].nunique(
        )/db['Qual é o seu departamento?'].value_counts()).reset_index().rename(columns = {'index':'Departamento', 0:'count'})
    sim_departamento = sim_departamento.sort_values('count', ascending = False).reset_index(drop = True)
    
    chart = generate_bar_chart_similarity_department(sim_departamento, 400, 600)
    components.html(
        chart.to_html(),
        height = height + h_buffer,
        width = width + w_buffer,
    )
    
if __name__ == "__main__":
    main()