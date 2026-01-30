# New polling-based callbacks for progressive Genie status display

# Callback 1: Handle Send button - start query and show immediate feedback
@app.callback(
    [Output('chat-messages', 'children'),
     Output('chat-input', 'value'),
     Output('send-chat-message', 'disabled'),
     Output('genie-polling-data', 'data'),
     Output('genie-status-poller', 'disabled')],
    [Input('send-chat-message', 'n_clicks'),
     Input('clear-chat', 'n_clicks'),
     Input('chat-panel', 'style')],
    [State('chat-input', 'value'),
     State('conversation-history', 'data'),
     State('chat-messages', 'children')],
    prevent_initial_call=True
)
def handle_send_message(send_clicks, clear_clicks, panel_style, user_input, history, current_messages):
    """Handle Send click - start Genie query and show user message immediately"""
    ctx = callback_context
    if not ctx.triggered:
        return current_messages, "", False, None, True
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Clear chat
    if button_id == 'clear-chat':
        insights = get_quick_insights()
        welcome_msg = html.Div([
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
            dcc.Markdown(insights, style={
                'backgroundColor': '#f0f0f0',
                'padding': '12px 16px',
                'borderRadius': '12px',
                'marginBottom': '16px',
                'color': DB_COLORS['dark'],
                'fontSize': '14px',
                'lineHeight': '1.5',
                **FONT_STYLE
            })
        ], style={'marginBottom': '12px'})
        return [welcome_msg], "", False, None, True
    
    # Load initial insights when panel opens
    if button_id == 'chat-panel' and panel_style.get('right') == '0':
        if not history or len(history) == 0:
            insights = get_quick_insights()
            welcome_msg = html.Div([
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
                dcc.Markdown(insights, style={
                    'backgroundColor': '#f0f0f0',
                    'padding': '12px 16px',
                    'borderRadius': '12px',
                    'marginBottom': '16px',
                    'color': DB_COLORS['dark'],
                    'fontSize': '14px',
                    'lineHeight': '1.5',
                    **FONT_STYLE
                })
            ], style={'marginBottom': '12px'})
            return [welcome_msg], "", False, None, True
        return current_messages, "", False, None, True
    
    # Send message - START GENIE QUERY AND SHOW IMMEDIATELY
    if button_id == 'send-chat-message':
        if not user_input or user_input.strip() == "":
            return current_messages, "", False, None, True
        
        # Get conversation ID from history
        genie_conversation_id = None
        if history:
            for msg in history:
                if msg.get('genie_conversation_id'):
                    genie_conversation_id = msg['genie_conversation_id']
                    break
        
        # START the Genie query (doesn't wait for completion)
        query_result = start_genie_query(user_input, genie_conversation_id)
        
        if not query_result.get('success'):
            # Error starting query
            error_msg = html.Div([
                html.Div("Error", style={
                    'display': 'inline-block',
                    'padding': '4px 12px',
                    'backgroundColor': '#f44336',
                    'color': 'white',
                    'borderRadius': '12px',
                    'fontSize': '11px',
                    'fontWeight': '600',
                    'marginBottom': '8px',
                    **FONT_STYLE
                }),
                html.Div(query_result.get('error', 'Failed to start query'), style={
                    'backgroundColor': '#ffebee',
                    'padding': '12px 16px',
                    'borderRadius': '12px',
                    'marginBottom': '16px',
                    'color': DB_COLORS['dark'],
                    'fontSize': '14px',
                    **FONT_STYLE
                })
            ], style={'marginBottom': '12px'})
            return current_messages + [error_msg], "", False, None, True
        
        # Show user message IMMEDIATELY
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
                **FONT_STYLE
            }),
            html.Div(user_input, style={
                'backgroundColor': '#e3f2fd',
                'padding': '12px 16px',
                'borderRadius': '12px',
                'marginBottom': '16px',
                'color': DB_COLORS['dark'],
                'fontSize': '14px',
                'lineHeight': '1.5',
                **FONT_STYLE
            })
        ], style={'marginBottom': '12px'})
        
        # Show initial "thinking" status
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
                **FONT_STYLE
            }),
            html.Div("📝 Starting query...", id='genie-status-message', style={
                'backgroundColor': '#f0f0f0',
                'padding': '12px 16px',
                'borderRadius': '12px',
                'marginBottom': '16px',
                'color': DB_COLORS['dark'],
                'fontSize': '14px',
                'fontStyle': 'italic',
                **FONT_STYLE
            })
        ], style={'marginBottom': '12px'}, id='genie-thinking-container')
        
        # Store polling data
        polling_data = {
            'conversation_id': query_result['conversation_id'],
            'message_id': query_result['message_id'],
            'hostname': query_result['hostname'],
            'token': query_result['token'],
            'user_question': user_input,
            'poll_count': 0
        }
        
        # Return: user message + thinking message, enable polling
        immediate_messages = current_messages + [user_msg, thinking_msg]
        return immediate_messages, "", True, polling_data, False
    
    return current_messages, "", False, None, True


