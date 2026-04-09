import yaml,sys,time,copy,json,pickle
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

def dump(name,obj):
    Path(f'/mnt/data/diode_transport_project/results/plate_3d/{name}.pkl').write_bytes(pickle.dumps(obj))

cfg25=mk(25)
# reproduce probe path
first=solve(cfg25,279473.7143366262)
second=solve(cfg25,279468.0,first['phi'],first['rho'])
print('25 second grad',second['metrics'].center_gradient,'conv',second['conv'], flush=True)
dump('tmp25_second',second)

cfg37=mk(37); g37,_=create_uniform_grid(cfg37)
phi37=interp(second['grid'],second['phi'],g37); rho37=interp(second['grid'],second['rho'],g37)
seed_phi,seed_rho=phi37,rho37
for j in [272000.0,274000.0,276000.0]:
    M=solve(cfg37,j,seed_phi,seed_rho)
    print('37',j,'grad',M['metrics'].center_gradient,'conv',M['conv'], flush=True)
    dump(f'tmp37_{int(j)}',M)
    seed_phi,seed_rho=M['phi'],M['rho']
