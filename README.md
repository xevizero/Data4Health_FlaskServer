# Data4Health - FlaskServer
This repository contains the Pycharm project of our Server for Data4Health. The server acts as a back-end for our Android Client, 
as a handler for the Data4Help API service requests and also contains a little front-end website for developers.
The project is developed in Flask, a very cool framework for Python.
## Getting Started
You can start by installing Python from here: https://www.python.org/downloads/

The next step would be importing the project in the PyCharm IDE. You need PyCharm Professional that contains native support for Flask, 
which is not found in the free Community Edition. Create a JetBrains account here: https://www.jetbrains.com/ and by using your 
email from Politecnico request access to professional only software. Then download PyCharm Professional from your account page.

After you have installed and configured your IDE and you have imported our project, make sure you have set a Python interpreter in 
your IDE settings; if you have Python installed in the default directory, PyCharm should recognize it automatically.

Before being able to launch the server, you'll need to edit your IDE settings and to install some Flask plugins.

Start in PyCharm by going into "Run > Edit Configurations..." and create a new Flask Server type configuration with the following options:
```
Target type: Script path
Target: <<yourPathToTheProject>>\Data4Health_FlaskServer\Server\app.py
Environment variables: (add a new one) FLASK_APP=app.py
Python Interpreter: Make sure it is set
```
Now open the "Terminal" tab in PyCharm and type the following commands to install Flask and its components:
```
pip install flask
pip install flask-sqlalchemy
pip install flask-login
pip install flask-wtf
```
You are now ready to launch the Flask server in "Run > Run 'Flask...'".
## Testing with Android
By default, PyCharm will launch the server on Localhost. If you are testing with a real Android Device you'll need to allow the server
to be reachable on your local network. Find out the local IPv4 address of your computer and go back into "Run > Edit Configurations..." and
add the following option:
```
Additional options: --host=<<your IP, without quotes>>
```
You'll now be able to reach your server by simply changing the Endpoint on Android as detailed by the Readme file on the Android Client 
repository.
## Using the Server
You are now ready to use and test the Server project. By opening the default page, you'll land on a Login page which represents the 
little website that acts as a front-end for developers and gives access to the Data4Help API. If you are signed in as a developer you 
can access the API by making GET requests to: "yourIPv4:5000//data4help/api", for example:
```
curl 'http://127.0.0.1:5000/data4help/api?Sex=Male&Argument=dailySteps'
```
You can also simply open a browser and make requests on our form page or directly in the URL bar.
This is just a prototype so the commands support is quite limited.
You can specify these parameters:
```
Sex - AgeFrom - AgeTo - WeightFrom - WeightTo - Argument
```
"Argument" represents what you want to retrieve and can be:
```
BloodPressure - HeartRate - dailySteps
```
To actually see any data you'll need to populate a test database. We used SQLite which makes this a fairly easy task, just open the app.db
file in any SQLite editor, there are even online editors you can use. You can also use the command line or our Android Client if you have
a wearable device to generate biometric data with.
# Final Notes
For any question feel free to contact us and we'll provide the necessary sypport if you have zero experience with the Python language
or PyCharm.
# Authors
Jacopo Frasson

Giacomo Lancellotti

Matteo Lodi