# Callback 2: Poll Genie status and update progressively
@app.callback(
    [Output('genie-status-message', 'children'),
     Output('genie-thinking-container', 'children', allow_duplicate=True),
     Output('conversation-history', 'data'),
     Output('send-chat-message', 'disabled', allow_duplicate=True),
     Output('genie-status-poller', 'disabled', allow_duplicate=True),
     Output('genie-polling-data', 'data', allow_duplicate=True)],
    [Input('genie-status-poller', 'n_intervals')],
    [State('genie-polling-data', 'data'),
     State('conversation-history', 'data')],
    prevent_initial_call=True
)
def poll_genie_status(n_intervals, polling_data, history):
    """Poll Genie for status updates and show progress"""
    if not polling_data:
        return dash.no_update, dash.no_update, history or [], False, True, None
    
    # Check current status
    status_result = check_genie_status(
        polling_data['conversation_id'],
        polling_data['message_id'],
        polling_data['hostname'],
        polling_data['token']
    )
    
    if not status_result.get('success'):
        # Error checking status
        error_content = [
            html.Div("Genie AI", style={
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
            html.Div(f"❌ {status_result.get('message', 'Error checking status')}", style={
                'backgroundColor': '#ffebee',
                'padding': '12px 16px',
                'borderRadius': '12px',
                'marginBottom': '16px',
                'color': DB_COLORS['dark'],
                'fontSize': '14px',
                **FONT_STYLE
            })
        ]
        return dash.no_update, error_content, history or [], False, True, None
    
    current_status = status_result.get('status')
    status_message = status_result.get('message')
    
    # If still processing, update status message and continue polling
    if current_status != 'COMPLETED':
        polling_data['poll_count'] = polling_data.get('poll_count', 0) + 1
        
        # Timeout after 30 polls (60 seconds)
        if polling_data['poll_count'] > 30:
            timeout_content = [
                html.Div("Genie AI", style={
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
                dcc.Markdown("⏱️ Query is taking longer than expected. Please try a simpler question.", style={
                    'backgroundColor': '#fff3cd',
                    'padding': '12px 16px',
                    'borderRadius': '12px',
                    'marginBottom': '16px',
                    'color': DB_COLORS['dark'],
                    'fontSize': '14px',
                    **FONT_STYLE
                })
            ]
            return dash.no_update, timeout_content, history or [], False, True, None
        
        # Continue polling, update status message
        return status_message, dash.no_update, history or [], True, False, polling_data
    
    # COMPLETED! Show final answer
    response_text = status_result.get('response', 'No response received')
    sql_query = status_result.get('sql')
    
    if sql_query:
        response_text += f"\n\n**Query used:**\n```sql\n{sql_query}\n```"
    
    final_content = [
        html.Div("Genie AI", style={
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
        dcc.Markdown(response_text, style={
            'backgroundColor': '#f0f0f0',
            'padding': '12px 16px',
            'borderRadius': '12px',
            'marginBottom': '16px',
            'color': DB_COLORS['dark'],
            'fontSize': '14px',
            'lineHeight': '1.5',
            **FONT_STYLE
        })
    ]
    
    # Update history
    if history is None:
        history = []
    
    history.append({
        'role': 'User',
        'content': polling_data['user_question'],
        'genie_conversation_id': polling_data['conversation_id']
    })
    history.append({
        'role': 'AI',
        'content': response_text,
        'genie_conversation_id': polling_data['conversation_id']
    })
    
    # Return final answer, stop polling, re-enable button
    return dash.no_update, final_content, history, False, True, None
