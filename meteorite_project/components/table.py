from dash import dash_table

def MeteorTable(df):
    return dash_table.DataTable(
        id="meteor-table",
        columns=[
            {"name": "Name", "id": "name"},
            {"name": "Jahr", "id": "year"},
            {"name": "Masse", "id": "formatted_mass"},
            {"name": "Klasse", "id": "recclass"},
            {"name": "Land", "id": "country"},
        ],
        data=df.to_dict("records"),
        page_size=10,
        row_selectable="single",
        style_table={"height": "35vh", "overflowY": "auto", "marginTop": "8px"},
        style_cell={"fontFamily": "Arial", "fontSize": "12px", "padding": "3px"},
    )
