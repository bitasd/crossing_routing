import itertools
import pandas
from Segments import JuncLeg_


# creating the leg object for multi-node X
class Mixin:

    def legLookUp(self, dual_identify='DIVIDED', LegIntAngle=80):

        for k, v in self.juncs_dict.items():
            jid = v.id
            print("junc id: ", jid)
            jcoord = [v._attributes['lon'][0], v._attributes['lat'][0]]
            links_df = v._attributes['cc_ordered_segs'][0]
            # print(links_df)
            # roads with no "divided" tag -- each one leg
            not_divid_df = links_df[links_df['dual'] != dual_identify]

            legs = [[seg_id] for seg_id in not_divid_df['incid_seg_id_'].tolist()]

            # roads with tag "divided"
            divid_df = links_df[links_df['dual'] == dual_identify]

            for bid in range(len(divid_df)):
                pair_lst = [divid_df['incid_seg_id_'].tolist()[bid]]

                for bjd in range(len(divid_df)):

                    if bjd != bid and \
                            (
                                abs(divid_df['bearing_r'].tolist()[bid] - divid_df['bearing_r'].tolist()[bjd]) < LegIntAngle or
                                abs(divid_df['bearing_r'].tolist()[bid] - divid_df['bearing_r'].tolist()[bjd]) > (360 - LegIntAngle)
                            ) and \
                            divid_df['name'].tolist()[bid] == divid_df['name'].tolist()[bjd]:
                        pair_lst.append(divid_df['incid_seg_id_'].tolist()[bjd])

                        break

                pair_lst.sort()
                legs.append(pair_lst)
                # print("leg pair_lts", pair_lst)
                # print("leg legs", legs)

            # removing duplicate pairs
            legs.sort()
            # print("legs after sort", legs)

            pairs_gpd = list(k for k, _ in itertools.groupby(legs))
            # print("pairs_gpd", pairs_gpd)
            # Avg bearing
            bearing_avgs = []
            for leg_pair in pairs_gpd:
                links_ = [links_df[links_df['incid_seg_id_'] == lid]['bearing_r'].item() for lid in leg_pair]
                bearing_avg = sum(links_) / len(links_)
                bearing_avgs.append(bearing_avg)
            legs_df = pandas.DataFrame(
                list(zip(pairs_gpd, bearing_avgs)),
                columns=['links', 'avg_bearing']
            )
            legs_df['cc_rank'] = legs_df['avg_bearing'].rank(ascending=False, method='first').astype(int)
            _l = JuncLeg_(id=jid, _jnodes=v._nodes, _jcoord=jcoord,
                          cc_junclegs_df=legs_df)

            self.legs_dict.update({
                jid: _l
            })
