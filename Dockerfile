FROM dynverse/dynwrappy:v0.1.0

ARG GITHUB_PAT

RUN git clone https://github.com/dynverse/pCreode.git && pip install -e pCreode

COPY definition.yml run.py example.sh /code/

ENTRYPOINT ["/code/run.py"]
