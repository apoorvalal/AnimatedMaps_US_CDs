# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:hydrogen
#     text_representation:
#       extension: .py
#       format_name: hydrogen
#       format_version: '1.3'
#       jupytext_version: 1.9.1
#   kernelspec:
#     display_name: 'Env: Geo'
#     language: python
#     name: gds
# ---

# %%
# system
import glob, pickle, multiprocessing
from joblib import Parallel, delayed
from pathlib import Path

# pyscience imports
import numpy as np
import pandas as pd

# viz
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from plotnine import *
sns.set(style="ticks", context="talk")
font = {'family' : 'IBM Plex Sans',
               'weight' : 'normal',
               'size'   : 10}
plt.rc('font', **font)
plt.rcParams['figure.figsize'] = (10, 10)
matplotlib.style.use(['seaborn-talk', 'seaborn-ticks', 'seaborn-whitegrid'])
%matplotlib inline
%config InlineBackend.figure_format = 'retina'

# geodata packages
import geopandas as gpd
import contextily as cx

# %% [markdown]
# # Data Ingest
#
# downloaded by `0_get` from [this excellent repository](https://cdmaps.polisci.ucla.edu/). State-specific zipfiles can be found [here](https://github.com/JeffreyBLewis/congressional-district-boundaries).

# %% [markdown]
# ## one-time read and pickle of all geometries

# %%
shapes1 = sorted(glob.glob("shp/*.zip"))
shapes1[:5]

# %% [markdown]
# Geopandas can read zipfiles, which saves us the trouble of having to unzip everything. Marginally slower, so extract if you plan to read files repeatedly. I parallelise the reading in process across 4 cores.

# %% tags=[]
%%time
readCong = lambda x: gpd.read_file(f"zip://{x}!districtShapes")['geometry']
cong_files = Parallel(n_jobs=6)(delayed(readCong)(f) for f in shapes1)

# %%
cong_files[0].shape

# %%
pd.Series([f.shape[0] for f in cong_files]).plot()

# %%
%%time
import pickle
with open("tmp/list_of_maps.pkl", "wb") as f:
    pickle.dump(cong_files, f)

# %% [markdown]
# ## read pickled lists

# %%
%%time
cong_files =  pickle.load(open("tmp/list_of_maps.pkl", "rb"))

# %%
xw = pd.read_pickle("tmp/cong_time_xw.pkl")
xw.info()


# %% [markdown]
# ## dry run
# %%
us_outline = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2017//STATE/tl_2017_us_state.zip")
# %%
f, ax = plt.subplots(figsize = (10, 12), dpi = 150)
k = 113
cong_files[k].plot(facecolor = 'None', edgecolor = 'r', ax = ax)
ax.set_ylim(24, 50)
ax.set_xlim(-130, -60)
us_outline.plot(facecolor = 'None', edgecolor = 'k', linewidth = 1.2, ax = ax)
ax.set_axis_off()
ax.set_title(f"Congressional District boundaries: {xw.loc[xw.cong == k]['startdate'].dt.year.values[0]}")
f.tight_layout()

# %% [markdown]
# # Animated map

# %%
from matplotlib import animation
from IPython.display import display
from IPython.display import HTML


# %%
def plot_animation(list_dfs = cong_files):
    f, ax = plt.subplots(figsize = (15, 10), dpi = 120)

    def get_data(i):
        data = list_dfs[i]
        return(data)

    def animate(k):
        ax.clear()
        # extract data
        data = get_data(k)
        # plot CDs
        data.plot(facecolor = 'None', edgecolor = 'r', ax = ax)
        # outline
        us_outline.plot(facecolor = 'None', edgecolor = 'k', linewidth = 1.2, ax = ax)
        ax.set_title(f"US Congressional District boundaries \n {xw.loc[xw.cong == k+1]['startdate'].dt.year.values[0]}")
        # zoom in on mainland
        ax.set_ylim(24, 50)
        ax.set_xlim(-130, -60)
        ax.set_axis_off()

    ani = animation.FuncAnimation(
            f, animate, frames=list(range(0,len(list_dfs))), interval=400,
            repeat=True, blit=False
        )
    f.tight_layout()
    return ani

# %%
ani = plot_animation()

# %% [markdown]
# Write to mp4. Output omitted.

# %%
%%time
HTML(ani.to_html5_video())

# %% [markdown]
# Convert to interactive animation

# %%
import matplotlib
matplotlib.rcParams['animation.embed_limit'] = 2**128

# %%
HTML(ani.to_jshtml())
