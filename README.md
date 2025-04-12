Approach1 :\
Steps for installation and running:\
Create a virtual environment in local system.\
Install Python 3.9.13 and other necessary libraries.\
download this code from github to local.\
open the the vocieapp project code in vscode or any similar editor.\
activate the virtual environment.\
run the following command in termainal : streamlit run app.py\
![image](https://github.com/Pythonography/voiceapp/assets/158061776/1e0fad33-6da3-47fb-aa10-85eb33a62a49) \

\
Approach2: \
Download the zip file to local \
In vscode ( or any IDE) terminal, run this cmd: docker build -t <imagename> \
Once docker is built, run this cmd : docker run -d -p 8501:8501 --name <container name> <imagename> \
Go to browser and type localhost:8501 \
App will now open in the browser.
