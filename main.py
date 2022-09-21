import geopandas
import GeoAtoms
import numpy
import warnings
warnings.filterwarnings('ignore')

geopandas.options.display_precision = 9

streets = geopandas.read_file(
    # 'C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\intersection\\Nov1\\geobase_dual_4326_sample.gpkg'
# 'C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\x_accessiblity\\data\\dual_4326_sample3.gpkg'
'C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\x_accessiblity\\data\\downtown_ToAll_2_4326.gpkg'  # gives errors
)

# streets = streets.dropna(how='all')
# streets.fillna(0, inplace=True)
# streets.replace(numpy.nan, 0, inplace=True)

print("streets:", len(streets))


from_attributes_wanted = [
    # 'ID_TRC',
    'CLASSE',
    'SENS_CIR', 'DIVIDED',
    'POSITION_R', 'NOM_VOIE'
]

to_attributes_wanted = [
    # 'ID_TRC',
    'CLASSE',
    'SENS_CIR', 'DIVIDED',
    'POSITION_R', 'NOM_VOIE'

]

crossed_over_attributes_wanted = [

    'DIVIDED',
    'SENS_CIR',
    'NOM_VOIE'


]
trc_attributes_wanted = [
    'ID_TRC_int'
]
streets = streets[streets['geometry'].is_valid]

ga = GeoAtoms.Geoatoms()

ga.first_order_import(streets, field_val_spec_dual_cargwy={'DIVIDED': 'DIVIDED'}, field_street_name='NOM_VOIE')

# some kind of set up that could be used to tell the geoatoms  what attributes are
# fetch from to, from, and crossed over segments and saved with the geometry

ga.crossing_movements()
# this is where only the through crossing part is happeingn s
# so one idea is to preemptively count for that and store the information in a list
#                         incident

gdf_junc = ga.junc_layer(my_id='ID_TRC_int')
ga.legLookUp()


# gdf = ga.do_simple_crossing(from_attributes_wanted=from_attributes_wanted,
#                             to_attributes_wanted=to_attributes_wanted,
#                             crossed_over_attributes_wanted=crossed_over_attributes_wanted,
#                             trc_attributes_wanted=trc_attributes_wanted)

#
# gdf.to_file(
#     'crossing_t.gpkg',
#     layer='crossing_101',
#     driver="GPKG"
# )
#
# gdf_junc.to_file(
#     'junc_layer_t.gpkg',
#     layer='junc_layer_1',
#     driver="GPKG"
# )
# gdf_junc.to_csv('juncLayert.csv')

# merging nodes of a multinode junction into the averaged point and creating the geometry
merged_junc_gdf = ga.mergeGeom()
merged_junc_gdf.to_file("C:\\Users\\bitas\\folders\\Research\\Montreal\\codes\\x_accessiblity\\data\\merged_at_X\\merge_1.gpkg", layer="test1", driver="GPKG")