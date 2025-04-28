from email.policy import default
from functools import reduce

import dcc
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from werkzeug.datastructures.structures import CallbackDict

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY, dbc.icons.FONT_AWESOME],
)

# clean up spreadsheets:
## food CPI:
df1 = pd.read_csv("../Data/Consumer_Index_Data/CPI_food_athome.csv")
df1['year'] = pd.to_datetime(df1['year'])
df1['year'] = df1['year'].dt.year
df1 = df1.groupby('year')['CPI_food'].mean().reset_index()
df1["CPI_food"] = df1["CPI_food"].round(2)
df1 = df1[(df1['year'] >= 1973) & (df1['year'] <= 2023)]

## fuel and utilities CPI
df2 = pd.read_csv("../Data/Consumer_Index_Data/CPI_fuel_Utilities.csv")
df2['year'] = pd.to_datetime(df2['year'])
df2['year'] = df2['year'].dt.year
df2 = df2.groupby('year')['CPI_Fuel_ut'].mean().reset_index()
df2["CPI_Fuel_ut"] = df2["CPI_Fuel_ut"].round(2)
df2 = df2[(df2['year'] >= 1973) & (df2['year'] <= 2023)]

## housing CPI
df3 = pd.read_csv("../Data/Consumer_Index_Data/CPI_housing.csv")
df3['year'] = pd.to_datetime(df3['year'])
df3['year'] = df3['year'].dt.year
df3 = df3.groupby('year')['CPI_housing'].mean().reset_index()
df3["CPI_housing"] = df3["CPI_housing"].round(2)
df3 = df3[(df3['year'] >= 1973) & (df3['year'] <= 2023)]

## Used Cars and Vehicles CPI
df4 = pd.read_csv("../Data/Consumer_Index_Data/CPI_Usedcars_vehicles.csv")
df4['year'] = pd.to_datetime(df4['year'])
df4['year'] = df4['year'].dt.year
df4 = df4.groupby('year')['CPI_cars'].mean().reset_index()
df4["CPI_cars"] = df4["CPI_cars"].round(2)
df4 = df4[(df4['year'] >= 1973) & (df4['year'] <= 2023)]

## mean family income
dff = pd.read_csv("../Data/Mean_Income_Data/Mean_income_family.csv")
dff['year'] = pd.to_datetime(dff['year'])
dff['year'] = dff['year'].dt.year
dff = dff[(dff['year'] >= 1973) & (dff['year'] <= 2023)]

## College Cost
dfff = pd.read_csv("../Data/Education_Data/College_Cost_Data.csv")

#  make one df
df6 = pd.merge(df1, df2, on='year')
df7 = pd.merge(df3,df4, on='year')
df = pd.merge(df6,df7, on='year')

on_campus = ["Tuition", "Books and Supplies", "Food and Housing (on Campus)", "Other (on Campus)"]
off_campus = ["Tuition", "Books and Supplies", "Food and Housing (off Campus)", "Other (off Campus)"]


"""
==========================================================================
Markdown Text
"""

datasource_text = dcc.Markdown(
    """
    [Data source 1:](https://fred.stlouisfed.org/)
    Federal Reserve Economic Data from the Federal Reserve Bank of St.Louis.
    
    [Data source 2:](https://nces.ed.gov/)
    National Center for Education Statistics 
    
    """
)

household_CPI_text = dcc.Markdown(
    """
> **The Consumer Price Index (CPI) ** is according to the US Bureau of Labor Statistic "a measure of the average change over time in the prices paid by urban consumers for a market basket of consumer goods and services". It is considered an indicator for inflation: A high CPI means that consumers are paying a higher price for the same quantity of goods.

> Select one of the household necessities below and see how its CPI has changed over time.
  Also, take a look at how the median household income has changed over time. Do you think the income has increased enough to keep up with the inflation?
"""
)

education_text = dcc.Markdown(
    """
> After seeing how the cost of different household necessities has changed over time, take a look at the average cost of college for a year!

> Choose which type of school you are interested in, and select if you would rather live on or off campus to get the average total cost!
"""

)

Introduction_text = dcc.Markdown(
    """
> Have you ever heard about the Consumer Price Index, but you do not really know what it is? Do you want to find out how the Consumer Price Index of different household necessities has changed over time?
> Are you curious about how the estimated cost of College changes between public and private schools? Go to the Explore tab to get the answer to these and other questions!
> If you want to take a look at the data tables, go to the Data tab. And if you would like to explore some more data, check out the source websites!
    """
)

