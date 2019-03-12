FROM dynverse/dynwrappy:v0.1.0

RUN git clone https://github.com/dynverse/pCreode.git && pip install -e pCreode

COPY definition.yml run.py example.h5 /code/

ENTRYPOINT ["/code/run.py"]
