from flask import Flask, render_template, url_for
from flask import request, redirect, flash, make_response, jsonify
from Laptops_Database_Setup import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
import random
import string
import json


from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Shoe Mart"


db_engine = create_engine('sqlite:///laptops_catalog.db', connect_args={'check_same_thread': False}, echo=True)


Base.metadata.create_all(db_engine)
Database_Session = sessionmaker(bind=db_engine)
session = Database_Session()

#google signin

@app.route('/gconnect', methods=['POST'])
def gconnect():
    	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid State parameter'), 401)
        	response.headers['Content-Type'] = 'application/json'
        	return response
    	code = request.data

    	try:
        	oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        	oauth_flow.redirect_uri = 'postmessage'
        	credentials = oauth_flow.step2_exchange(code)
    	except FlowExchangeError:
        	response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        	response.headers['Content-Type'] = 'application/json'
        	return response
    	access_token = credentials.access_token
    	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    	h = httplib2.Http()
    	result = json.loads(h.request(url, 'GET')[1])

    	if result.get('error') is not None:
        	response = make_response(json.dumps(result.get('error')), 500)
        	response.headers['Content-Type'] = 'application/json'
        	return response

    	gplus_id = credentials.id_token['sub']
    	if result['user_id'] != gplus_id:
        	response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        	response.headers['Content-Type'] = 'application/json'
        	return response

   	if result['issued_to'] != CLIENT_ID:
		response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        	print("Token's client ID does not match app's.")
        	response.headers['Content-Type'] = 'application/json'
        	return response

    	stored_access_token = login_session.get('access_token')
   	stored_gplus_id = login_session.get('gplus_id')
	
    	if stored_access_token is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'), 200)
         	response.headers['Content-Type'] = 'application/json'
         	return response

    	login_session['access_token'] = credentials.access_token
    	login_session['gplus_id'] = gplus_id

    	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    	params = {'access_token': credentials.access_token, 'alt': 'json'}
    	answer = requests.get(userinfo_url, params=params)

    	data = answer.json()

    	login_session['username'] = data['name']
    	login_session['picture'] = data['picture']
    	login_session['email'] = data['email']

    	user_id = getUserID(login_session['email'])
    	if not user_id:
        	user_id = createUser(login_session)
    	login_session['user_id'] = user_id

    	output = ''
    	output += '<center><h2><font color="green">Welcome '
    	output += login_session['username']
    	output += '!</font></h2></center>'
    	output += '<center><img src="'
    	output += login_session['picture']
    	output += \
        	' " style = "width: 299px; height: 299px;border-radius:129px;- \
     		 webkit-border-radius:139px;-moz-border-radius: 139px;">'
    	flash("you are now logged in as %s" % login_session['username'])
    	print("Done")
    	return output


#user signup


def createUser(login_session):
	newUser = User(name=login_session['username'],email=login_session['email'],picture=login_session['picture'])
    	session.add(newUser)
   	session.commit()


#retrive user_data


def getUserInfo(user_id):
	user = session.query(User).filter_by(id=user_id).one()
    	return user


#get userid


def getUserID(email):
	try:
		user = session.query(User).filter_by(email=email).one()
        	return user.id
    	except Exception as e:
        	return None



#index page 

@app.route('/')
def index():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits)for x in range(32))
   	login_session['state'] = state
    	companies = session.query(Company).all()
	laptops = session.query(Laptop).all()
    	return render_template('index.html', STATE=state, laptop_companies=companies, laptops_list=laptops)


#show laptops before signin

@app.route('/getLaptops/<int:company_id>/')
def getLaptops(company_id):
	company=session.query(Company).filter_by(id=company_id).one()
	laptops=session.query(Laptop).filter_by(company_id=company_id).all()
	return render_template('getLaptops.html', laptop_companies=company, laptops_list=laptops)
	


#home page after sigin

@app.route('/home')
def home():
	company = session.query(Company).all()
	return render_template("home.html", laptop_companies=company)



#adding new laptop company


@app.route('/addCompany',methods=['POST','GET'])
def addCompany():
	if request.method == 'POST':
	        newComp = Company(name=request.form['name'],icon=request.form['icon'])
        	session.add(newComp)
        	session.commit()
        	return redirect(url_for('home'))
    	else:
        	return render_template('addCompany.html')


#edit laptop company details

