"""Evaluacion contra registros anotados de PhysioNet.

Este modulo NO se ejecuta en el notebook: requiere descargar datos.
Correlo en tu maquina para obtener numeros contra anotaciones de cardiologo,
que valen mucho mas que cualquier resultado sobre senal sintetica.

    pip install wfdb
    python mitbih.py
"""
import numpy as np

def evaluar_registro(nombre='100', pn_dir='mitdb', canal=0, tol=0.15):
    import wfdb
    from detector import detectar, evaluar

    reg = wfdb.rdrecord(nombre, pn_dir=pn_dir)
    ann = wfdb.rdann(nombre, 'atr', pn_dir=pn_dir)
    x, fs = reg.p_signal[:, canal], reg.fs

    # Anotaciones que corresponden a un latido (excluye ruido, cambios de ritmo)
    LATIDO = set('NLRBAaJSVrFejnE/fQ?')
    verdad = np.array([s/fs for s, sym in zip(ann.sample, ann.symbol)
                       if sym in LATIDO])

    detectados, _ = detectar(x, fs)
    Se, VPP, VP, FN, FP = evaluar(detectados, verdad, tol=tol)
    return dict(registro=nombre, fs=fs, latidos=len(verdad),
                Se=Se, VPP=VPP, VP=VP, FN=FN, FP=FP)


if __name__ == '__main__':
    # Registros representativos: 100 y 101 son limpios; 105 tiene mucho ruido;
    # 108 tiene artefacto de electrodo; 208 y 210 tienen arritmia abundante.
    REGISTROS = ['100', '101', '103', '105', '108', '200', '208', '210', '222', '228']
    print(f'{"registro":>9} {"latidos":>8} | {"Se":>7} | {"VPP":>7} | {"FN":>5} {"FP":>5}')
    print('-' * 55)
    todos = []
    for r in REGISTROS:
        try:
            res = evaluar_registro(r)
            todos.append(res)
            print(f'{res["registro"]:>9} {res["latidos"]:>8} | {res["Se"]:>6.2f}% | '
                  f'{res["VPP"]:>6.2f}% | {res["FN"]:>5} {res["FP"]:>5}')
        except Exception as e:
            print(f'{r:>9} {"—":>8} | error: {e}')
    if todos:
        VP = sum(d['VP'] for d in todos); FN = sum(d['FN'] for d in todos)
        FP = sum(d['FP'] for d in todos)
        print('-' * 55)
        print(f'{"GLOBAL":>9} {VP+FN:>8} | {100*VP/(VP+FN):>6.2f}% | '
              f'{100*VP/(VP+FP):>6.2f}% | {FN:>5} {FP:>5}')
