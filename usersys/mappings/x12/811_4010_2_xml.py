# X12 811 4010 to XML mapping script
from .recordsX12_to_xml import * 


def getTransactionTypeCodeComment(code):
    return {
        'CD': 'Consolidated Debit Invoice',
        'CE': 'Consolidated Credit Invoice',
        #    CF
        #    Consolidated Debit Memo
        #    CG
        #    Consolidated Credit Memo
        'CI': 'Consolidated Invoice',
        #    CM
        #    Call Detail Memo
        #    CN
        #    Credit Invoice
        #    CR
        #    Credit Memo
        'DI': 'Debit Invoice',
        #    DR
        #    Debit Memo
        #    FB
        #    Final Bill
        #    FD
        #    Consolidated Invoice, Final Bill
        #    FE
        #    Memorandum, Final Bill
        #    ME
        #    Memorandum
        #    RG
        #    Revised Final Bill
    }.get(code, None)


def getTermsTypeCodeComment(code):
    return {
        '03': 'Fixed Date',
        '10': 'Instant',
        '18': 'Fixed Date, Late Payment Penalty Applies',
    }.get(code, None)


def getHierarchicalLevelCodeComment(code):
    return {
        '1': 'Service/Billing Provider',
        '2': 'Billing Arrangement',
        '3': 'Sub-Billing Arrangement',
        '4': 'Group',
        '5': 'Category',
        '6': 'Sub-Category',
        '7': 'Type',
        '8': 'Charge Detail',
        '9': 'Line Detail',
    }.get(code, None)


def getHierarchicalChildCodeComment(code):
    return {
        '0': 'No Subordinate HL Segment in This Hierarchical Structure.',
        '1': 'Additional Subordinate HL Data Segment in This Hierarchical Structure.',
    }.get(code, None)


def core_out(iter):
    while next(iter, None) is not None: pass

