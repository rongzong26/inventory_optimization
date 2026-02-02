"""Dashboard layout components"""
from dash import html, dcc
import dash_ag_grid as dag
import dash_leaflet as dl
from datetime import datetime

DB_COLORS = {'primary': '#FF3621', 'dark': '#0B2026', 'light_gray': '#EEEDE9', 'off_white': '#F9F7F4'}
CONTAINER_STYLE = {'margin': '20px 40px', 'padding': '20px', 'backgroundColor': DB_COLORS['off_white'], 
                   'borderRadius': '8px', 'border': f'2px solid {DB_COLORS["light_gray"]}'}
FONT_STYLE = {'fontFamily': 'DM Sans, sans-serif'}

def create_modal(modal_id, title, content, button_ids, button_labels, display='none'):
    buttons = [html.Button(label, id=btn_id, n_clicks=0, style={
        'padding': '12px 35px', 'backgroundColor': DB_COLORS['primary'] if i == 0 else 'white',
        'color': 'white' if i == 0 else DB_COLORS['dark'],
        'border': f'2px solid {DB_COLORS["primary"]}' if i == 0 else f'2px solid {DB_COLORS["dark"]}',
        'borderRadius': '8px', 'fontSize': '16px', 'fontWeight': '600',
        'cursor': 'pointer', 'marginLeft': '10px', 'transition': 'all 0.3s', **FONT_STYLE
    }) for i, (btn_id, label) in enumerate(zip(button_ids, button_labels))]
    
    return html.Div([html.Div([html.Div([
        html.H2(title, style={'margin': '0 0 25px 0', 'color': DB_COLORS['dark'], 'fontWeight': '700', 
                             'fontSize': '28px', 'textAlign': 'center', 'borderBottom': f'3px solid {DB_COLORS["primary"]}',
                             'paddingBottom': '15px', **FONT_STYLE}),
        html.Div(content, style={'marginBottom': '35px', 'lineHeight': '1.8', 'color': DB_COLORS['dark'], 
                               'fontSize': '15px', **FONT_STYLE}),
        html.Div(buttons, style={'textAlign': 'center', 'marginTop': '30px'})
    ], style={'backgroundColor': 'white', 'padding': '50px', 'borderRadius': '12px', 'maxWidth': '700px', 
             'width': '90%', 'position': 'relative', 'boxShadow': '0 10px 40px rgba(0, 0, 0, 0.2)'})
    ], style={'position': 'fixed', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 
             'top': '0', 'left': '0', 'width': '100%', 'height': '100%', 'backgroundColor': 'rgba(0, 0, 0, 0.6)', 
             'zIndex': '1001' if 'welcome' in modal_id else '1000'})
    ], id=modal_id, style={'display': display})

def create_header():
    # Get current date dynamically
    current_date = datetime.now().strftime("%B %d, %Y")
    
    return html.Div([
        # Agnico Eagle branding on the left with official logo
        html.Div([
            html.Div([
                # Official Agnico Eagle logo
                html.Img(
                    src='https://s21.q4cdn.com/374334112/files/images/AgnicoClientLogo.png',
                    style={
                        'height': '50px', 'marginRight': '0px', 'verticalAlign': 'middle',
                        'filter': 'brightness(0) invert(1)'  # Make logo white for dark background
                    }
                )
            ], style={'marginBottom': '4px'}),
            html.Div(current_date, style={
                'color': DB_COLORS['off_white'], 'fontSize': '14px', 
                'fontWeight': '500', **FONT_STYLE
            })
        ], style={
            'position': 'absolute', 'left': '30px', 'top': '50%', 'transform': 'translateY(-50%)', 'zIndex': '10'
        }),
        html.H1("Inventory Optimization Control Center", style={
            'textAlign': 'center', 'padding': '30px 20px', 'margin': '0', 'backgroundColor': DB_COLORS['dark'],
            'color': DB_COLORS['off_white'], 'fontWeight': '700', 'fontSize': '32px', **FONT_STYLE}),
        html.Div([
            html.Button([
                html.Span("💬 ", style={'marginRight': '8px'}),
                "Inventory Assistant"
            ], id='toggle-chat-panel', n_clicks=0, style={
                'padding': '10px 20px', 'backgroundColor': DB_COLORS['primary'], 
                'color': 'white', 'border': 'none', 'borderRadius': '5px', 
                'cursor': 'pointer', 'fontWeight': '600', 'fontSize': '14px', 
                'marginRight': '10px', 'transition': 'all 0.3s', **FONT_STYLE
            }),
            html.Button("Instructions", id='instructions-button', style={
                'padding': '10px 20px', 'backgroundColor': DB_COLORS['off_white'], 'color': DB_COLORS['dark'], 
                'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer', 'fontWeight': '600', 
                'fontSize': '14px', **FONT_STYLE
            })
        ], style={'position': 'absolute', 'right': '30px', 'top': '50%', 'transform': 'translateY(-50%)', 'zIndex': '10'})
    ], style={'position': 'relative', 'backgroundColor': DB_COLORS['dark'], 'minHeight': '90px'})

