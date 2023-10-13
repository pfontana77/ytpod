from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/feed.xml')
def serve_feed():
    return send_from_directory('.', 'feed.xml')

@app.route('/output/<filename>')
def serve_file(filename):
    return send_from_directory('output', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
