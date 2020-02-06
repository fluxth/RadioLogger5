from gui import app

@app.after_request
def apply_caching(response):
    response.headers['Access-Control-Allow-Origin'] = '*' 
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, X-Requested-With, Content-Type'
    return response

app.run(host='0.0.0.0', port=5003, debug=True)