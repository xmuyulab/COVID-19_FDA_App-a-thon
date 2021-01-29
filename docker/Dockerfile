FROM jupyter/base-notebook:python-3.8.6

RUN conda install numpy pandas plotly scipy dash 
ADD . /opt
ENTRYPOINT python /opt/tcrmap.py -i /opt/sample_full.tsv -p 8050
