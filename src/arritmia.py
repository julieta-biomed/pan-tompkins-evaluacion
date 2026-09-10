import numpy as np
from scipy import signal as sg
from detector import detectar, evaluar
FS=500

def ecg_extra(dur=180.0, hr=62.0, prop_extra=0.10, fs=FS, semilla=5):
    """ECG con extrasistoles ventriculares: QRS ancho, prematuro y con pausa
    compensadora. Es el caso donde la regla de 360 ms puede equivocarse."""
    rng=np.random.default_rng(semilla)
    n=int(fs*dur); t=np.arange(n)/fs; x=np.zeros(n); tr=0.5; p=[]; tipos=[]
    normal=[(-0.200,0.15,0.025),(-0.035,-0.10,0.008),(0.0,1.10,0.010),
            (0.035,-0.25,0.010),(0.280,0.30,0.045)]
    # extrasistole: sin P, QRS ancho y de polaridad distinta, T opuesta
    extra=[(0.0,-0.95,0.028),(0.045,0.55,0.030),(0.300,-0.35,0.055)]
    rr_med=60/hr
    while tr<dur-0.8:
        es = rng.random()<prop_extra and len(p)>2
        p.append(tr); tipos.append('V' if es else 'N')
        for c,a,s in (extra if es else normal):
            x+=a*np.exp(-0.5*((t-(tr+c))/s)**2)
        if es:
            tr += 1.55*rr_med          # pausa compensadora
        else:
            tr += max(0.35, rng.normal(rr_med,0.045))
            if rng.random()<prop_extra: tr -= 0.28*rr_med   # prematuridad
    return t, x*(1.30/1.10), np.array(p), np.array(tipos)

def ruido(t, fs=FS, semilla=11):
    rng=np.random.default_rng(semilla)
    sos=sg.butter(4,[20,150],'bandpass',fs=fs,output='sos')
    return (0.35*np.sin(2*np.pi*0.28*t)+0.12*np.sin(2*np.pi*60*t)
            +0.03*sg.sosfilt(sos,rng.standard_normal(len(t))))

t,limpio,pv,tipos = ecg_extra()
x = limpio + ruido(t)
nV=int(np.sum(tipos=='V'))
print(f'{len(pv)} latidos, de los cuales {nV} extrasistoles ventriculares\n')
print(f'{"configuración":>26} | {"Se global":>10} | {"Se en extrasístoles":>20} | {"VPP":>7}')
print('-'*72)
for nom,cfg in [('completo',{}),('sin regla de 360 ms',dict(regla_360=False)),
                ('sin search-back',dict(search_back=False))]:
    d,_=detectar(x,FS,**cfg)
    Se,VPP,_,_,_=evaluar(d,pv)
    ok=sum(1 for tv in pv[tipos=='V'] if len(d) and np.min(np.abs(d-tv))<0.15)
    print(f'{nom:>26} | {Se:>9.1f}% | {100*ok/max(nV,1):>19.1f}% | {VPP:>6.1f}%')
