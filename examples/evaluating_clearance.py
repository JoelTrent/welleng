import pandas as pd
import trimesh

import welleng as we
# from welleng.io import import_iscwsa_collision_data
from welleng.survey import Survey
import welleng.clearance
from welleng.mesh import transform_trimesh_scene
# from welleng.import_data import import_iscwsa_collision_data

# from import_data import import_iscwsa_collision_data
# from well_data import Survey, interpolate_survey
# from clearance import Clearance

# Import some well trajectory data. Here we'll use the ISCWSA trajectories, extracting
# the data from the Excel file downloaded from their website.
filename = filename=f"reference/standard-set-of-wellpaths-for-evaluating-clearance-scenarios-r4-17-may-2017.xlsm"
data = we.io.import_iscwsa_collision_data(filename)

# Make a dictionary of surveys
surveys = {}
for well in data["wells"]:
    s = Survey(
        md=data["wells"][well]["MD"],
        inc=data["wells"][well]["IncDeg"],
        azi=data["wells"][well]["AziDeg"],
        n=data["wells"][well]["N"],
        e=data["wells"][well]["E"],
        tvd=data["wells"][well]["TVD"],
        sigmaH=data["wells"][well]["sigmaH"],
        sigmaL=data["wells"][well]["sigmaL"],
        sigmaA=data["wells"][well]["sigmaA"],
        start_xyz=[
            data["wells"][well]["E"][0],
            data["wells"][well]["N"][0],
            data["wells"][well]["TVD"][0]
            ],
        start_nev=[
            data["wells"][well]["N"][0],
            data["wells"][well]["E"][0],
            data["wells"][well]["TVD"][0]
            ],
        deg=True,
        unit="meters"
    )
    surveys[well] = s

# Add clearance data to dictionary
results = {}
reference = surveys["Reference well"]
for well in surveys:
    if well == "Reference well":
        continue
    else:
        offset = surveys[well]
        if well == "10 - well":
            c = we.clearance.Clearance(reference, offset, kop_depth=900)
            result = we.clearance.ISCWSA(c)
        else:
            c = we.clearance.Clearance(reference, offset)
            result = we.clearance.ISCWSA(c)
            # scene.add_geometry(c.m_off.mesh, node_name=well, geom_name=well, parent_node_name=None)
        results[well] = result

# scene = trimesh.scene.scene.Scene()
# transform_trimesh_scene(scene, origin=([0,0,0]), scale=100, redux=1).export("blender/scene_transform.glb")

# export the data to Excel
with pd.ExcelWriter(f'data/output/output.xlsx') as writer:
    for well in results.keys():
        if well == "Reference well": continue
        r = results[well]
        data = {
            "REF_MD (m)": r.c.ref.md,
            "REF_TVD (m)": r.c.ref.tvd,
            "REF_N (m)": r.c.ref.n,
            "REF_E (m)": r.c.ref.e,
            "Offset_MD (m)": r.off.md,
            "Offset_TVD (m)": r.off.tvd,
            "Offset_N (m)": r.off.n,
            "Offset_E (m)": r.off.e,
            "Hoz_Bearing (deg)": r.hoz_bearing_deg,
            "C-C Clr Dist (m)": r.dist_CC_Clr,
            "Ref_PCR (m 1sigma)": r.ref_PCR,
            "Offset_PCR (m 1 sigma)": r.off_PCR,
            "Calc hole": r.calc_hole,
            "ISCWSA ACR": r.ISCWSA_ACR
        }
        df = pd.DataFrame(data=data)
        df.to_excel(writer, sheet_name=f'{well} - output')