source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv -p python3 annotator_supreme --system-site-packages 
workon annotator_supreme
pip install -r requirements.txt
echo "Setup of annotator_supreme python env is complete."
