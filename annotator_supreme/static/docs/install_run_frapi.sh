echo "   _____                       __            __    "
echo "  /     \   ____   ___________|  | _______ _/  |_  "
echo " /  \ /  \_/ __ \_/ __ \_  __ \  |/ /\__  \\   __\ "
echo "/    Y    \  ___/\  ___/|  | \/    <  / __ \|  |   "
echo "\____|__  /\___  >\___  >__|  |__|_ \(____  /__|   "
echo "        \/     \/     \/           \/     \/       "
echo "=== Meerkat Facial Recognition - On-premise version ==="
echo ""
echo "This script will install the docker image of our on-premise"
echo "version. If it is the first time you are running this, please"
echo "take notice that the downloading of the image will take a couple"
echo "of minutes"
echo ""
echo "Any problems or doubts in the installation process, you can contact"
echo "us using support@meerkat.com.br"
echo ""
echo "Before continuing, please make sure that you have installed the"
echo "following requirements:"
echo "- docker"
echo "- basic Unix tools: gzip, tar, wget"
echo ""

install_on_premise() {
	if [ "$(uname)" = "Darwin" ]; then
		echo "First, let's login to the docker hub..."
		docker login -u meerkatcvonpremise -e meerkat.cv.onpremise@gmail.com -p cvrocksindeed!
		echo "Pulling image..."
		docker pull meerkatcvonpremise/frapi_on_premise:latest
		echo "Running container"
		docker run -d -p 9001:9001 -p 80:80 -p 8091:8091 -p 4444:4444 --ulimit nofile=1024 -m=900m meerkatcvonpremise/frapi_on_premise
	elif [ "$(expr substr $(uname -s) 1 5)" = "Linux" -o "$(expr substr $(uname -s) 1 10)" = "MINGW32_NT" ]; then
		echo "First, let's login to the docker hub..."
		sudo docker login -u meerkatcvonpremise -e meerkat.cv.onpremise@gmail.com -p cvrocksindeed!
		echo "Pulling image..."
		sudo docker pull meerkatcvonpremise/frapi_on_premise:latest
		echo "Running container"
		mkdir ~/.meerkat_cb/
	    sudo chmod 777 -R ~/.meerkat_cb/
		sudo docker run -d -v ~/.meerkat_cb/:/opt/couchbase/var -p 9001:9001 -p 80:80 -p 8091:8091 -p 4444:4444 meerkatcvonpremise/frapi_on_premise
	fi

    # now, waits for the server to be up
    statuscode="$(curl -I http://localhost/frapi/ 2>/dev/null | head -n 1 | cut -d ' ' -f2)"

    printf "Waiting for the API to launch."

    ntimeout=300
    secs=1

    while [ "$statuscode" != "200" ] && [ $secs -lt $ntimeout ]; do
        printf "."
        sleep 1
        statuscode="$(curl -I http://localhost/frapi/ 2>/dev/null | head -n 1 | cut -d ' ' -f2)"
        secs=$((secs+1))
    done

    if [ "$statuscode" = "200" ]; then
        echo "Done. Opening http://localhost/frapi/"
        xdg-open "http://localhost/frapi/"
    else
        echo "Something went wrong and a timeout was triggered. Check you docker logs and contact us."
    fi
}

while true; do
    read -p "Would you like to continue with the installation? " yn
    case $yn in
        [Yy]* ) install_on_premise; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done