footer = html.Div(
    dcc.Markdown(
        """
         This information is intended solely as general information for educational
        and entertainment purposes only - it is suppose to serve as an overview, and it is not exhaustive. 
        Further Research is recommended.
        """
    ),
    className="p-2 mt-5 bg-primary text-white small",
)

"""
==========================================================================
Tables
"""

housing_table = dash_table.DataTable(
    id="housing data",
    columns=([{"id": col, "name": col, "type": "numeric",}
            for col in df.columns]
    ),
    data=df.to_dict("records"),
    sort_action="native",
    page_size=15,
    style_table={"overflowX": "scroll"},
)

income_table = dash_table.DataTable(
    id="income data",
    columns=([{"id": col, "name": col, "type": "numeric",}
            for col in dff.columns]
    ),
    data=dff.to_dict("records"),
    sort_action="native",
    page_size=15,
    style_table={"overflowX": "scroll"},
)

college_table = dash_table.DataTable(
    id="college data",
    columns=([{"id": col, "name": col, "type": "numeric",}
            for col in dfff.columns]
    ),
    data=dfff.to_dict("records"),
    sort_action="native",
    page_size=15,
    style_table={"overflowX": "scroll"},
)

"""
==========================================================================
Figures
"""
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=dff['year'],
    y=dff['Mean_inc'],
    mode='lines+markers',
    name='Sales'
))
fig1.update_layout(
    title='Mean Household Income Over Years',
    xaxis_title='Year',
    yaxis_title='Income in $'
)

"""
==========================================================================
Make Tabs
"""

# ======= Explore tab components

household_card = dbc.Card(household_CPI_text, className="mt-2")

checklist_card = dbc.Card(
    [
        html.H4("Select household necessities to inspect:", className="card-title"),
        dcc.Checklist(
            id="household_checklist",
            options = [
                {'label': " Housing", "value" : "CPI_housing"},
                {"label": " Fuel and Utilities", "value": "CPI_Fuel_ut"},
                {"label": " Used Cars/Vehicles", "value" : "CPI_cars"},
                {"label": " Food (eating at home)", "value" : "CPI_food"}
                ],
            value=[],
        ),
    ],
    body=True,
    className="mt-4",
)

# ======= InputGroup components

type_school = dbc.InputGroup(
    [
        dcc.Dropdown(
            id = "dropdown_college",
            options =[
            {'label': 'Public, In-state', 'value': 'Public_instate'},
            {'label': 'Public, Out-state', 'value': 'Public_outstate'},
            {'label': 'Private Nonprofit', 'value': 'Private_Nonprofit'},
            {'label': 'Private For-Profit', 'value': 'Private_Forprofit'}
        ],
            placeholder= "Select the school type",
            value = "Public_instate",
        style = {"width" : "100%"},

        ),
    ],
    className="mb-3",
)
housing = dbc.InputGroup(
    [
        dcc.Dropdown(
            id = "dropdown_housing",
            options =[
            {'label': 'on Campus', 'value': 'on_Campus'},
            {'label': 'off Campus', 'value': 'off_Campus'},
        ],
            placeholder = "Select where you would live",
            value = "on_Campus",
        style = {"width" : "100%"},

        ),
    ],
    className="mb-3",
)

end_amount = dbc.InputGroup(
    [
        dbc.InputGroupText("Total Cost (in Dollars)"),
        dbc.Input(id="ending_amount", disabled=True, className="text-black"),
    ],
    className="mb-3",
)

input_groups = html.Div(
    [type_school, housing, end_amount],
    className="mt-4 p-4",
)


# =====  Results Tab components

data_source_card_housing = dbc.Card(
    [
        dbc.CardHeader("Source Data: CPI of household necessities"),
        html.Div(housing_table),
    ],
    className="mt-4",
)


data_source_card_income= dbc.Card(
    [
        dbc.CardHeader("Source Data: Mean income household"),
        html.Div(income_table),
    ],
    className="mt-4",
)

data_source_card_college= dbc.Card(
    [
        dbc.CardHeader("Source Data: College Cost"),
        html.Div(college_table),
    ],
    className="mt-4",
)