@app.route('/editCompany/<int:company_id>',methods=['POST','GET'])
def editCompany(company_id):
	editComp = session.query(Company).filter_by(id=company_id).one()
	if request.method == 'POST':
        	if request.form['name']:
            		editComp.name = request.form['name']
	    		editComp.icon = request.form['icon']
            		return redirect(url_for('home'))
    	else:
        	return render_template('editCompany.html', company=editComp)



#remove laptop company


@app.route('/deleteCompany/<int:company_id>',methods=['POST','GET'])
def deleteCompany(company_id):
	removeComp=session.query(Company).filter_by(id=company_id).one()
	if request.method=='POST':
	        session.delete(removeComp)
        	session.commit()
        	return redirect(url_for('home'))
    	else:
        	return render_template('deleteCompany.html',company=removeComp)


#user can view laptops of specific company

@app.route('/retriveLaptops/<int:company_id>/')
def retriveLaptops(company_id):
	companies=session.query(Company).filter_by(id=company_id).one()
	laptops=session.query(Laptop).filter_by(company_id=company_id).all()
	return render_template('retriveLaptops.html',laptops_list=laptops,company=companies)


#add new laptop info 


@app.route('/addLaptop/<int:company_id>',methods=['POST','GET'])
def addLaptop(company_id):
	if request.method=='POST' and request.form['name']:
        	newLaptop=Laptop(name=request.form['name'],price=request.form['price'],
                ram=request.form['ram'],rom=request.form['rom'],
                          image=request.form['image'],company_id=company_id)
        	session.add(newLaptop)
        	session.commit()
        	return redirect(url_for('retriveLaptops',company_id=company_id))
    	else:
        	return render_template('addLaptop.html',company_id=company_id)
    	return render_template('addlaptop.html',company_id=company_id)




#edit laptops info


@app.route('/editLaptop/<int:company_id>/<int:laptop_id>',methods=['POST','GET'])
def editLaptop(company_id,laptop_id):
    updateLaptop=session.query(Laptop).filter_by(id=laptop_id).one()
    if request.method=='POST':
        updateLaptop.name=request.form['name']
        updateLaptop.price=request.form['price']
        updateLaptop.ram=request.form['ram']
        updateLaptop.rom=request.form['rom']
        updateLaptop.image=request.form['image']
        session.commit()
        return redirect(url_for('retriveLaptops',company_id=company_id))
    else:
        return render_template('editLaptops.html',company_id=company_id,laptop_id=laptop_id,laptop_details=updateLaptop)


#delete laptops info


@app.route('/deleteLaptop/<int:company_id>/<int:laptop_id>',methods=['POST','GET'])
def deleteLaptop(company_id,laptop_id):
    removeLaptop=session.query(Laptop).filter_by(id=laptop_id).one()
    if request.method=="POST":
        session.delete(removeLaptop)
        session.commit()
        return redirect(url_for('retriveLaptops',company_id=company_id))
    else:
        return render_template('deleteLaptop.html',company_id=company_id,laptop_id=laptop_id,laptop=removeLaptop)



@app.route('/company/<int:id>/JSON')
def CompanyJSON(id):
    companies = session.query(Company).filter_by(id=id).all()
    return jsonify(companies=[i.serialize for i in companies])



@app.route('/laptop/<int:id>/JSON')
def LaptopJSON(id):
    lap = session.query(Laptop).filter_by(company_id=id).all()
    return jsonify(mob=[i.serialize for i in lap])




@app.route('/logout')
def logout():
	access_token = login_session['access_token']
    	print("In gdisconnect access token is %s", access_token)
    	print("User Name is:")
    	print(login_session['username'])

    	if access_token is None:
        	print("Access Token is None")
        	response = make_response(
            	json.dumps('Current user not connected.'), 401)
        	response.headers['Content-Type'] = 'application/json'
        	return response
    	access_token = login_session['access_token']
    	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    	h = httplib2.Http()
    	result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type':
                           'application/x-www-form-urlencoded'})[0]

    	print(result['status'])
    	if result['status'] == '200':
        	del login_session['access_token']
        	del login_session['gplus_id']
        	del login_session['username']
        	del login_session['email']
        	del login_session['picture']
        	response = make_response(json.dumps('Successfully disconnected.'), 200)
        	response.headers['Content-Type'] = 'application/json'
        	flash("Successfully logged out")
        	return redirect(url_for('index'))
    	else:
        	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        	response.headers['Content-Type'] = 'application/json'
        	return response

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host="127.0.0.1", port=8000)