def create_filter_dropdown(label, filter_id, options, placeholder):
    return html.Div([
        html.Label(label, style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block', 
                                'color': DB_COLORS['dark'], **FONT_STYLE}),
        dcc.Dropdown(id=filter_id, options=[{'label': o, 'value': o} for o in options], value=None, 
                    multi=False, placeholder=placeholder, style=FONT_STYLE)
    ], style={'width': '23%', 'display': 'inline-block', 'marginRight': '2%', 'verticalAlign': 'top'})

def create_filters(sites, equipment, parts, risk_levels):
    return html.Div([
        create_filter_dropdown("Site:", 'site-filter', sites, "All Sites"),
        create_filter_dropdown("Equipment:", 'equipment-filter', equipment, 
                             "All Equipment" if equipment else "No Equipment Data"),
        create_filter_dropdown("Part:", 'part-filter', parts, "All Parts"),
        create_filter_dropdown("Risk Level:", 'risk-filter', risk_levels, "All Risk Levels")
    ], style=CONTAINER_STYLE)

def create_map_and_kpi_row(initial_center):
    return html.Div([
        html.Div([
            dl.Map(id='understock-map', center=initial_center, zoom=7.5, children=[
                dl.TileLayer(url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                           attribution='Tiles &copy; Esri'),
                dl.TileLayer(url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
                           attribution='Labels &copy; Esri'),
                dl.LayerGroup(id='map-markers')
            ], style={'height': '350px', 'border': f'2px solid {DB_COLORS["light_gray"]}', 'borderRadius': '8px'})
        ], style={'flex': '1', 'backgroundColor': DB_COLORS['off_white'], 'padding': '20px', 'borderRadius': '8px', 
                 'border': f'2px solid {DB_COLORS["light_gray"]}', 'marginRight': '20px'}),
        html.Div([
            html.H3("Parts Inventory – Operational Impact", style={'marginTop': '0', 'marginBottom': '15px', 
                   'color': DB_COLORS['dark'], 'fontWeight': '600', 'fontSize': '16px', **FONT_STYLE}),
            html.P("This shows whether sites have enough parts to complete planned work without creating inventory risk",
                  style={'marginBottom': '15px', 'color': DB_COLORS['dark'], 'fontSize': '13px', 
                        'lineHeight': '1.5', **FONT_STYLE}),
            html.Div(id='kpi-table', style={'overflowY': 'auto', 'maxHeight': '250px'})
        ], style={'flex': '1', 'backgroundColor': DB_COLORS['off_white'], 'padding': '20px', 'borderRadius': '8px',
                 'border': f'2px solid {DB_COLORS["light_gray"]}', 'height': '350px', 'overflow': 'auto'})
    ], style={'display': 'flex', 'margin': '0 40px 20px 40px'})

def create_data_table():
    return html.Div([
        html.H3("Detailed Inventory Data", style={'marginTop': '0', 'marginBottom': '20px', 
               'color': DB_COLORS['dark'], 'fontWeight': '500', **FONT_STYLE}),
        dag.AgGrid(id='data-grid', rowData=[], columnDefs=[],
            defaultColDef={"resizable": True, "sortable": True, "filter": True, "tooltipComponent": "agTooltipComponent"},
            dashGridOptions={"pagination": True, "paginationPageSize": 20, "tooltipShowDelay": 500,
                "getRowStyle": {"styleConditions": [
                    {"condition": "params.data.risk_level == 'Stocked'", "style": {"backgroundColor": "#d4edda"}},
                    {"condition": "params.data.risk_level == 'Low Stock'", "style": {"backgroundColor": "#fff3cd"}},
                    {"condition": "params.data.risk_level == 'Out of Stock'", "style": {"backgroundColor": "#f8d7da"}}
                ]}, "maintainColumnOrder": True},
            style={'height': '400px', **FONT_STYLE})
    ], style=CONTAINER_STYLE)

def create_ai_button():
    return html.Div([
        html.Button("AI Suggested Part Allocation", id='ai-allocation-button', n_clicks=0, disabled=True,
            style={'padding': '15px 40px', 'backgroundColor': '#cccccc', 'color': '#666666', 'border': 'none', 
                  'borderRadius': '8px', 'fontSize': '16px', 'fontWeight': '500', 'cursor': 'not-allowed',
                  'display': 'block', 'margin': '0 auto', **FONT_STYLE}),
        html.P("Select a site and a part in the filters above to enable AI suggestions", 
              style={'marginTop': '10px', 'marginBottom': '0', 'fontSize': '12px', 'color': DB_COLORS['dark'], 
                    'fontStyle': 'italic', 'textAlign': 'center', **FONT_STYLE})
    ], style=CONTAINER_STYLE)

