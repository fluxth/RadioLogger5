from gui import app

# !! TEMP FOR DEV
@app.after_request
def apply_caching(response):
    response.headers['Access-Control-Allow-Origin'] = "http://127.0.0.1:3000"
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, X-Requested-With'
    return response

app.run(debug=True)