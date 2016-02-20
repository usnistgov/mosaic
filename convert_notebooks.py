import mosaic
import glob

mosaicpath=mosaic.__path__[0]

nb_dir=['plots', 'analysis']

nb=[]
for d in nb_dir:
	nb.extend(glob.glob(mosaicpath+'/../_mosaic-examples/'+d+'/*.ipynb'))

c = get_config()
c.NbConvertApp.notebooks = nb
