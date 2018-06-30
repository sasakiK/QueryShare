FROM python:3.6

RUN groupadd -r uwsgi && useradd -r -g uwsgi uwsgi

RUN pip install pulp \
                uWSGI \
                dash==0.21.1 \
                dash-renderer==0.12.1 \
                dash-html-components==0.10.1 \
                dash-core-components==0.13.0-rc5 \
                loremipsum \
                #dash-core-components==0.22.1  \
                dash_table_experiments \
                pandas \
                dash-auth \
                flask_caching \
                redis

WORKDIR /app
COPY app /app
COPY cmd.sh /

USER uwsgi

EXPOSE 5000

CMD ["/cmd.sh"]
