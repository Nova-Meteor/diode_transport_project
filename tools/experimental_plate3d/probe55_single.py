import yaml,sys,copy,pickle,time,traceback
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
try:
    # reconstruct best37 from cached bracket states
    left=pickle.loads(Path('/mnt/data/diode_transport_project/results/plate_3d/tmp37_274000.pkl').read_bytes())
    right=pickle.loads(Path('/mnt/data/diode_transport_project/results/plate_3d/tmp37_276000.pkl').read_bytes())
    cfg37=mk(37)
    # Manually use best known 37 root point from prior run
    bestj=274085.56615320774
    best37=solve(cfg37,bestj,right['phi'],right['rho'])
    cfg55=mk(55); g55,_=create_uniform_grid(cfg55)
    phi55=interp(best37['grid'], best37['phi'], g55); rho55=interp(best37['grid'], best37['rho'], g55)
    for j in [280000.0, 286000.0]:
        t=time.time(); res=solve(cfg55,j,phi55,rho55); dt=time.time()-t
        print('55',j,'dt',dt,'grad',res['metrics'].center_gradient,'conv',res['conv'], flush=True)
        phi55,rho55=res['phi'],res['rho']
except Exception:
    traceback.print_exc(); raise
