FROM python

ADD requirements_flower_derived.txt /

RUN pip install -r requirements_flower_derived && \
    rm -rf ~/.cache

ADD flower_endpoint.bsh /

CMD ["/flower_endpoint.bsh"]