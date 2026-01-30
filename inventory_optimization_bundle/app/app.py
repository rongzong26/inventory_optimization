"""Mining Parts Inventory Dashboard"""
import os
from dash import Dash, html, dcc, Input, Output, callback_context, State
import pandas as pd
import dash_leaflet as dl
from utils import get_connection, read_table, call_databricks_llm
from layout import create_layout, DB_COLORS, create_modal
from prompts import INVENTORY_RECOMMENDATION_PROMPT
from chat_assistant import get_chat_response, get_quick_insights

# Configuration - use environment variables for sensitive data
HTTP_PATH = os.getenv("DATABRICKS_WAREHOUSE_HTTP_PATH", "/sql/1.0/warehouses/TBD_UPDATE_AFTER_AUTH")
TABLE_NAME = os.getenv("DATABRICKS_TABLE_NAME", "rz_demo.supply_chain.gold_master_part_inventory")

# Constants
RISK_PRIORITY = {'Out of Stock': 1, 'Low Stock': 2, 'Stocked': 3}
RISK_COLORS = {'Out of Stock': 'red', 'Low Stock': 'gold', 'Stocked': 'green'}

def load_inventory_data():
    """Load inventory data from Databricks table"""
    try:
        print(f"Attempting to load data from: {TABLE_NAME}")
        print(f"Using warehouse: {HTTP_PATH}")
        df = read_table(TABLE_NAME, get_connection(HTTP_PATH))
        print(f"Successfully loaded {len(df)} rows")
        print(f"Columns: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"!!! ERROR loading data: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

# Load data and extract unique values for filters
inventory_data = load_inventory_data()
sites = sorted(inventory_data['plant_name'].unique()) if not inventory_data.empty else []
parts = sorted(inventory_data['part_name'].unique()) if not inventory_data.empty else []
equipment = sorted([e for e in inventory_data.get('equip_name', pd.Series()).unique() if e]) if not inventory_data.empty else []
risk_levels = ['Stocked', 'Low Stock', 'Out of Stock']
map_center = [inventory_data['lat'].mean(), inventory_data['lon'].mean()] if not inventory_data.empty else [-26.65, 152.95]

# Initialize Dash app
app = Dash(__name__)
app.index_string = '''<!DOCTYPE html><html><head>{%metas%}<title>{%title%}</title>{%favicon%}{%css%}<style>
@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
.markdown-content table{border-collapse:collapse;width:100%;margin:15px 0;font-family:'DM Sans',sans-serif;font-size:14px}
.markdown-content table th{background-color:#0B2026;color:white;padding:10px;text-align:left;font-weight:600;border:1px solid #ddd}
.markdown-content table td{padding:10px;border:1px solid #ddd;text-align:left}
.markdown-content table tr:nth-child(even){background-color:#F9F7F4}
.markdown-content table tr:hover{background-color:#EEEDE9}
</style></head><body>{%app_entry%}<footer>{%config%}{%scripts%}{%renderer%}</footer></body></html>'''

app.layout = create_layout(sites, equipment, parts, risk_levels, map_center)

ai_modal = html.Div([html.Div([html.Div([
    html.H2('AI Suggested Part Allocation', style={'margin': '0 0 20px 0', 'color': DB_COLORS['dark'],
        'fontFamily': 'DM Sans, sans-serif', 'fontWeight': '700', 'fontSize': '24px', 'textAlign': 'center'}),
    html.Div(id='ai-loading', children=[html.Div([
        html.Div(className='spinner', style={'border': '4px solid #f3f3f3', 'borderTop': f'4px solid {DB_COLORS["primary"]}',
            'borderRadius': '50%', 'width': '40px', 'height': '40px', 'animation': 'spin 1s linear infinite', 'margin': '0 auto 15px auto'}),
        html.Div('Generating AI recommendations...', style={'textAlign': 'center', 'color': DB_COLORS['dark'], 
            'fontFamily': 'DM Sans, sans-serif', 'fontSize': '14px'})
    ], style={'textAlign': 'center', 'padding': '40px 20px'})], style={'display': 'none'}),
    html.Div(id='ai-response-content', children=[
        html.P('Click the AI Suggested Part Allocation button to generate recommendations.', 
            style={'marginBottom': '30px', 'color': DB_COLORS['dark'], 'fontFamily': 'DM Sans, sans-serif', 
                  'lineHeight': '1.8', 'textAlign': 'center', 'fontStyle': 'italic'})
    ], style={'display': 'block'}),
    html.Div([
        html.Button('Initiate', id='modal-accept-button', n_clicks=0, style={'padding': '10px 30px', 
            'backgroundColor': DB_COLORS['primary'], 'color': 'white', 'border': 'none', 'borderRadius': '6px',
            'fontSize': '16px', 'fontWeight': '500', 'fontFamily': 'DM Sans, sans-serif', 'cursor': 'pointer', 'marginRight': '10px'}),
        html.Button('Cancel', id='modal-cancel-button', n_clicks=0, style={'padding': '10px 30px', 
            'backgroundColor': DB_COLORS['light_gray'], 'color': DB_COLORS['dark'], 'border': f'1px solid {DB_COLORS["dark"]}',
            'borderRadius': '6px', 'fontSize': '16px', 'fontWeight': '500', 'fontFamily': 'DM Sans, sans-serif', 'cursor': 'pointer'})
    ], style={'textAlign': 'right'})
], style={'backgroundColor': 'white', 'padding': '40px', 'borderRadius': '10px', 'maxWidth': '700px', 
    'width': '90%', 'position': 'relative', 'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)'})
], style={'position': 'fixed', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 
    'top': '0', 'left': '0', 'width': '100%', 'height': '100%', 'backgroundColor': 'rgba(0, 0, 0, 0.5)', 'zIndex': '1000'})
], id='ai-modal', style={'display': 'none'})

welcome_modal = create_modal('welcome-modal', 'Inventory Optimization Control Center', [
    "This dashboard helps Turnaround Leads manage spare parts inventory across multiple mine sites.",
    html.Br(), html.Br(),
    html.B("Key Capabilities:"),
    html.Ul([
        html.Li("Review current inventory levels and risk status across all sites"),
        html.Li("Identify low stock and out-of-stock situations"),
        html.Li("Use AI to generate recommendations for part reallocation between sites"),
        html.Li("Get vendor ordering suggestions to address shortages")
    ], style={'textAlign': 'left', 'marginLeft': '20px'}),
    html.Br(),
    "Select a site and part, then click 'Get AI Suggestion' to receive actionable recommendations."
], ['welcome-modal-close-button'], ['Get Started'], 'block')

app.layout.children.extend([ai_modal, welcome_modal])

@app.callback([Output('ai-allocation-button', 'disabled'), Output('ai-allocation-button', 'style')],
              [Input('site-filter', 'value'), Input('part-filter', 'value')])
def toggle_ai_button(site, part):
    """Enable AI button only when both site and part are selected"""
    enabled = bool(site and part)
    return not enabled, {'padding': '12px 40px', 'backgroundColor': DB_COLORS['primary'] if enabled else '#cccccc',
        'color': 'white' if enabled else '#666666', 'border': 'none', 'borderRadius': '8px', 'fontSize': '16px',
        'fontWeight': '500', 'fontFamily': 'DM Sans, sans-serif', 'cursor': 'pointer' if enabled else 'not-allowed', 
        'display': 'block', 'margin': '0 auto'}

@app.callback(Output('welcome-modal', 'style'),
              [Input('welcome-modal-close-button', 'n_clicks'), Input('instructions-button', 'n_clicks')],
              prevent_initial_call=True)
def toggle_welcome(close, instructions):
    """Show welcome modal on instructions button click, hide on close"""
    ctx = callback_context
    return {'display': 'block' if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[0] == 'instructions-button' else 'none'}

@app.callback([Output('ai-modal', 'style'), Output('ai-loading', 'style', allow_duplicate=True), 
               Output('ai-response-content', 'style', allow_duplicate=True)],
              [Input('ai-allocation-button', 'n_clicks'), Input('modal-accept-button', 'n_clicks'),
               Input('modal-cancel-button', 'n_clicks')], prevent_initial_call=True)
def toggle_ai_modal(ai, accept, cancel):
    """Toggle AI modal visibility and loading state"""
    ctx = callback_context
    if not ctx.triggered:
        return {'display': 'none'}, {'display': 'none'}, {'display': 'block'}
    return ({'display': 'block'}, {'display': 'block'}, {'display': 'none'}) if ctx.triggered[0]['prop_id'].split('.')[0] == 'ai-allocation-button' else ({'display': 'none'}, {'display': 'none'}, {'display': 'block'})

@app.callback([Output('map-markers', 'children'), Output('kpi-table', 'children'),
               Output('data-grid', 'rowData'), Output('data-grid', 'columnDefs')],
              [Input('site-filter', 'value'), Input('equipment-filter', 'value'),
               Input('part-filter', 'value'), Input('risk-filter', 'value')])
def update_dashboard(site, equip, part, risk):
    """Update map markers, KPI table, and AG Grid based on filter selections"""
    # Apply filters to data
    df = inventory_data.copy()
    if site: df = df[df['plant_name'] == site]
    if equip and 'equip_name' in df.columns: df = df[df['equip_name'] == equip]
    if part: df = df[df['part_name'] == part]
    if risk: df = df[df['risk_level'] == risk]
    
    # Build KPI table
    if df.empty:
        kpi = html.Div("No data", style={'textAlign': 'center', 'padding': '20px', 'color': DB_COLORS['dark']})
    else:
        kpis = df.groupby('plant_name').apply(lambda x: pd.Series({
            'Sufficient Inventory': f"{(len(x[x['risk_level'] == 'Stocked']) / len(x) * 100):.1f}%",
            'Low Inventory Risk': f"{(len(x[x['risk_level'] == 'Low Stock']) / len(x) * 100):.1f}%",
            'Stockout Risk': f"{(len(x[x['risk_level'] == 'Out of Stock']) / len(x) * 100):.1f}%"
        }), include_groups=False).reset_index()
        
        rows = [html.Tr([
            html.Td(r['plant_name'], style={'padding': '10px', 'borderBottom': f'1px solid {DB_COLORS["light_gray"]}', 
                'fontSize': '13px', 'color': 'red' if float(r['Stockout Risk'].rstrip('%')) > 0 else DB_COLORS['dark'], 
                'fontWeight': '600' if float(r['Stockout Risk'].rstrip('%')) > 0 else 'normal'}),
            html.Td(r['Sufficient Inventory'], style={'padding': '10px', 'textAlign': 'center', 
                'borderBottom': f'1px solid {DB_COLORS["light_gray"]}', 'fontSize': '13px'}),
            html.Td(r['Low Inventory Risk'], style={'padding': '10px', 'textAlign': 'center', 
                'borderBottom': f'1px solid {DB_COLORS["light_gray"]}', 'fontSize': '13px'}),
            html.Td(r['Stockout Risk'], style={'padding': '10px', 'textAlign': 'center', 
                'borderBottom': f'1px solid {DB_COLORS["light_gray"]}', 'fontSize': '13px'})
        ]) for _, r in kpis.iterrows()]
        
        kpi = html.Table([html.Thead(html.Tr([html.Th(h, style={'padding': '10px', 'textAlign': 'left' if i == 0 else 'center', 
            'borderBottom': f'2px solid {DB_COLORS["dark"]}', 'fontWeight': '600', 'fontSize': '14px'})
            for i, h in enumerate(['Site', 'Sufficient Inventory', 'Low Inventory Risk', 'Stockout Risk'])])), 
            html.Tbody(rows)], style={'width': '100%', 'borderCollapse': 'collapse', 
                                     'fontFamily': 'DM Sans, sans-serif', 'color': DB_COLORS['dark']})
    
    # Build map markers with tooltips
    markers = []
    if not df.empty:
        # Aggregate risk by site (worst risk wins)
        sr = df.groupby(['plant_id', 'plant_name', 'lat', 'lon']).agg(
            risk_level=('risk_level', lambda x: 'Out of Stock' if 'Out of Stock' in x.values 
                       else ('Low Stock' if 'Low Stock' in x.values else 'Stocked'))).reset_index()
        
        for _, r in sr.iterrows():
            sdf = df[df['plant_id'] == r['plant_id']]
            parts = []
            for rl, rc in [('Stocked', 'green'), ('Low Stock', 'orange'), ('Out of Stock', 'red')]:
                pl = ', '.join(sorted(sdf[sdf['risk_level'] == rl]['part_name'].unique()))
                parts.append(html.Div([html.Span('✓ ' if rl == 'Stocked' else ('⚠ ' if rl == 'Low Stock' else '✗ '), 
                    style={'color': rc, 'fontWeight': 'bold', 'fontSize': '14px'}),
                    html.Span(f'{rl}: ', style={'fontWeight': '500'}),
                    html.Span(pl or 'None', style={'fontSize': '11px', 'color': '#555', 'wordWrap': 'break-word'})
                ], style={'marginBottom': '6px', 'wordWrap': 'break-word', 'overflowWrap': 'break-word'}))
            
            markers.append(dl.CircleMarker(id=f"marker-{r['plant_id']}-{r['risk_level']}",
                center=[float(r['lat']), float(r['lon'])], radius=10, color=RISK_COLORS[r['risk_level']], 
                fillColor=RISK_COLORS[r['risk_level']], fillOpacity=0.7, weight=2,
                children=[dl.Tooltip(html.Div([html.Div(r['plant_name'], style={'fontWeight': 'bold', 'fontSize': '14px', 
                    'marginBottom': '10px', 'paddingBottom': '8px', 'borderBottom': '2px solid #ccc', 'color': '#0B2026',
                    'wordWrap': 'break-word', 'overflowWrap': 'break-word'}), *parts], style={'padding': '8px', 
                    'minWidth': '350px', 'maxWidth': '450px', 'fontFamily': 'DM Sans, sans-serif', 'lineHeight': '1.4',
                    'wordWrap': 'break-word', 'overflowWrap': 'break-word', 'whiteSpace': 'normal'}), 
                    permanent=False, direction='auto')]))
    
    # Build AG Grid data
    gdf = df.copy()
    if 'work_order_id' in gdf.columns:
        gdf = gdf.drop_duplicates(subset=['plant_name', 'part_name', 'equip_name', 'work_order_id'], keep='first')
    gdf['risk_sort'] = gdf['risk_level'].map(RISK_PRIORITY)
    gdf = gdf.sort_values('risk_sort')
    
    cols = ['plant_name', 'part_name', 'equip_name', 'work_order_id', 'planned_date', 'required_part_quantity', 
            'on_hand_stock', 'reserved_qty', 'projected_available_stock', 'safety_stock', 'shortage_quantity', 
            'risk_level', 'criticality']
    names = {'plant_name': 'Plant Name', 'part_name': 'Part Name', 'equip_name': 'Equipment Name', 
             'work_order_id': 'Work Order ID', 'planned_date': 'Planned Date', 'required_part_quantity': 'Required Quantity',
             'on_hand_stock': 'On Hand Stock', 'reserved_qty': 'Reserved Qty', 'projected_available_stock': 'Projected Stock',
             'safety_stock': 'Safety Stock', 'shortage_quantity': 'Shortage Qty', 'risk_level': 'Risk Level', 
             'criticality': 'Criticality'}
    tips = {'plant_name': 'Mine site location', 'part_name': 'Spare part name or description',
            'equip_name': 'Equipment that requires this part', 'work_order_id': 'Work order number for planned maintenance',
            'planned_date': 'Scheduled date for work order', 'required_part_quantity': 'Number of parts needed',
            'on_hand_stock': 'Current inventory available', 'reserved_qty': 'Parts already allocated',
            'projected_available_stock': 'Expected available stock', 'safety_stock': 'Minimum inventory threshold',
            'shortage_quantity': 'Gap between required and available', 'risk_level': 'Inventory status', 
            'criticality': 'Priority level'}
    
    vc = [c for c in cols if c in gdf.columns and c != 'risk_sort']
    cdefs = [{"field": c, "headerName": names.get(c, c), "headerTooltip": tips.get(c, names.get(c, c)),
             "sortable": True, "filter": True} for c in vc]
    
    return markers, kpi, gdf.to_dict('records'), cdefs

@app.callback([Output('ai-response-content', 'children'), Output('ai-response-content', 'style'),
               Output('ai-loading', 'style')],
              [Input('ai-allocation-button', 'n_clicks')],
              [State('part-filter', 'value'), State('site-filter', 'value'), State('equipment-filter', 'value'),
               State('risk-filter', 'value'), State('data-grid', 'rowData')], prevent_initial_call=True)
def generate_ai(n, part, site, equip, risk, grid):
    """Generate AI recommendations for part allocation based on current filters and data"""
    # Convert grid data to DataFrame
    gdf = pd.DataFrame(grid) if grid else pd.DataFrame()
    
    # Get inventory data for the selected part across all sites
    inv = inventory_data[inventory_data['part_name'] == part] if part else pd.DataFrame()
    
    # Format data as readable strings for LLM prompt
    if not gdf.empty:
        grid_str = gdf.to_string(index=False)
    else:
        grid_str = "No grid data available"
    
    if not inv.empty:
        inv_str = inv.to_string(index=False)
    else:
        inv_str = "No inventory data available"
    
    # Build prompt with context data
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")
    prompt = INVENTORY_RECOMMENDATION_PROMPT.format(grid_df=grid_str, inventory_data=inv_str, current_date=current_date)
    
    try:
        resp = call_databricks_llm(prompt)
        return html.Div([dcc.Markdown(resp, dangerously_allow_html=True, style={'color': DB_COLORS['dark'],
            'fontFamily': 'DM Sans, sans-serif', 'lineHeight': '1.6'})
        ], style={'width': '100%'}, className='markdown-content'), \
            {'display': 'block', 'maxHeight': '400px', 'overflowY': 'auto', 'padding': '10px', 'marginBottom': '20px'}, \
            {'display': 'none'}
    except Exception as e:
        return html.Div([html.P("Error:", style={'margin': '0 0 10px 0', 'color': '#d32f2f', 
            'fontFamily': 'DM Sans, sans-serif', 'fontWeight': '500'}),
            html.P(str(e), style={'margin': '0', 'color': DB_COLORS['dark'], 'fontFamily': 'DM Sans, sans-serif', 
                                 'whiteSpace': 'pre-wrap', 'lineHeight': '1.6'})]), \
            {'display': 'block', 'maxHeight': '400px', 'overflowY': 'auto', 'padding': '10px', 'marginBottom': '20px'}, \
            {'display': 'none'}

@app.callback(
    Output('chat-panel', 'style'),
    [Input('toggle-chat-panel', 'n_clicks'),
     Input('close-chat-panel', 'n_clicks')],
    [State('chat-panel', 'style')],
    prevent_initial_call=True
)
def toggle_chat_panel(open_clicks, close_clicks, current_style):
    """Toggle the embedded chat panel"""
    ctx = callback_context
    if not ctx.triggered:
        return current_style
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    new_style = current_style.copy()
    
    if button_id == 'toggle-chat-panel':
        # Toggle open/closed
        if new_style.get('right') == '-500px':
            new_style['right'] = '0'
        else:
            new_style['right'] = '-500px'
    elif button_id == 'close-chat-panel':
        # Close
        new_style['right'] = '-500px'
    
    return new_style

@app.callback(
    [Output('chat-messages', 'children'),
     Output('conversation-history', 'data'),
     Output('chat-input', 'value'),
     Output('send-chat-message', 'disabled')],
    [Input('send-chat-message', 'n_clicks'),
     Input('clear-chat', 'n_clicks'),
     Input('chat-panel', 'style')],
    [State('chat-input', 'value'),
     State('conversation-history', 'data'),
     State('chat-messages', 'children')],
    prevent_initial_call=True
)
def handle_chat_interaction(send_clicks, clear_clicks, panel_style, user_input, history, current_messages):
    """Handle chat messages and responses using Genie API"""
    ctx = callback_context
    if not ctx.triggered:
        return current_messages, history or [], "", False
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Clear chat
    if button_id == 'clear-chat':
        welcome_msg = html.Div([
            html.Div("Genie AI", style={
                'display': 'inline-block',
                'padding': '4px 12px',
                'backgroundColor': DB_COLORS['primary'],
                'color': 'white',
                'borderRadius': '12px',
                'fontSize': '11px',
                'fontWeight': '600',
                'marginBottom': '8px',
                'fontFamily': 'DM Sans, sans-serif'
            }),
            dcc.Markdown(
                "👋 Chat cleared! Ask me anything about your supply chain data.",
                style={
                    'backgroundColor': '#f0f0f0',
                    'padding': '12px 16px',
                    'borderRadius': '12px',
                    'marginBottom': '16px',
                    'color': DB_COLORS['dark'],
                    'fontSize': '14px',
                    'lineHeight': '1.5',
                    'fontFamily': 'DM Sans, sans-serif'
                }
            )
        ], style={'marginBottom': '12px'})
        return [welcome_msg], [], "", False
    
    # Load initial insights when panel opens
    if button_id == 'chat-panel' and panel_style.get('right') == '0':
        if not history or len(history) == 0:
            insights = get_quick_insights()
            welcome_msg = html.Div([
                html.Div("Genie AI", style={
                    'display': 'inline-block',
                    'padding': '4px 12px',
                    'backgroundColor': DB_COLORS['primary'],
                    'color': 'white',
                    'borderRadius': '12px',
                    'fontSize': '11px',
                    'fontWeight': '600',
                    'marginBottom': '8px',
                    'fontFamily': 'DM Sans, sans-serif'
                }),
                dcc.Markdown(
                    insights,
                    style={
                        'backgroundColor': '#f0f0f0',
                        'padding': '12px 16px',
                        'borderRadius': '12px',
                        'marginBottom': '16px',
                        'color': DB_COLORS['dark'],
                        'fontSize': '14px',
                        'lineHeight': '1.5',
                        'fontFamily': 'DM Sans, sans-serif'
                    }
                )
            ], style={'marginBottom': '12px'})
            return [welcome_msg], [], "", False
        return current_messages, history, "", False
    
    # Send message - show user message and thinking indicator immediately
    if button_id == 'send-chat-message':
        if not user_input or user_input.strip() == "":
            return current_messages, history or [], "", False
        
        # Initialize history if None
        if history is None:
            history = []
        
        # Add user message to display immediately
        user_msg = html.Div([
            html.Div("You", style={
                'display': 'inline-block',
                'padding': '4px 12px',
                'backgroundColor': '#e3f2fd',
                'color': '#1976d2',
                'borderRadius': '12px',
                'fontSize': '11px',
                'fontWeight': '600',
                'marginBottom': '8px',
                'fontFamily': 'DM Sans, sans-serif'
            }),
            html.Div(
                user_input,
                style={
                    'backgroundColor': '#e3f2fd',
                    'padding': '12px 16px',
                    'borderRadius': '12px',
                    'marginBottom': '16px',
                    'color': DB_COLORS['dark'],
                    'fontSize': '14px',
                    'lineHeight': '1.5',
                    'fontFamily': 'DM Sans, sans-serif'
                }
            )
        ], style={'marginBottom': '12px', 'textAlign': 'right'})
        
        # Add thinking message
        thinking_msg = html.Div([
            html.Div("Genie AI", style={
                'display': 'inline-block',
                'padding': '4px 12px',
                'backgroundColor': DB_COLORS['primary'],
                'color': 'white',
                'borderRadius': '12px',
                'fontSize': '11px',
                'fontWeight': '600',
                'marginBottom': '8px',
                'fontFamily': 'DM Sans, sans-serif'
            }),
            html.Div(
                "🤔 Thinking and querying your data...",
                style={
                    'backgroundColor': '#f0f0f0',
                    'padding': '12px 16px',
                    'borderRadius': '12px',
                    'marginBottom': '16px',
                    'color': DB_COLORS['dark'],
                    'fontSize': '14px',
                    'lineHeight': '1.5',
                    'fontFamily': 'DM Sans, sans-serif',
                    'fontStyle': 'italic'
                }
            )
        ], style={'marginBottom': '12px'})
        
        # IMMEDIATELY show user message + thinking indicator (don't wait for Genie)
        immediate_messages = current_messages + [user_msg, thinking_msg]
        
        # Get Genie AI response in the background
        ai_response, genie_conversation_id = get_chat_response(user_input, history)
        
        # Add AI message to display (replaces thinking message)
        ai_msg = html.Div([
            html.Div("Genie AI", style={
                'display': 'inline-block',
                'padding': '4px 12px',
                'backgroundColor': DB_COLORS['primary'],
                'color': 'white',
                'borderRadius': '12px',
                'fontSize': '11px',
                'fontWeight': '600',
                'marginBottom': '8px',
                'fontFamily': 'DM Sans, sans-serif'
            }),
            dcc.Markdown(
                ai_response,
                style={
                    'backgroundColor': '#f0f0f0',
                    'padding': '12px 16px',
                    'borderRadius': '12px',
                    'marginBottom': '16px',
                    'color': DB_COLORS['dark'],
                    'fontSize': '14px',
                    'lineHeight': '1.5',
                    'fontFamily': 'DM Sans, sans-serif'
                }
            )
        ], style={'marginBottom': '12px'})
        
        # Update conversation history with Genie conversation ID
        history.append({
            'role': 'User', 
            'content': user_input,
            'genie_conversation_id': genie_conversation_id
        })
        history.append({
            'role': 'AI', 
            'content': ai_response,
            'genie_conversation_id': genie_conversation_id
        })
        
        # Update messages display (user + AI, no thinking message)
        new_messages = current_messages + [user_msg, ai_msg]
        
        return new_messages, history, "", False
    
    return current_messages, history or [], "", False

# Enter key support is now handled via inline JavaScript in layout.py

if __name__ == "__main__":
    app.run()

