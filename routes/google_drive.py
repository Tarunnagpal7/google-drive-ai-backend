from flask import Blueprint, request, jsonify,session
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import networkx as nx

drive_bp = Blueprint("drive", __name__)

@drive_bp.route("/drive/status")
def drive_status():
    creds_data = session.get('credentials')
    if not creds_data:
        return jsonify({"connected": False})
    
    return jsonify({"connected": True})



@drive_bp.route("/report", methods=["GET"])
def report():
    try:
        if 'credentials' not in session:
            return jsonify({"error": "Not authorized"}), 401

        creds = Credentials(**session['credentials'])
        service = build('drive', 'v3', credentials=creds)

        all_files = []
        page_token = None
        while True:
            response = service.files().list(
                q="'me' in owners and trashed = false",
                spaces='drive',
                fields='nextPageToken, files(id, name, mimeType, parents, owners)',
                pageToken=page_token
            ).execute()
            all_files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        my_files = [f for f in all_files if f.get('owners', [{}])[0].get('me', True)]

        folder_map = {}
        file_info = {}
        for f in my_files:
            file_info[f['id']] = {
                'name': f['name'],
                'mimeType': f['mimeType'],
                'parents': f.get('parents', [])
            }

        G = nx.DiGraph()
        for fid, info in file_info.items():
            label = info['name']
            if info['mimeType'] == 'application/vnd.google-apps.folder':
                label += ' (folder)'
            else:
                label += f' ({info["mimeType"].split("/")[-1]})'
            G.add_node(fid, label=label)

            for pid in info['parents']:
                if pid not in G:
                    G.add_node(pid, label=f"Unknown Folder ({pid})")
                G.add_edge(pid, fid)

        tree_data = {
            node: {
                'label': G.nodes[node]['label'],
                'children': list(G.successors(node))
            } for node in G.nodes
        }

        return jsonify(tree_data)

    except Exception as e:
        print("🚨 /report error:", e)
        return jsonify({"error": str(e)}), 500
