#######################################################################################
## DO NOT EDIT THIS FILE! This file was automatically generated from the dockerfile. ##
## Run dynwrap:::.container_dockerfile_to_singularityrecipe() to update this file.   ##
#######################################################################################

Bootstrap: shub

From: dynverse/dynwrap:py2.7

%labels
    version 0.1.1

%post
    chmod -R a+r /code
    chmod a+x /code
    git clone https://github.com/KenLauLab/pCreode.git && pip install pCreode

%files
    . /code

%runscript
    exec python /code/run.py
