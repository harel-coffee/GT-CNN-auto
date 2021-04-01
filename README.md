# GT-CNN: Glycosyltransferase fold prediction using deep learning

## Requirement

Please ensure the following software is installed:

- `Python (v3.7.4 or later)` [link](https://www.python.org/downloads/)
- `Pytorch (v1.8.1 or later recommend using GPU version)` [link](https://pytorch.org/)
- `fastai` [link](https://fastai1.fast.ai/install.html)
- `pandas` [link](https://pandas.pydata.org/pandas-docs/stable/getting_started/install.html)
- `seaborn` [link](https://seaborn.pydata.org/installing.html)
- `torchviz` [link](https://pypi.org/project/torchviz/)
- `sklearn` [link](https://scikit-learn.org/stable/install.html)
- `scipy` [link](https://www.scipy.org/install.html)
- `numpy` [link](https://numpy.org/install/)
- `matplotlib` [link](https://matplotlib.org/stable/users/installing.html)
- `umap` [link](https://umap-learn.readthedocs.io/en/latest/)
- `jupyterlab` [link](https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html)
- `opencv2`[link](https://pypi.org/project/opencv-python/)
- `tensorboardX`[link](https://pypi.org/project/tensorboardX/)
- [`imblearn`](https://pypi.org/project/imblearn/)

## Dataset and Pretrained Models

All used dataset is avaliable through this link:[dataset](https://www.dropbox.com/sh/u10eufybjhycuph/AAAEtmqI_fUFVSNyysTMDHxUa?dl=0), please download and put it under main folder with name ./Datasets

All pretrained model is avaliable through this link: [models](https://www.dropbox.com/sh/gn60mm7dy4ywrcr/AADLnvFDiMDuObYOOHiyHwA1a?dl=0), please download and put it under main folder with name ./PretrainedModels

## Complete Pipeline:

### Step1: Sequence collection

Collect related sequences for any family, group you want to analyze. Ideally, you want >100 and <500 sequences purged with a sequnece identity of 10-95%.
Edit sequence IDs in format (>Family(GT2-A)|UniqueID|TaxInfo)

### Step2: Secondary structure prediction
- Done using NetsurfP2.0[link](http://www.cbs.dtu.dk/services/NetSurfP/). Generates a csv file with the predictions for all sequences. 
- Note: any other SOTA SS predictor also works as long as the output csv file is formated with such columns: ["Name", "fold", "family", "q3seq", "rawseq"]


### Step3: Preprocessing
- Notebook: [1-Preprocessing.ipynb](./Codes/1-Preprocessing.ipynb) 
- This notebook is mainly for: 
1. Domain and sequence lenghth based filtering, in our work, based on statistical analyasis, we select 798 as our cuttung threhold and padding length 
2. Sequence paddings, this is mainly for CNN model to process.


### Step4: CNN-Attention model training
- Notebook: [2-CNNAttention.ipynb](./Codes/2-CNNAttention.ipynb) 
- This notebook is for training the cnn attention model using outputs generated from preprocessing steps.
- The pretrained model is made available and dataset is avaliable upon request.

### Step5: Autoencoder models training
- Notebook: [3-CNNAutoencoder-all.ipynb](./Codes/3-CNNAutoencoder-all.ipynb) and [4-CNNAutoencoder-sub.ipynb](./Codes/4-CNNAutoencoder-sub.ipynb) 
- This notebook is for training the autoencoder model using locked features generated from the CNN model.
- The pretrained models are made available and dataset is avaliable upon request.

### Step6: Generate all GT level Reconstruction Error
- Notebook: [5-RE_FAS_calculations.ipynb](./Codes/5-RE_FAS_calculations.ipynb) 
- Pretrained: ./PretrainedModels/Autoencoder_gtAll.pickle
- Better with GPU. 

### Step7: Generate GT cluster level Fold Assignment Score
- Notebook: [5-RE_FAS_calculations.ipynb](./Codes/5-RE_FAS_calculations.ipynb) 
- Pretrained: ./PretrainedModels/Autoencoder_gt--.pickle
- Better with GPU.

### Step8: Analysis and fold prediction using the above results
- Notebook: [5-RE_FAS_calculations.ipynb](./Codes/5-RE_FAS_calculations.ipynb) 
- Plotting of results.
- Generate RE and FAS values for new families.

## For fold prediction of a new family of sequences:

Required steps are Step 1-3 and 6-8.

The pretrained models from Step 4 and 5 are made available.

All the required files to run the notebooks for these required steps are provided in the directories [PretrainedModels](./PretrainedModels) and [Datasets](./Datasets) 

All the required notebooks outlining the steps are provided in the [Codes](./Codes) directory.

Outputs for each step are written to the ExampleOutputs directory and can be changed within the jupyter notebooks.

## For questions, comments and requests, please contact the ESBG lab at UGA.

Natarajan Kannan: nkannan@uga.edu

Zhongliang Zhou: Zhongliang.Zhou@uga.edu

Rahil Taujale: rtaujale@uga.edu

## Updates

- v1.0.0
  - First packaged version with complete notebooks and datasets.

## Citation

If you find this tool helpful, please cite:

Rahil Taujale, Zhongliang Zhou, Wayland Yeung, Kelley W Moremen, Sheng Li and Natarajan Kannan.**Mapping the glycosyltransferase fold landscape using deep learning.** Preprint.

