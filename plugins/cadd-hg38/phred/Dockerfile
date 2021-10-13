FROM ubuntu:20.04
RUN apt-get update && \
    apt-get install -y git wget
RUN git clone https://github.com/kircherlab/CADD-scripts.git && \
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -p miniconda3 -b

ENV PATH=/miniconda3/bin:$PATH

RUN conda config --prepend channels bioconda && \
    conda config --prepend channels conda-forge && \
    conda install -c conda-forge -y mamba && \
    mamba install -c conda-forge -c bioconda -y snakemake

RUN mkdir -p /CADD-scripts/data/prescored/GRCh37_v1.6/no_anno/ && \
    cd  /CADD-scripts && \
    snakemake test/input.tsv.gz --use-conda --conda-create-envs-only --conda-prefix envs --configfile config/config_GRCh38_v1.6.yml --snakefile Snakefile -j1

COPY ./wrapper.sh /wrapper.sh
RUN chmod +x /wrapper.sh
