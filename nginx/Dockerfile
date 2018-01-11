#FROM ngnix
FROM meerkatcvonpremise/meerkat_base:latest

COPY nginx.conf /usr/local/nginx/conf/nginx.conf

RUN ln -sf /dev/stdout /usr/local/nginx/logs/access.log
RUN ln -sf /dev/stderr /usr/local/nginx/logs/error.log
	
# run the Ngnix server
CMD /usr/local/nginx/sbin/nginx

EXPOSE 80