# ========= Learn Tab  Components
Introduction_card = dbc.Card(
    [
        dbc.CardHeader("An Introduction to Cost of Living and College Education in the US"),
        dbc.CardBody(Introduction_text),
    ],
    className="mt-4",
)


# ========= Build tabs
tabs = dbc.Tabs(
    [
        dbc.Tab(Introduction_card, tab_id="tab1", label="Overview"),
        dbc.Tab(
            [household_CPI_text, checklist_card, education_text, input_groups],
            tab_id="tab-2",
            label="Explore",
            className="pb-4",
        ),
        dbc.Tab([data_source_card_income, data_source_card_housing,data_source_card_college], tab_id="tab-3", label="Data"),
    ],
    id="tabs",
    active_tab="tab-2",
    className="mt-2",
)


"""
===========================================================================
Main Layout
"""

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H2(
                    "Cost of Living and College Education in the US",
                    className="text-center bg-primary text-white p-2",
                ),
            )
        ),
        dbc.Row(
            dbc.Col(
                html.H3(
                    "Lisa Kiefer - CS150",
                    style={"fontSize": "20px", "color": "grey"},
                    className="text-center"
                )
            )
        ),
        dbc.Row(
            [
                dbc.Col(tabs, width=12, lg=5, className="mt-4 border"),
                dbc.Col(
                    [
                        dcc.Graph(id="housing_line_chart", className="mb-2"),
                        dcc.Graph(figure = fig1),
                        dcc.Graph(id="college_cost_bar_chart", className="pb-4"),
                        html.Hr(),
                        html.Div(id="summary_table"),
                        html.H6(datasource_text, className="my-2"),
                    ],
                    width=12,
                    lg=7,
                    className="pt-4",
                ),
            ],
            className="ms-1",
        ),
        dbc.Row(dbc.Col(footer)),
    ],
    fluid=True,
)


"""
==========================================================================
Callbacks
"""

@app.callback(
    Output("housing_line_chart", "figure"),
    [Input("household_checklist","value")]
)
def update_line_chart(selected_values):
    if not selected_values:
        return{}
    fig = go.Figure()
    for value in selected_values:
        fig.add_trace(go.Scatter(
            x=df['year'],
            y=df[value],
            mode='lines',
            name=value
        ))
    fig.update_layout(
        title='Consumer Price Index of household expenses over time',
        xaxis_title='Year',
        yaxis_title='Consumer Price Index',
        yaxis = dict(range = [0,350]),
        legend_title='Household Expenses'
    )
    return fig

@app.callback(
    Output("college_cost_bar_chart","figure"),
    [Input("dropdown_college","value"),
    Input("dropdown_housing", "value")]
)
def update_graph(selected_type, housing_value):
    if housing_value == "on_Campus":
        filtered_data = dfff[dfff.Expenses.isin(on_campus)]
        fig = go.Figure(data=[
        go.Bar(
            x=filtered_data['Expenses'],
            y=filtered_data[selected_type],
        )
        ])
        fig.update_layout(
            title=f'Average Expenses for {selected_type} Colleges for a year (Data from 2023)',
            xaxis_title='Expense Category',
            yaxis_title='Cost (USD)',
            yaxis=dict(range=[0,35000])
        )
    else:
        filtered_data = dfff[dfff.Expenses.isin(off_campus)]
        fig = go.Figure(data=[
        go.Bar(
            x=filtered_data['Expenses'],
            y=filtered_data[selected_type],
        )
        ])
        fig.update_layout(
            title=f'Average Expenses for {selected_type} Colleges for a year',
            xaxis_title='Expense Category',
            yaxis_title='Cost (USD)',
            yaxis=dict(range=[0,35000])
        )
    return fig


@app.callback(
    Output("ending_amount", "value"),
    [Input("dropdown_college", "value"),
    Input("dropdown_housing", "value"),]

)
def update_total(selected_type, housing_value):
    if housing_value == "on_Campus":
        filtered_data = dfff[dfff.Expenses.isin(on_campus)]
        ending_amount = filtered_data[selected_type].sum()
    else:
        filtered_data = dfff[dfff.Expenses.isin(off_campus)]
        ending_amount = filtered_data[selected_type].sum()
    return ending_amount



if __name__ == "__main__":
    app.run(debug=True)
