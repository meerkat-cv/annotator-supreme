# Dockerfile for the supreme anotator
FROM meerkatcvonpremise/meerkat_base:latest

# install necessary packages
# RUN apt-get -y install libatlas-base-dev gfortran

# add code to the container
ADD requirements.txt /code/

# upgrade pip to avoid endless compilations 
RUN pip3 install pip --upgrade
RUN pip3 install -r /code/requirements.txt

#WORKDIR /code
#ENV LD_LIBRARY_PATH "/code/carpediem/third_party/yolo_py/linux/:/usr/lib/:/usr/local/lib"
#ENV SERVER_ENV ON_PREMISE

ARG SOURCE_COMMIT
ENV SOURCE_COMMIT $SOURCE_COMMIT
ADD server /code/server
ADD annotator_supreme/ /code/annotator_supreme
ADD run_api.py /code/

WORKDIR /code
# copy the nginx configuration to the correct location
RUN cp server/nginx.conf /usr/local/nginx/conf/nginx.conf

RUN ln -sf /dev/stdout /usr/local/nginx/logs/access.log
RUN ln -sf /dev/stderr /usr/local/nginx/logs/error.log
	
# run the Ngnix server
CMD supervisord -c server/supervisord.conf
