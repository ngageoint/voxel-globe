FROM python

RUN pip install flower==0.9.1 && \
    rm -rf ~/.cache

ADD flower_endpoint.bsh /

CMD ["/flower_endpoint.bsh"]