def create_embedded_chat():
    """Create fully embedded chat panel with custom AI interface"""
    return html.Div([
        html.Div([
            # Chat header
            html.Div([
                html.H3("✨ Genie AI Assistant", style={
                    'margin': '0',
                    'color': 'white',
                    'fontSize': '18px',
                    'fontWeight': '600',
                    **FONT_STYLE
                }),
                html.Button("✕", id='close-chat-panel', n_clicks=0, style={
                    'backgroundColor': 'transparent',
                    'color': 'white',
                    'border': 'none',
                    'fontSize': '24px',
                    'cursor': 'pointer',
                    'padding': '0',
                    'lineHeight': '1',
                    'fontWeight': 'bold'
                })
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'padding': '15px 20px',
                'backgroundColor': DB_COLORS['dark'],
                'borderBottom': '1px solid #ddd'
            }),
            
            # Chat messages area
            html.Div(
                id='chat-messages',
                children=[
                    html.Div([
                        html.Div("AI", style={
                            'display': 'inline-block',
                            'padding': '4px 12px',
                            'backgroundColor': DB_COLORS['primary'],
                            'color': 'white',
                            'borderRadius': '12px',
                            'fontSize': '11px',
                            'fontWeight': '600',
                            'marginBottom': '8px',
                            **FONT_STYLE
                        }),
                        dcc.Markdown(
                            "👋 Hello! I can help you with inventory questions. Loading current status...",
                            style={
                                'backgroundColor': '#f0f0f0',
                                'padding': '12px 16px',
                                'borderRadius': '12px',
                                'marginBottom': '16px',
                                'color': DB_COLORS['dark'],
                                'fontSize': '14px',
                                'lineHeight': '1.5',
                                **FONT_STYLE
                            }
                        )
                    ], style={'marginBottom': '12px'})
                ],
                style={
                    'flexGrow': '1',
                    'overflowY': 'auto',
                    'padding': '20px',
                    'backgroundColor': 'white',
                    'maxHeight': 'calc(100vh - 200px)',
                    'minHeight': '400px'
                }
            ),
            
            # Chat input area
            html.Div([
                dcc.Textarea(
                    id='chat-input',
                    placeholder='Ask me anything about your supply chain data (powered by Genie)... (Press Enter to send)',
                    style={
                        'width': '100%',
                        'minHeight': '60px',
                        'maxHeight': '120px',
                        'padding': '12px',
                        'border': '1px solid #ddd',
                        'borderRadius': '8px',
                        'resize': 'vertical',
                        'fontSize': '14px',
                        'fontFamily': 'DM Sans, sans-serif',
                        'marginBottom': '10px'
                    }
                ),
                html.Div([
                    html.Button([
                        html.Span("🚀 ", style={'marginRight': '6px'}),
                        "Send"
                    ], id='send-chat-message', n_clicks=0, style={
                        'padding': '10px 24px',
                        'backgroundColor': DB_COLORS['primary'],
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '8px',
                        'cursor': 'pointer',
                        'fontWeight': '600',
                        'fontSize': '14px',
                        'marginRight': '10px',
                        **FONT_STYLE
                    }),
                    html.Button("Clear", id='clear-chat', n_clicks=0, style={
                        'padding': '10px 24px',
                        'backgroundColor': '#f5f5f5',
                        'color': DB_COLORS['dark'],
                        'border': '1px solid #ddd',
                        'borderRadius': '8px',
                        'cursor': 'pointer',
                        'fontWeight': '600',
                        'fontSize': '14px',
                        **FONT_STYLE
                    })
                ], style={'display': 'flex', 'justifyContent': 'flex-end'})
            ], style={
                'padding': '15px 20px',
                'backgroundColor': '#f9f9f9',
                'borderTop': '1px solid #ddd'
            }),
            
            # Hidden store for conversation history
                    dcc.Store(id='conversation-history', data=[]),
                    dcc.Store(id='pending-question', data=None),
                    dcc.Interval(id='response-checker', interval=1000, disabled=True, n_intervals=0)
            
        ], style={
            'display': 'flex',
            'flexDirection': 'column',
            'height': '100vh',
            'backgroundColor': 'white'
        })
    ], 
    id='chat-panel',
    style={
        'position': 'fixed',
        'right': '-500px',
        'top': '0',
        'width': '500px',
        'height': '100vh',
        'backgroundColor': 'white',
        'boxShadow': '-5px 0 20px rgba(0,0,0,0.3)',
        'zIndex': '998',
        'transition': 'right 0.3s ease-in-out'
    })

def create_layout(sites, equipment, parts, risk_levels, initial_center):
    return html.Div([
        html.Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap'),
        create_header(), create_filters(sites, equipment, parts, risk_levels),
        create_map_and_kpi_row(initial_center), create_data_table(), create_ai_button(),
        create_embedded_chat()
    ], style={'backgroundColor': DB_COLORS['light_gray'], 'minHeight': '100vh', **FONT_STYLE})