def main(inn, out):
    # 811 pick up some values from ISA envelope
    out.put({'BOTSID': 'envelope', 'sender': inn.ta_info['frompartner']})
    out.put({'BOTSID': 'envelope', 'receiver': inn.ta_info['topartner']})
    out.put({'BOTSID': 'envelope', 'testindicator': inn.ta_info['testindicator']})

    mesg_out = out.putloop({'BOTSID': 'envelope'}, {'BOTSID': 'message'})

    # ST - transaction_set_header
    identifier_code = inn.get({'BOTSID': 'ST', 'ST01': None})  # should be here 811
    control_number = inn.get({'BOTSID': 'ST', 'ST02': None})
    mesg_out.put({'BOTSID': 'message'}, {'BOTSID': 'transaction_set_header', 'identifier_code': identifier_code})
    mesg_out.put({'BOTSID': 'message'}, {'BOTSID': 'transaction_set_header', 'control_number': control_number})

    for st in inn.getloop({'BOTSID': 'ST'}):
        #st.displayqueries()
        print(st.get({'BOTSID': 'ST'},{'BOTSID': 'BIG', 'BIG01': None}))
        # BIG - Beginning Segment for Invoice
        mesg_out.put({'BOTSID': 'message'}, {'BOTSID': 'begseg_for_invoice', 'invoice_issue_date': inn.get({'BOTSID': 'ST'},
                                                                                                           {'BOTSID': 'BIG',
                                                                                                            'BIG01': None})})
        mesg_out.put({'BOTSID': 'message'}, {'BOTSID': 'begseg_for_invoice',
                                             'invoice_number': inn.get({'BOTSID': 'ST'}, {'BOTSID': 'BIG', 'BIG02': None})})
        transaction_type_code = inn.get({'BOTSID': 'ST'}, {'BOTSID': 'BIG', 'BIG07': None})
        mesg_out.put({'BOTSID': 'message'},
                     {'BOTSID': 'begseg_for_invoice', 'transaction_type_code': transaction_type_code})
        mesg_out.put({'BOTSID': 'message'}, {'BOTSID': 'begseg_for_invoice',
                                             'transaction_type_code__comment': getTransactionTypeCodeComment(
                                                 transaction_type_code)})
        # REF
        core_out(seg_ref(st, mesg_out, 'message'))
        # ITD
        for itd in inn.getloop({'BOTSID': 'ST'}, {'BOTSID': 'ITD'}):
            tos_out = mesg_out.putloop({'BOTSID': 'message'}, {'BOTSID': 'terms_of_sale'})
            terms_type_code = itd.get({'BOTSID': 'ITD', 'ITD01': None})
            tos_out.put({'BOTSID': 'terms_of_sale', 'terms_type_code': terms_type_code})
            tos_out.put({'BOTSID': 'terms_of_sale', 'terms_type_code__comment': getTermsTypeCodeComment(terms_type_code)})
            tos_out.put({'BOTSID': 'terms_of_sale', 'terms_net_due_date': itd.get({'BOTSID': 'ITD', 'ITD06': None})})
        # DTM
        core_out(seg_dtm(inn.getloop({'BOTSID': 'ST'}, {'BOTSID': 'DTM'}), mesg_out, {'BOTSID': 'message'}))

        # N1
        for n1, n1_out, n1_tag_name in seg_n1(inn.getloop({'BOTSID': 'ST'}, {'BOTSID': 'N1'}), mesg_out,
                                                   {'BOTSID': 'message'}):
            # N3
            core_out(seg_n3(n1.getloop({'BOTSID': 'N1'}, {'BOTSID': 'N3'}), n1_out, {'BOTSID': n1_tag_name}))
            # N4
            core_out(seg_n4(n1.getloop({'BOTSID': 'N1'}, {'BOTSID': 'N4'}), n1_out, {'BOTSID': n1_tag_name}))
        # HL
        for hl in inn.getloop({'BOTSID': 'ST'}, {'BOTSID': 'HL'}):
            hl_out = mesg_out.putloop({'BOTSID': 'message'}, {'BOTSID': 'hierarchical_level'})
            hl_out.put({'BOTSID': 'hierarchical_level', 'id_number': hl.get({'BOTSID': 'HL', 'HL01': None})})
            hl_out.put({'BOTSID': 'hierarchical_level', 'parent_id_number': hl.get({'BOTSID': 'HL', 'HL02': None})})
            level_code = hl.get({'BOTSID': 'HL', 'HL03': None})
            hl_out.put({'BOTSID': 'hierarchical_level', 'level_code': level_code})
            hl_out.put({'BOTSID': 'hierarchical_level', 'level_code__comment': getHierarchicalLevelCodeComment(level_code)})
            child_code = hl.get({'BOTSID': 'HL', 'HL04': None})
            hl_out.put({'BOTSID': 'hierarchical_level', 'child_code': child_code})
            hl_out.put({'BOTSID': 'hierarchical_level', 'child_code__comment': getHierarchicalChildCodeComment(child_code)})
            # LX
            for lx in hl.getloop({'BOTSID': 'HL'}, {'BOTSID': 'LX'}):
                lx_out = hl_out.putloop({'BOTSID': 'hierarchical_level'}, {'BOTSID': 'assigned_number'})
                lx_out.put({'BOTSID': 'assigned_number', 'number': lx.get({'BOTSID': 'LX', 'LX01': None})})
                # SI
                core_out(seg_si(lx, lx_out, 'assigned_number'))
            # PID
                core_out(seg_pid(lx, lx_out, 'assigned_number'))
                # REF
                # old core_out(seg_ref(lx.getloop({'BOTSID': 'LX'}, {'BOTSID': 'REF'}), lx_out,
                #                          {'BOTSID': 'assigned_number'}))
                core_out(seg_ref(lx, lx_out, 'assigned_number'))
                # AMT
                core_out(seg_amt(lx.getloop({'BOTSID': 'LX'}, {'BOTSID': 'AMT'}), lx_out,
                                          {'BOTSID': 'assigned_number'}))
                # DTM
                core_out(seg_dtm(lx.getloop({'BOTSID': 'LX'}, {'BOTSID': 'DTM'}), lx_out,
                                          {'BOTSID': 'assigned_number'}))
                # TXI
                core_out(seg_txi(lx.getloop({'BOTSID': 'LX'}, {'BOTSID': 'TXI'}), lx_out,
                                          {'BOTSID': 'assigned_number'}))

            # NM1
            for nm1, nm1_out, nm1_tag_name in seg_nm1(hl.getloop({'BOTSID': 'HL'}, {'BOTSID': 'NM1'}), hl_out,
                                                          {'BOTSID': 'hierarchical_level'}):
                # N2
                core_out(seg_n2(nm1.getloop({'BOTSID': 'NM1'}, {'BOTSID': 'N2'}), nm1_out,
                                         {'BOTSID': 'entity_name'}))
                # N3
                core_out(seg_n3(nm1.getloop({'BOTSID': 'NM1'}, {'BOTSID': 'N3'}), nm1_out,
                                         {'BOTSID': 'entity_name'}))
                # N4
                core_out(seg_n4(nm1.getloop({'BOTSID': 'NM1'}, {'BOTSID': 'N4'}), nm1_out,
                                         {'BOTSID': 'entity_name'}))

            # IT1
            for it1, it1_out, it1_tag_name in seg_it1(hl.getloop({'BOTSID': 'HL'}, {'BOTSID': 'IT1'}),
                                                                        hl_out, {'BOTSID': 'hierarchical_level'}):
                # DTM
                core_out(seg_dtm(it1.getloop({'BOTSID': 'IT1'}, {'BOTSID': 'DTM'}), it1_out,
                                          {'BOTSID': it1_tag_name}))

            # SLN
            for sln, sln_out, sln_tag_name in seg_sln(hl.getloop({'BOTSID': 'HL'}, {'BOTSID': 'SLN'}),
                                                                        hl_out, {'BOTSID': 'hierarchical_level'}):
                # SI
                core_out(seg_si(sln, sln_out, sln_tag_name))
                # PID
                core_out(seg_pid(sln, sln_out, sln_tag_name))
                # REF
                core_out(seg_ref(sln, sln_out, sln_tag_name))
                # QTY
                core_out(seg_qty(sln, sln_out, sln_tag_name))

            # TCD
            for tcd, tcd_out, tcd_tag_name in seg_tcd(hl, hl_out, 'hierarchical_level'):
                # SI
                core_out(seg_si(tcd, tcd_out, tcd_tag_name))
        # TDS
        core_out(seg_tds(st, mesg_out, 'message'))
        # BAL
        for bal, bal_out, bal_tag_name in seg_bal(st, mesg_out, 'message'):
            # DTM
            core_out(seg_dtm(bal.getloop({'BOTSID': 'BAL'}, {'BOTSID': 'DTM'}), bal_out,
                                               {'BOTSID': bal_tag_name}))
        # CTT
        core_out(seg_ctt(st, mesg_out, 'message'))
        # SE
        core_out(seg_se(st, mesg_out, 'message'))

    return
