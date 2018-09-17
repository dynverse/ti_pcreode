FROM dynverse/dynwrap:py2.7

RUN git clone https://github.com/KenLauLab/pCreode.git && pip install pCreode

LABEL version 0.1.2

ADD . /code

ENTRYPOINT python /code/run.py
