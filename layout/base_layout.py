# layout/base_layout.py
from dash import html, dcc, dash_table
import numpy as np
from utils.formatting import format_mass_int

def create_layout(df):
    """Gibt das komplette HTML-Layout zurück (inkl. Sidebar, Nav-Buttons, Map, Table, Diagramme)."""
    return html.Div([
    dcc.Store(id='map-type', data='nav-clu'),  # Standardmäßig Cluster-Karte
    html.H1("Impact Atlas - Meteoriten weltweit", style={'textAlign': 'center', 'fontFamily': 'Arial'}),

    # Neue Navigationsleiste
    html.Div([
        html.Button(
            "Cluster Karte",
            id='nav-clu',
            className='nav-button',
            n_clicks=1,  # Set an initial click to make this the default
            style={
                'flex': '1',
                'padding': '10px 20px',
                'margin': '0 5px',
                'backgroundColor': '#4CAF50',
                'color': 'white',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'fontSize': '16px'
            }
        ),
        html.Button(
            "Punktekarte",
            id='nav-pun',
            className='nav-button',
            n_clicks=0,
            style={
                'flex': '1',
                'padding': '10px 20px',
                'margin': '0 5px',
                'backgroundColor': '#2196F3',
                'color': 'white',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'fontSize': '16px'
            }
        ),
        html.Button(
            "Heatmap",
            id='nav-hea',
            className='nav-button',
            n_clicks=0,
            style={
                'flex': '1',
                'padding': '10px 20px',
                'margin': '0 5px',
                'backgroundColor': '#ff9800',
                'color': 'white',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'fontSize': '16px'
            }
        ),
        html.Button(
            "Diagramm",
            id='nav-dia',
            className='nav-button',
            n_clicks=0,
            style={
                'flex': '1',
                'padding': '10px 20px',
                'margin': '0 5px',
                'backgroundColor': '#9c27b0',
                'color': 'white',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'fontSize': '16px'
            }
        )
    ], style={
        'display': 'flex',
        'justifyContent': 'center',
        'marginBottom': '20px',
        'gap': '10px',
        'padding': '0 20px'
    }),

    html.Div(id="main-container", children=[

        # Kartenbereich und Tabelle
        html.Div(id="map-and-table-container", children=[
            dcc.Graph(id='meteor-map', config={"scrollZoom": True},
                    style={'height': '50vh'}),

            dash_table.DataTable(
                id='meteor-table',
                columns=[
                    {"name": "Name", "id": "name"},
                    {"name": "Jahr", "id": "year"},
                    {"name": "Masse", "id": "formatted_mass"},
                    {"name": "Klasse", "id": "recclass"},
                    {"name": "Land", "id": "country"},
                ],
                page_size=10,
                style_table={
                    'height': '35vh',
                    'overflowY': 'auto',
                    'marginTop': '8px',
                    'tableLayout': 'fixed',
                },
                style_cell={
                    'fontFamily': 'Arial',
                    'fontSize': '12px',
                    'padding': '3px',
                    'textAlign': 'left',
                    'width': '20%',
                    'minWidth': '20%',
                    'maxWidth': '20%',
                    'whiteSpace': 'normal',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                },
            ),
        ], style={ # Standard-Style: sichtbar, wenn App geladen wird
            'flex': '75%', 'padding': '10px',
            'display': 'flex', 'flexDirection': 'column'
        }),

        # Bereich für die Diagramme (initially hidden)
        html.Div(id="diagram-container", children=[
            html.H3("Meteoritenfunde pro Land", style={'textAlign': 'center', 'marginTop': '10px'}),
            dcc.Graph(id='country-diagram-graph', config={"scrollZoom": True},
                      style={'height': '40vh', 'width': '100%', 'marginBottom': '20px'}), # Etwas kleiner

            html.H3("Meteoritenfunde pro Meteoritenklasse", style={'textAlign': 'center', 'marginTop': '10px'}),
            dcc.Graph(id='class-diagram-graph', config={"scrollZoom": True},
                      style={'height': '40vh', 'width': '100%'})
        ], style={ # Standard-Style: versteckt
            'flex': '75%', 'padding': '10px',
            'display': 'none', 'flexDirection': 'column'
        }),


        # Steuerungsbereich
        html.Div([
            # Masse-Filter
            html.H4("Masse in Gramm:", style={'marginBottom': '10px', 'borderBottom': '1px solid #ccc'}),
            html.Div(id='mass-slider-display',
                    style={'textAlign':'center', 'fontSize':'12px', 'marginTop':'-6px'}),
            dcc.RangeSlider(
                id='mass-slider',
                min=df['log_mass'].min(),
                max=df['log_mass'].max(),
                value=[df['log_mass'].min(), df['log_mass'].max()],
                marks={
                    float(f"{tick:.2f}"): format_mass_int(10**tick - 1)
                    for tick in np.linspace(df['log_mass'].min(),
                                            df['log_mass'].max(),
                                            8)
                },
                step=0.05,
                updatemode='drag',
            ),
            html.Br(),
            html.Div([
                html.Label("min:", style={'margin': '10px'}),
                dcc.Input(
                    id='min-mass-input',
                    type='number',
                    value=df['mass'].min(),
                    style={'width': '45%', 'marginRight': '5%'}
                ),
                html.Label("max:", style={'margin': '10px'}),
                dcc.Input(
                    id='max-mass-input',
                    type='number',
                    value=df['mass'].max(),
                    style={'width': '45%'}
                )
            ], style={'display': 'flex', 'justifyContent': 'space-between'}),

            # Meteoritentyp-Filter
            html.H4("Meteoritentyp:", style={'marginBottom': '10px', 'borderBottom': '1px solid #ccc'}),
            dcc.Dropdown(
                options=[{"label": i, "value": i} for i in sorted(df["recclass"].unique())],
                value=None,
                multi=True,
                id="class-filter",
                placeholder="Typ auswählen (mehrere möglich)"
            ),

            # Jahr-Filter
            html.H4("Jahr:", style={'marginBottom': '10px', 'borderBottom': '1px solid #ccc'}),
            html.Div(id='year-slider-display',
                style={'textAlign':'center', 'fontSize':'12px','marginTop':'-6px'}),
            dcc.RangeSlider(
                id='year-slider',
                min=df['year'].min(),
                max=df['year'].max(),
                value=[df['year'].min(), df['year'].max()],
                marks={int(i): f'{int(i)}' for i in np.linspace(df['year'].min(), df['year'].max(), 5)},
                updatemode='drag'
            ),
            html.Br(),
            html.Div([
                html.Label("von:", style={'margin': '10px'}),
                dcc.Input(
                    id='min-year-input',
                    type='number',
                    value=df['year'].min(),
                    style={'width': '45%', 'marginRight': '5%'}
                ),
                html.Label("bis:", style={'margin': '10px'}),
                dcc.Input(
                    id='max-year-input',
                    type='number',
                    value=df['year'].max(),
                    style={'width': '45%'}
                )
            ], style={'display': 'flex', 'gap': '10px'}),

            # Fall/Found-Filter
            html.H4("Status (Fall/Found):", style={'marginBottom': '10px', 'borderBottom': '1px solid #ccc'}),
            dcc.Checklist(
                options=[
                    {"label": "Beobachtet", "value": "Fell"},
                    {"label": "Gefunden", "value": "Found"}
                ],
                value=df["fall"].unique().tolist(),
                id="fall-filter",
                labelStyle={'display': 'inline-block', 'margin': '3px 0'}
            ),

            # Ortssuche
            html.H4("Ortssuche:", style={'marginBottom': '10px', 'borderBottom': '1px solid #ccc'}),
            html.Label("Ort:", style={'margin': '10px'}),
            dcc.Input(
                id='location-input',
                type='text',
                placeholder='z. B. Berlin, Paris, New York',
                style={'width': '100%', 'padding': '8px', 'borderRadius': '4px', 'border': '1px solid #ccc'}
            ),
            html.Br(),
            html.Label("Suchradius (km):", style={'margin': '10px'}),
            dcc.Dropdown(
                id='radius-dropdown',
                options=[
                    {'label': '50 km', 'value': 50},
                    {'label': '100 km', 'value': 100},
                    {'label': '200 km', 'value': 200},
                    {'label': '500 km', 'value': 500},
                    {'label': '1000 km', 'value': 1000},
                    {'label': 'Unbegrenzt', 'value': 'unlimited'}
                ],
                value='unlimited',
                style={'width': '100%', 'marginBottom': '15px'}
            ),
            html.Div([
                html.Button(
                    'Ortssuche starten',
                    id='search-button',
                    style={
                        'width': '48%',
                        'padding': '10px',
                        'backgroundColor': '#4CAF50',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '4px',
                        'cursor': 'pointer',
                        'fontWeight': 'bold',
                        'marginTop': '10px'
                    }
                ),
                html.Button(
                    'Zurücksetzen',
                    id='reset-button',
                    style={
                        'width': '48%',
                        'padding': '10px',
                        'backgroundColor': '#f44336',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '4px',
                        'cursor': 'pointer',
                        'fontWeight': 'bold',
                        'marginTop': '10px',
                        'marginLeft': '4%'
                    }
                )
            ], style={'display': 'flex', 'justifyContent': 'space-between'}),

            # Statistik
            html.H4("Statistik:", style={'marginBottom': '10px', 'borderBottom': '1px solid #ccc'}),
            html.Div(id='stats-container')
        ], style={
            'flex': '25%',
            'padding': '20px',
            'backgroundColor': '#f9f9f9',
            'borderLeft': '1px solid #ccc',
            'borderRadius': '0 5px 5px 0',
            'overflowY': 'auto',
            'maxHeight': '85vh'
        })
    ], style={
        'display': 'flex',
        'flexDirection': 'row',
        'justifyContent': 'space-between',
        'border': '1px solid #ddd',
        'borderRadius': '5px',
        'boxShadow': '0 0 10px rgba(0,0,0,0.1)',
        'height': '85vh'
    })
], id="app-container", style={
    'maxWidth': '1600px',
    'margin': '0 auto',
    'padding': '20px',
    'boxSizing': 'border-box',
    'fontFamily': 'Arial, sans-serif'
})