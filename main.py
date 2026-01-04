from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import base64
import io
import os
from app import build_rag
from app import ask_rag


UPLOAD_FOLDER = "uploaded_pdfs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# 🔥 Clear old files on app start
for file in os.listdir(UPLOAD_FOLDER):
    file_path = os.path.join(UPLOAD_FOLDER, file)
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
    except Exception as e:
        print("Error deleting file:", e)
app = Dash(__name__, 
           external_stylesheets=[
               dbc.themes.DARKLY,
               dbc.icons.FONT_AWESOME,
               "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap"
           ])

app.layout = html.Div([
    # Background elements
    html.Div(className="background-shapes"),
    
    # Main container
    dbc.Container([
        dbc.Row([
            dbc.Col([
                # Header with logo
                html.Div([
                    html.Div([
                        html.I(className="fas fa-brain fa-2x gradient-text mr-3"),
                        html.H1("Doku AI", className="display-4 gradient-text font-weight-bold mb-0")
                    ], className="d-flex align-items-center justify-content-center mb-4"),
                    html.P("Intelligent Document Analysis Assistant", 
                          className="text-center subheader mb-5")
                ], className="header-container"),
                
                # Upload Section
                html.Div([
                    html.Div([
                        html.I(className="fas fa-cloud-upload-alt fa-3x mb-3 icon-upload"),
                        html.H3("Upload Document", className="mb-4"),
                        dcc.Upload(
                            id='upload-document',
                            children=html.Div([
                                dbc.Button([
                                    html.I(className="fas fa-file-import mr-2"),
                                    "Choose Document"
                                ], color="primary", size="lg", className="upload-btn")
                            ]),
                            multiple=False,
                            className="upload-area"
                        ),
                        html.Div(id='upload-badge-container', className="mt-4")
                    ], className="upload-container text-center")
                ], className="card-glass mb-5"),
                
                # Chat Interface
                html.Div([
                    html.H4([
                        html.I(className="fas fa-comments mr-2"),
                        "Ask Doku AI"
                    ], className="mb-4 text-center"),
                    
                    # Message History
                    html.Div(id='chat-history', className="chat-container mb-4"),
                    
                    # Input Area
                    html.Div([
                        dbc.InputGroup([
                            dbc.Input(
                                id="question-input",
                                placeholder="Ask anything about your document...",
                                className="chat-input",
                                type="text"
                            ),
                            dbc.Button(
                                [
                                    html.I(className="fas fa-paper-plane"),
                                    html.Span(" Send", className="ml-2 d-none d-md-inline")
                                ],
                                id="ask-button",
                                color="primary",
                                className="send-btn",
                                n_clicks=0
                            )
                        ], className="input-group-custom")
                    ], className="input-container")
                ], className="card-glass"),
                
                # Features Grid
                html.Div([
                    html.H4("Capabilities", className="text-center mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.I(className="fas fa-search fa-2x mb-3 feature-icon"),
                                html.H5("Smart Search", className="mb-2"),
                                html.P("Find information instantly", className="text-muted small")
                            ], className="text-center feature-card")
                        ], md=6, sm=12, className="mb-3"),
                        dbc.Col([
                            html.Div([
                                html.I(className="fas fa-file-contract fa-2x mb-3 feature-icon"),
                                html.H5("Document Analysis", className="mb-2"),
                                html.P("Extract key insights", className="text-muted small")
                            ], className="text-center feature-card")
                        ], md=6, sm=12, className="mb-3"),
                        # dbc.Col([
                        #     html.Div([
                        #         html.I(className="fas fa-chart-line fa-2x mb-3 feature-icon"),
                        #         html.H5("Data Extraction", className="mb-2"),
                        #         html.P("Tables & statistics", className="text-muted small")
                        #     ], className="text-center feature-card")
                        # ], md=3, sm=6, className="mb-3"),
                        # dbc.Col([
                        #     html.Div([
                        #         html.I(className="fas fa-lightbulb fa-2x mb-3 feature-icon"),
                        #         html.H5("Insight Generation", className="mb-2"),
                        #         html.P("Get summarized insights", className="text-muted small")
                        #     ], className="text-center feature-card")
                        # ], md=3, sm=6, className="mb-3"),
                    ], className="mt-4")
                ], className="card-glass mt-4"),
                
                # Footer
                html.Div([
                    html.P([
                        "Powered by ",
                        html.Span("Advanced AI", className="gradient-text"),
                        " • Secure • Fast • Accurate"
                    ], className="text-center mb-0"),
                    html.P("© 2026 Doku AI. All rights reserved.", 
                          className="text-center text-muted small mt-2")
                ], className="footer mt-5")
                
            ], width=12, lg=10, xl=8, className="mx-auto"),
            dcc.Store(id='uploaded-file-store', storage_type='memory', data=[])
        ])
    ], fluid=True, className="main-container")
], className="app-container")

# Callbacks for upload and chat
@callback(
    Output('upload-badge-container', 'children'),
    Input('upload-document', 'contents'),
    State('upload-document', 'filename')
)
def update_upload_badge(contents, filename):
    if contents is not None:
        save_pdf(contents, filename)
        build_rag()   # 🔥 Build RAG once after upload

        return dbc.Badge(
            f"✓ {filename} uploaded and indexed",
            color="success",
            className="upload-badge p-3"
        )
    return dbc.Badge("Ready for document upload", color="secondary")




def save_pdf(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        f.write(decoded)
        return path


@callback(
    Output('chat-history', 'children'),
    Output('question-input', 'value'),
    Input('ask-button', 'n_clicks'),
    State('question-input', 'value'),
    State('chat-history', 'children')
)
def update_chat(n_clicks, question, history):
    if n_clicks > 0 and question:
        history = history or []

        user_msg = html.Div(question, className="user-message")
        ai_reply = ask_rag(question)

        ai_msg = html.Div(ai_reply, className="ai-message")

        history.extend([
            html.Div(user_msg, className="chat-bubble user"),
            html.Div(ai_msg, className="chat-bubble ai")
        ])

        return history, ""

    return history or [], question


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)