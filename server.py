from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def test():
    return 'ur here'


@app.route('/events', methods=["POST"])
def events():

    chal_id = request.form.get('challenge')
    print request.form.items()
    print chal_id
    return chal_id

if __name__ == '__main__':
    app.run(port=5050)
