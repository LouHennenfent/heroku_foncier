
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import geopandas as gpd

###########################################################################
# Importation des données 

token = 'pk.eyJ1IjoibGV2eWMxNiIsImEiOiJjbDFrdjNlbTYwNHBuM2pvNndxZjg5dWZ6In0.jzvqLsgklwMYNRkQVaogZQ'

objets_filepath = 'tableurok_2.csv'

df = pd.read_csv(objets_filepath)

#objets_import=xls.parse('Sheet1') #voir à quoi ça sert

print(df)

dep_ls = df['dep_name'].unique() # dep_ls = liste des departements
dep_ls_format = [
    {'label' : k, 'value' : k} for k in sorted(dep_ls)
    ] # [{'label': 'fin', 'value': 'fin'}, {'label': 'mor', 'value': 'mor'}]

dep_format = [{'label' : '(Select All)', 'value' : 'All'}] # pour faire marcher le dropdown 
dep_all = dep_format + dep_ls_format

app = dash.Dash(__name__, suppress_callback_exceptions=True) # Ici le Dashboard est demarre
server = app.server

app.layout = dbc.Container([

    dbc.Row([
        html.H2("Dashboard sur des indicateurs d'habitations"),
            
    ],justify="center"),

    dbc.Row([
        html.Div(
            [
                dbc.Label("Département.s : "),
                dcc.Dropdown(id="SelecDep",
                    options=[
                        {'label': "Côtes-d'Armor", 'value': "Côtes-d'Armor"},
                        {'label': 'Ille-et-Vilaine', 'value': 'Ille-et-Vilaine'},
                        {'label': 'Morbihan', 'value': 'Morbihan'},
                        {'label': 'Finistère', 'value': 'Finistère'},
                    ],
                    value ='Ille-et-Vilaine',
                    placeholder="Selectionne un département",
                    )
                        ],style={'padding-bottom':'20px'}
                    ),
        html.Div([
                dbc.Label("Indicateur à afficher"),
                dcc.Dropdown(id="SelecIndic",
                    options=[
                        {'label': "Proportion d'appartements", 'value': 'prop_appart'},
                        {'label': 'Prix au m²', 'value': 'Prixm2'},
                    ],
                    placeholder="Selectionne un indicateur",
                    value ='Prixm2',
                    )
                        ],style={'padding-bottom':'20px'}
                    ),
    ]),

    dbc.Row([
    
        html.Div([
                  dcc.Graph(id="choropleth",style = {'width':'100%'}),
                            ]
                    ),

    ])
])


@app.callback(
    Output("choropleth", "figure"), 
    [Input("SelecDep","value"),
    Input("SelecIndic","value"),
    ])

def display_choropleth(Dep,SelecIndic):

    #Dep = Dep.sort

    Dep1 = df[(df["dep_name"]==Dep)]

    Dep1['geometry'] = gpd.GeoSeries.from_wkt(Dep1['geometry'])
    GeoDF = gpd.GeoDataFrame(Dep1, geometry='geometry')

    print(type(GeoDF))

    Max_value = GeoDF[SelecIndic].max()

    if SelecIndic == 'prop_appart' :
        Color = 'BrBg_r'
    else : 
        Color = 'RdYlGn_r'

    print(Color)

    fig = px.choropleth_mapbox(GeoDF,
                           geojson=GeoDF.geometry,
                           locations=GeoDF.index,
                           hover_name="com_name",
                           hover_data={"nb_appart":True,"nb_maisons":True,"prop_appart":True,"Prixm2":True},
                           color=SelecIndic,
                           color_continuous_scale=Color,
                           range_color = [0,Max_value],
                           center={"lat": 48.16,"lon":-3.49},
                           mapbox_style="carto-positron",
                           zoom=7,
                           opacity=0.8,
                           height=500
                           )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                        mapbox_accesstoken=token,
                        hoverlabel=dict( 
                            bgcolor="white",
                            font_size=16,
                            font_family="Inter"))

    return fig

if __name__ == '__main__':
    app.run_server(debug=False)