import yaml,sys,copy,json,pickle,time,traceback
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator
sys.path.insert(0,'/mnt/data/diode_transport_project/src')
from fdm_3d.grid import create_uniform_grid
from fdm_3d.poisson_solver import Plate3DSolver
from fdm_3d.field_solver import extract_surface_metrics
base=yaml.safe_load(Path('/mnt/data/diode_transport_project/configs/plate_3d_convergence.yaml').read_text())
conv=base.get('convergence',{})

def apply(dst,src):
    for k,v in src.items():
        if isinstance(v,dict) and isinstance(dst.get(k),dict): apply(dst[k],v)
        else: dst[k]=v

def mk(n):
    c=copy.deepcopy(base); c['grid']['nx']=c['grid']['ny']=c['grid']['nz']=n
    apply(c['search'], conv.get('search_overrides', {})); apply(c['solver'], conv.get('solver_overrides', {})); return c

def interp(srcg, arr, dstg):
    rgi=RegularGridInterpolator((srcg.x,srcg.y,srcg.z), arr, bounds_error=False, fill_value=None)
    X,Y,Z=np.meshgrid(dstg.x,dstg.y,dstg.z, indexing='ij')
    pts=np.column_stack([X.ravel(),Y.ravel(),Z.ravel()])
    return rgi(pts).reshape(dstg.shape)

def solve(cfg,j,initial_phi=None,initial_rho=None):
    grid,bc=create_uniform_grid(cfg); solver=Plate3DSolver(cfg,grid,bc)
    outer_max=int(solver.solver_cfg.get('outer_max_iter',5)); outer_tol=float(solver.solver_cfg.get('outer_tol',5e-5))
    phi=solver.initialize_potential() if initial_phi is None else np.array(initial_phi,copy=True)
    rho=np.zeros_like(phi) if initial_rho is None else np.array(initial_rho,copy=True)
    solver._apply_side_boundaries(phi)
    conv=False
    for outer in range(1,outer_max+1):
        old=phi.copy(); rho=solver.compute_space_charge_density(phi,j)
        phi,it,inner,max_delta,h=solver.solve_fixed_rho(phi,rho)
        if np.max(np.abs(phi-old))<outer_tol and inner:
            conv=True; break
    m=extract_surface_metrics(phi,grid)
    return {'grid':grid,'phi':phi,'rho':rho,'metrics':m,'conv':conv,'j':j}

def secant_from_states(cfg, left, right, steps=6):
    a,b=left['j'],right['j']; fa,fb=left['metrics'].center_gradient,right['metrics'].center_gradient
    if fa*fb>0: raise RuntimeError(f'no sign {fa},{fb}')
    best=left if abs(fa)<=abs(fb) else right
    seed_phi,seed_rho=right['phi'],right['rho']
    for _ in range(steps):
        x=b - fb*(b-a)/(fb-fa) if abs(fb-fa)>1e-12 else 0.5*(a+b)
        if not (a < x < b): x=0.5*(a+b)
        M=solve(cfg,x,seed_phi,seed_rho)
        fx=M['metrics'].center_gradient
        print('eval',cfg['grid']['nx'],x,fx,M['conv'], flush=True)
        seed_phi,seed_rho=M['phi'],M['rho']
        if abs(fx)<abs(best['metrics'].center_gradient): best=M
        if fa*fx<0: b,fb=x,fx; right=M
        else: a,fa=x,fx; left=M
        print(' bracket',a,b, flush=True)
    return best,(a,b),left,right
try:
    left=pickle.loads(Path('/mnt/data/diode_transport_project/results/plate_3d/tmp37_274000.pkl').read_bytes())
    right=pickle.loads(Path('/mnt/data/diode_transport_project/results/plate_3d/tmp37_276000.pkl').read_bytes())
    cfg37=mk(37)
    best37, br37, left37, right37 = secant_from_states(cfg37,left,right,6)
    print('best37',best37['j'],best37['metrics'].center_gradient, flush=True)
    cfg55=mk(55); g55,_=create_uniform_grid(cfg55)
    warm55_phi=interp(best37['grid'],best37['phi'],g55)
    warm55_rho=interp(best37['grid'],best37['rho'],g55)
    prev=None; seed_phi,seed_rho=warm55_phi,warm55_rho; probes=[]; bracket55=None
    for j in [276000.0,278000.0,280000.0,282000.0,284000.0,286000.0,288000.0]:
        M=solve(cfg55,j,seed_phi,seed_rho)
        probes.append({'j':j,'grad':M['metrics'].center_gradient,'conv':M['conv']})
        print('probe55',j,M['metrics'].center_gradient,M['conv'], flush=True)
        seed_phi,seed_rho=M['phi'],M['rho']
        if prev is not None and prev['metrics'].center_gradient * M['metrics'].center_gradient < 0:
            bracket55=(prev,M)
            break
        prev=M
    if bracket55 is None: raise RuntimeError('no 55 bracket')
    best55, br55, left55, right55 = secant_from_states(cfg55, bracket55[0], bracket55[1], 6)
    out={'root37_j':best37['j'],'root37_grad':best37['metrics'].center_gradient,'root37_bracket':br37,'probes55':probes,'root55_j':best55['j'],'root55_grad':best55['metrics'].center_gradient,'root55_bracket':br55,'root55_conv':best55['conv']}
    Path('/mnt/data/diode_transport_project/results/plate_3d/55_only_targeted_result.json').write_text(json.dumps(out,indent=2), encoding='utf-8')
    print('FINAL', json.dumps(out, indent=2), flush=True)
except Exception:
    traceback.print_exc(); raise
