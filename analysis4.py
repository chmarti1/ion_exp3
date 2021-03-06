import numpy as np
import matplotlib.pyplot as plt
import lplot
import lconfig
import tc

# Generate float-sat plots


def smooth(x, N=20):
    xx = np.cumsum(x)/N
    xx = xx - np.roll(xx,N)
    xx[:N] = 0.
    xx[-N:] = 0.
    return xx

def median_filter(x, N=100):
    NN = int(N/2)
    xx = np.zeros_like(x)
    for index in range(NN,len(x)-NN):
        xs = list(x[(index-NN):(index+NN)])
        xs.sort()
        xx[index] = xs[NN]
    return xx


def fsanalysis(fileobj):
    # First, copy the meta parameters using the default function
    out = lconfig.default_afun(fileobj)
    # Create calibrated data
    V = fileobj.data[:,0]
    I = fileobj.data[:,1]*25.242500 - .15605
    Vtc1 = smooth(fileobj.data[:,2],200)
    ts = 1./fileobj.config[0].samplehz
    t = fileobj.t()
    out['V'] = V
    out['I'] = I
    out['T'] = tc.K.T(Vtc1*1000., Tcj=20.)
    out['scan'] = V.mean() < 5.
    tsample = []
    Tsample = []
    Isample = []
    Vsample = []
    # Extract a sample from each 10V peak for sawtooth scans
    if out['scan']:
        # Perform a test for a rising-edge trigger
        index = 0
        while index < (len(V)-120):
            # look for the positive 0 crossing in voltage
            if I[index]<0. and I[index+1]>=0.:
                Vsample.append(\
                    V[index] - (V[index+1] - V[index])/(I[index+1] - I[index]) * I[index])
                Is = I[index:index+100].tolist()
                Is.sort(reverse=True)
                tsample.append(t[index+50])
                Isample.append(Is[4]) # Reject the 4 largest points
                Tsample.append(np.mean(out['T'][index:index+100]))
                index+=120
            else:
                index += 1

    out['Tsample'] = Tsample
    out['Isample'] = Isample
    out['tsample'] = tsample
    out['Vsample'] = Vsample
    return out
    

files = [ 'data/b1_1.dat', 'data/b2_3.dat']
tstart = [24., 24.]
tstop = [344., 600.]
styles = ['o','s']
LAB = ['20scfh', '25scfh']

plt.close('all')
lplot.set_defaults(screen_dpi=112)

ax0 = lplot.init_fig('Floating Potential (V)', 'Saturation Current ($\mu$A)',figure_size=(6.,4.5))

for index in range(len(files)):
    
    data = lconfig.dfile(files[index], afun=fsanalysis, afile=None)
    
    t = np.array(data.analysis['tsample'])
    V = np.array(data.analysis['Vsample'])
    I = np.array(data.analysis['Isample'])

    ii = (t>tstart[index]) * (t<tstop[index])
    
    ax0.plot(V[ii], I[ii],styles[index], mec='k', mfc='w', label=LAB[index])
ax0.legend(loc=0)
ax0.get_figure().savefig('float_sat.png')

