FROM python

RUN pip install flower && \
    rm -rvf ~/.cache

ADD flower_endpoint.bsh /

CMD ["/flower_endpoint.bsh"]