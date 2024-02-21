
from flask import Flask, render_template, jsonify, request
from PIL import Image

# creates a Flask application, named app
app = Flask(__name__, static_url_path='/static')

# a route to display our html page gotten from [react-chat-widget](https://github.com/mrbot-ai/rasa-webchat)
@app.route("/")
def index():  
    return render_template('index.html')
# global count
# count = 0
@app.route('/send/image', methods=['GET','POST'])
def image_upload():
    # global count
    # print("홀짝: ", count)
    # print(request.form)
    print(request.files) 
    # count += 1
    file_receive = request.files['file']
    img = Image.open(file_receive)
    img.save('file_receive.jpg')
    #img.save('/home/zio/rasa1/static/js/change.png')

    return "성공"  # 저장 완료됨을 알림

# run the application ddss
if __name__ == "__main__": 
    app.run(host='0.0.0.0', port="5000", debug=True) 
    # app.run(debug=True)