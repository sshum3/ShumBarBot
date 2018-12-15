from flask import Flask, render_template, request, redirect, url_for
import json, time, serial

app = Flask(__name__)
app.secret_key = 'shumugfdsghjk'
app.config['SERVER_NAME'] = '192.168.1.33'


ser = serial.Serial('/dev/ttyACM0', 9600)
@app.route('/')
def needToLogin():
    return redirect(url_for('login'))

@app.route('/home/<username>')
def index(username):
    #Check if logged in...
    if 'username' == "":
        return redirect(url_for('login'))
    
    #Get Data
    with open('drinkdata.txt') as data_file:
        data = json.load(data_file)
    
    return render_template('index.html', username=username, cocktails=data['cocktails'])

    

    
@app.route('/mix/<id>/<username>')
def mix(id,username):
    #Get Data
    with open('drinkdata.txt') as data_file:
        data = json.load(data_file)
    
    for index, i in enumerate(data['cocktails']):
        if i['id'] == id:
            whatToMix = i['ingredients']
            nameOfCocktail = i['name']
            break
    
    #Send data to Arduino
    for alco in whatToMix:
        print(data['ingredients'][alco])
        ser.write(bytes(str(data['ingredients'][alco]), 'UTF-8'))
        ser.write(bytes("\n", 'UTF-8'))
        time.sleep(0.1)
    ser.write(bytes('100', 'UTF-8'))
    ser.write(bytes("\n", 'UTF-8'))
    
    data['cocktails'][index]['count'] += 1
    #Save Data
    with open('drinkdata.txt', 'w') as outfile:
        json.dump(data, outfile)
    return render_template('mix.html', nameOfCocktail=nameOfCocktail,username=username)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print('Setting Username' + request.form['username'])
        return redirect(url_for('index', username = request.form['username']))
    return render_template('login.html')


@app.route('/make/<username>', methods=['GET', 'POST'])
def make(username):
    #Check if logged in...
    if 'username' == "":
        return redirect(url_for('login'))
    
    #Get Data
    with open('drinkdata.txt') as data_file:
        data = json.load(data_file)
    
    if request.method == 'POST':
        cocking = []
        for ing in data['ingredients']:
            for i in range(int(request.form[ing])):
                cocking.append(ing)
        
        drinkId = str(int(time.time())) + request.form['cocktailname'];
        
        newcocktail = {'id': drinkId , 'name' : request.form['cocktailname'], 'ingredients' : cocking[:8], 'instructions': request.form['instructions'], 'count' : 0, 'createdby' : username }
        
        data['cocktails'].append(newcocktail)
        with open('drinkdata.txt', 'w') as outfile:
            json.dump(data, outfile)
        return redirect(url_for('index', username=username) + '#' + drinkId)
        
    else:
        """
        data = {'ingredients' : ['Vodka', 'White Rum', 'Dark Rum']}
        with open('drinkdata.txt', 'w') as outfile:
            json.dump(data, outfile)
        """

        return render_template('make.html', ingredients=data['ingredients'])


@app.route('/reset')
def reset():
	data = {
		'ingredients' : {'Gin': 4, 'Whiskey': 3, 'Vodka' : 2, 'White Rum' : 1, 'Dark Rum':0, 'Passoa': -1, 'Blackcurrant Liqueur': -2, 'Triple Sec': -3, 'Coffee Liqueur': -4},
		'cocktails' : [
			{'id': '1 Test', 'name' : 'Test', 'createdby' : 'Stuart', 'ingredients' : ['Vodka', 'Vodka', 'White Rum'], 'instructions': 'Add Lime', 'count' : 0 }
		]
	}
	for i in data['cocktails'][0]:
		print(i)
	
    #Save Data
	with open('drinkdata.txt', 'w') as outfile:
		json.dump(data, outfile)
	return 'Reset'


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80, threaded=True) #add when ready, threaded=True

#debug=True, 