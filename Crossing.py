from shapely.geometry import LineString
import math
import numpy as np
from MovementRelationData import AttributesForCrossingRelation_, MovementRelation_
import pyproj
import geopandas


class Mixin:

    def do_simple_crossing(self,
                           from_attributes_wanted,
                           to_attributes_wanted,
                           crossed_over_attributes_wanted,
                           trc_attributes_wanted=[]
                           ):
        gdf = geopandas.GeoDataFrame()
        gdf['geometry'] = None
        row_indx = 0
        for junc in (self.legs_dict.values()):
            cc_junclegs_df = junc.cc_junclegs_df
            idx = 100
            if len(cc_junclegs_df) >= 3:  # only eg than 3 legs qualify for crossing
                for i_ in range(len(cc_junclegs_df)):
                    for j_ in range(len(cc_junclegs_df)):
                        if j_ != i_:
                            from_df_ = cc_junclegs_df.loc[cc_junclegs_df.index == i_, ]
                            to_df_ = cc_junclegs_df.loc[cc_junclegs_df.index == j_, ]
                            to_cc_ = to_df_['cc_rank'].values[0]
                            to_bear = to_df_['avg_bearing'].values[0]
                            from_cc_ = from_df_['cc_rank'].values[0]
                            from_bear = from_df_['avg_bearing'].values[0]
                            num_leg_bein_crossed_ = ((to_cc_ - from_cc_) % len(cc_junclegs_df)) - 1

                            if num_leg_bein_crossed_ == 1:
                                crossed_cc_ = ((from_cc_ + num_leg_bein_crossed_ - 1) % len(
                                    cc_junclegs_df)) + 1  # if you start ranks from 1
                                crossed_df = cc_junclegs_df.loc[cc_junclegs_df['cc_rank'] == crossed_cc_,]

                                # Creating the crossing geometry
                                via_coords = junc._jcoord
                                rels_geom = LineString([self.point_from_bearing(via_coords, from_bear),
                                                        # via_coords,
                                                        self.point_from_bearing(via_coords, to_bear)])

                                # OFFSET TO THE RIGHT FOR VISUALIZATION
                                # if multi-node junction offset 8m ~ 0.00007
                                if type(junc._jnodes) == list:
                                    rels_geom_right_offset = rels_geom.parallel_offset(0.00007, 'right', join_style=2,
                                                                                       mitre_limit=2)
                                else:  # if single-node junction offset 5m ~ 0.000045
                                    rels_geom_right_offset = rels_geom.parallel_offset(0.000045, 'right', join_style=2,
                                                                                   mitre_limit=2)
                                # get_segment_attributes(self, segm_id, attr_list)
                                from_attrs_wanted = self.get_segment_attributes(from_df_['links'].values[0][0],
                                                                                from_attributes_wanted)
                                to_attrs_wanted = self.get_segment_attributes(to_df_['links'].values[0][0],
                                                                              to_attributes_wanted)
                                crossed_over_attrs_wanted = self.get_segment_attributes(
                                    crossed_df['links'].values[0][0],
                                    crossed_over_attributes_wanted)

                                from_seg_ids = from_df_['links'].item()
                                to_seg_ids = to_df_['links'].item()
                                c_seg_ids = crossed_df['links'].item()
                                # print("from_seg_ids: ", from_seg_ids)

                                cross_atr = AttributesForCrossingRelation_(
                                    junction_id=[junc.id],
                                    from_cc=[from_df_['cc_rank'].item()],
                                    to_cc=[to_df_['cc_rank'].item()],
                                    from_seg_id=[from_seg_ids],
                                    to_seg_id=[to_seg_ids],
                                    cross_cc=[crossed_cc_],
                                    trc_attrs={
                                        'f_f"{ID_TRC}"': [self.get_segment_attributes(i, trc_attributes_wanted) for i in from_seg_ids],
                                        't_ID_TRC': [self.get_segment_attributes(i, trc_attributes_wanted) for i in to_seg_ids],
                                        'c_ID_TRC': [self.get_segment_attributes(i, trc_attributes_wanted) for i in c_seg_ids]}
                                )
                                # print(cross_atr.trc_attrs)

                                crossing_movement = MovementRelation_(id=junc.id, crosing_attr=cross_atr,
                                                                      rels_geom=rels_geom_right_offset)
                                self.crossing_dict.update({idx: crossing_movement})
                                idx += 1

                                gdf.at[row_indx, 'geometry'] = rels_geom_right_offset

                                for __k in cross_atr.__dataclass_fields__:

                                    if (
                                            __k not in ['other_cross_over_attrs', 'trc_attrs'] and len(cross_atr.__dict__[f'{__k}']) > 0
                                    ):
                                        gdf.at[row_indx, f'{__k}'] = str(cross_atr.__dict__[f'{__k}'][0])

                                for _k in cross_atr.other_cross_over_attrs:
                                    gdf.at[row_indx, f'{_k}'] = cross_atr.other_cross_over_attrs[f'{_k}']

                                for _trck in cross_atr.trc_attrs:
                                    gdf.at[row_indx, f'{_trck}'] = f'{cross_atr.trc_attrs[f"{_trck}"]}'

                                for f_ik in range(len(from_attributes_wanted[1:])):
                                    gdf.at[row_indx, f'f_{from_attributes_wanted[f_ik]}'] = f'{from_attrs_wanted[f_ik]}'

                                for t_ik in range(len(to_attributes_wanted)):
                                    gdf.at[row_indx, f't_{to_attributes_wanted[t_ik]}'] = f'{to_attrs_wanted[t_ik]}'

                                for c_ik in range(len(crossed_over_attributes_wanted)):
                                    gdf.at[
                                        row_indx, f'c_{crossed_over_attributes_wanted[c_ik]}'] = f'{crossed_over_attrs_wanted[c_ik]}'

                                row_indx = row_indx + 1

                            else:
                                pass

        gdf.crs = pyproj.CRS.from_epsg(4326).to_wkt()
        return gdf

    @staticmethod
    def point_from_bearing(junc_point, bearing_, radii=0.00005):

        point_x = junc_point[0] + radii * np.sin(math.radians(bearing_))
        point_y = junc_point[1] + radii * np.cos(math.radians(bearing_))

        return [point_x, point_y]
