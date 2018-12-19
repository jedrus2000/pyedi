#
from .telco_codes_811 import getCodeComment
#
#################################
#
# AMT
#
# Monetary Amount
#
#################################
def seg_amt(inn_loop, out_parent, xml_parent):
    tag_name = 'monetary_amount'
    for inn in inn_loop:
        out = out_parent.putloop(xml_parent, {'BOTSID': tag_name})
        qualifier_code = inn.get({'BOTSID': 'AMT', 'AMT01': None})
        out.put({'BOTSID': tag_name, 'qualifier_code': qualifier_code})
        out.put({'BOTSID': tag_name, 'qualifier_code__comment': getCodeComment(522, qualifier_code)})
        out.put({'BOTSID': tag_name, tag_name: inn.get({'BOTSID': 'AMT', 'AMT02': None})})
        yield inn, out, tag_name


#################################
#
# BAL
#
# Balance Detail
#
#################################
def seg_bal(inn_parent, out_parent, xml_parent):
    inn_loop = inn_parent.getloop({'BOTSID': inn_parent.record['BOTSID']}, {'BOTSID': 'BAL'})
    tag_name = 'balance_detail'
    for inn in inn_loop:
        out = out_parent.putloop({'BOTSID': xml_parent}, {'BOTSID': tag_name})
        type_code = inn.get({'BOTSID': 'BAL', 'BAL01': None})
        out.put({'BOTSID': tag_name, 'type_code' : type_code} )
        out.put({'BOTSID': tag_name, 'type_code__comment': getCodeComment(951, type_code)})
        amount_qualifier_code = inn.get({'BOTSID': 'BAL', 'BAL02': None})
        out.put({'BOTSID': tag_name, 'amount_qualifier_code' : amount_qualifier_code} )
        out.put(
            {'BOTSID': tag_name, 'amount_qualifier_code__comment': getCodeComment(522, amount_qualifier_code)})
        out.put(
            {'BOTSID': tag_name, 'monetary_amount': inn.get({'BOTSID': 'BAL', 'BAL03': None})})
        yield inn, out, tag_name


#################################
#
# CTT
#
# Transaction Totals
#
#################################
def seg_ctt(inn_parent, out_parent, xml_parent):
    inn_loop = inn_parent.getloop({'BOTSID': inn_parent.record['BOTSID']}, {'BOTSID': 'CTT'})
    tag_name = 'transaction_totals'
    for inn in inn_loop:
        out = out_parent.putloop({'BOTSID': xml_parent}, {'BOTSID': tag_name})
        out.put(
            {'BOTSID': tag_name, 'number_line_items': inn.get({'BOTSID': 'CTT', 'CTT01': None})})
        yield inn, out, tag_name

#################################
#
# DTM
#
# Date/Time Reference
#
#################################
def seg_dtm(inn_loop, out_parent, xml_parent):
    tag_name = 'date_time_reference'
    for inn in inn_loop:
        out = out_parent.putloop(xml_parent, {'BOTSID': tag_name})
        date_time_qualifier = inn.get({'BOTSID': 'DTM', 'DTM01': None})
        out.put({'BOTSID': tag_name, 'date_time_qualifier': date_time_qualifier})
        out.put(
            {'BOTSID': tag_name, 'date_time_qualifier__comment': getCodeComment(374, date_time_qualifier)})
        out.put({'BOTSID': tag_name, 'date': inn.get({'BOTSID': 'DTM', 'DTM02': None})})
        yield inn, out, tag_name


#################################
#
# IT1
#
# Baseline Item Data (Invoice)
#
#################################
def seg_it1(inn_loop, out_parent, xml_parent):
    tag_name = 'baseline_invoice_data'
    for inn in inn_loop:
        out = out_parent.putloop(xml_parent, {'BOTSID': tag_name})
        out.put({'BOTSID': tag_name, 'assigned_identification': inn.get({'BOTSID': 'IT1', 'IT101': None})})
        out.put({'BOTSID': tag_name, 'quantity_invoiced': inn.get({'BOTSID': 'IT1', 'IT102': None})})
        unit_measurement_code = inn.get({'BOTSID': 'IT1', 'IT103': None})
        out.put({'BOTSID': tag_name, 'unit_measurement_code': unit_measurement_code})
        out.put({'BOTSID': tag_name, 'unit_measurement_code__comment': getCodeComment(355, unit_measurement_code)})
        out.put({'BOTSID': tag_name, 'unit_price': inn.get({'BOTSID': 'IT1', 'IT104': None})})
        for k in range(6, 10, 2):
            product_service_id_qualifier = inn.get({'BOTSID': 'IT1', 'IT1{0:02d}'.format(k): None})
            out.put({'BOTSID': tag_name,
                     'product_service_id_qualifier_{0:d}'.format(int((k - 4) / 2)): product_service_id_qualifier})
            out.put({'BOTSID': tag_name,
                     'product_service_id_qualifier_{0:d}__comment'.format(int((k - 4) / 2)): getCodeComment(235,
                                                                                                       product_service_id_qualifier)})
            product_service_id = inn.get({'BOTSID': 'IT1', 'IT1{0:02d}'.format(k + 1): None})
            out.put({'BOTSID': tag_name, 'product_service_id_{0:d}'.format(int((k - 4) / 2)): product_service_id})
            out.put({'BOTSID': tag_name,
                     'product_service_id_{0:d}__comment'.format(int((k - 4) / 2)): getCodeComment(234, product_service_id)})
        yield inn, out, tag_name


#################################
#
# N1
#
# Name
#
#################################
def seg_n1(inn_loop, out_parent, xml_parent):
    tag_name = 'party_details'
    for inn in inn_loop:
        out = out_parent.putloop(xml_parent, {'BOTSID': tag_name})
        entity_identifier_code = inn.get({'BOTSID': 'N1', 'N101': None})
        out.put({'BOTSID': tag_name, 'entity_identifier_code': entity_identifier_code})
        out.put(
            {'BOTSID': tag_name, 'entity_identifier_code__comment': getCodeComment(98, entity_identifier_code)})
        out.put({'BOTSID': tag_name, 'name': inn.get({'BOTSID': 'N1', 'N102': None})})
        ident_code_qualifier = inn.get({'BOTSID': 'N1', 'N103': None})
        out.put({'BOTSID': tag_name, 'ident_code_qualifier': ident_code_qualifier})
        out.put({'BOTSID': tag_name, 'ident_code_qualifier__comment': getCodeComment(66, ident_code_qualifier)})
        out.put({'BOTSID': tag_name, 'ident_code': inn.get({'BOTSID': 'N1', 'N104': None})})
        yield inn, out, tag_name


#################################
#
# N2
#
# Additional Name Information
#
#################################
def seg_n2(inn_loop, out_parent, xml_parent):
    tag_name = 'name_add_info'
    for inn in inn_loop:
        out = out_parent.putloop(xml_parent, {'BOTSID': tag_name})
        out.put({'BOTSID': tag_name, 'name1': inn.get({'BOTSID': 'N2', 'N201': None})})
        out.put({'BOTSID': tag_name, 'name2': inn.get({'BOTSID': 'N2', 'N202': None})})
        yield inn, out, tag_name


#################################
#
# N3
#
# Address Information
#
#################################
def seg_n3(inn_loop, out_parent, xml_parent):
    tag_name = 'party_address'
    for inn in inn_loop:
        out = out_parent.putloop(xml_parent, {'BOTSID': tag_name})
        out.put({'BOTSID': tag_name, 'address_information_1': inn.get({'BOTSID': 'N3', 'N301': None})})
        out.put({'BOTSID': tag_name, 'address_information_2': inn.get({'BOTSID': 'N3', 'N302': None})})
        yield inn, out, tag_name


#################################
#
# N4
#
# Geographic Location
#
#################################
def seg_n4(inn_loop, out_parent, xml_parent):
    tag_name = 'geo_location'
    for inn in inn_loop:
        out = out_parent.putloop(xml_parent, {'BOTSID': tag_name})
        out.put({'BOTSID': tag_name, 'city_name': inn.get({'BOTSID': 'N4', 'N401': None})})
        out.put({'BOTSID': tag_name, 'state_code': inn.get({'BOTSID': 'N4', 'N402': None})})
        out.put({'BOTSID': tag_name, 'postal_code': inn.get({'BOTSID': 'N4', 'N403': None})})
        yield inn, out, tag_name


#################################
#
# NM1
#
# Individual or Organizational Name
#
#################################
def seg_nm1(inn_loop, out_parent, xml_parent):
    tag_name = 'entity_name'
    for inn in inn_loop:
        out = out_parent.putloop(xml_parent, {'BOTSID': tag_name})
        identifier_code = inn.get({'BOTSID': 'NM1', 'NM101': None})
        out.put({'BOTSID': tag_name, 'identifier_code': identifier_code})
        out.put({'BOTSID': tag_name, 'identifier_code__comment': getCodeComment(98, identifier_code)})
        type_qualifier = inn.get({'BOTSID': 'NM1', 'NM102': None})
        out.put({'BOTSID': tag_name, 'type_qualifier': type_qualifier})
        out.put({'BOTSID': tag_name, 'type_qualifier__comment': getCodeComment(1065, type_qualifier)})
        out.put({'BOTSID': tag_name, 'name': inn.get({'BOTSID': 'NM1', 'NM103': None})})
        id_code_qualifier = inn.get({'BOTSID': 'NM1', 'NM108': None})
        out.put({'BOTSID': tag_name, 'id_code_qualifier': id_code_qualifier})
        out.put({'BOTSID': tag_name, 'id_code_qualifier__comment': getCodeComment(66, id_code_qualifier)})
        out.put({'BOTSID': tag_name, 'id_code': inn.get({'BOTSID': 'NM1', 'NM109': None})})
        yield inn, out, tag_name


#################################
#
# PID
#
# Product/Item Description
#
#################################
def seg_pid(inn_parent, out_parent, xml_parent):
    inn_loop = inn_parent.getloop({'BOTSID': inn_parent.record['BOTSID']}, {'BOTSID': 'PID'})
    tag_name = 'product_description'
    for inn in inn_loop:
        out = out_parent.putloop({'BOTSID': xml_parent}, {'BOTSID': tag_name})
        item_description_type = inn.get({'BOTSID': 'PID', 'PID01': None})
        out.put({'BOTSID': tag_name, 'item_description_type': item_description_type})
        out.put({'BOTSID': tag_name, 'item_description_type__comment':
            getCodeComment(349, item_description_type)})
        product_characteristic_code = inn.get({'BOTSID': 'PID', 'PID02': None})
        out.put({'BOTSID': tag_name, 'product_characteristic_code': product_characteristic_code})
        out.put({'BOTSID': tag_name, 'product_characteristic_code__comment':
            getCodeComment(750, product_characteristic_code)})
        agency_qualifier_code = inn.get({'BOTSID': 'PID', 'PID03': None})
        out.put({'BOTSID': tag_name, 'agency_qualifier_code': agency_qualifier_code})
        out.put({'BOTSID': tag_name, 'agency_qualifier_code__comment':
            getCodeComment(559, agency_qualifier_code)})
        out.put({'BOTSID': tag_name,
                     'product_description_code': inn.get({'BOTSID': 'PID', 'PID04': None})})
        out.put({'BOTSID': tag_name, 'description': inn.get({'BOTSID': 'PID', 'PID05': None})})
        source_subqualifier = inn.get({'BOTSID': 'PID', 'PID07': None})
        out.put(
            {'BOTSID': tag_name, 'source_subqualifier': source_subqualifier})
        out.put(
            {'BOTSID': tag_name, 'source_subqualifier__comment':
                getCodeComment(822, source_subqualifier)})
        yield inn, out, tag_name


#################################
#
# QTY
#
# Reference Identification
#
#################################
def seg_qty(inn_parent, out_parent, xml_parent):
    inn_loop = inn_parent.getloop({'BOTSID': inn_parent.record['BOTSID']}, {'BOTSID': 'QTY'})
    tag_name = 'quantity'
    for inn in inn_loop:
        out = out_parent.putloop({'BOTSID' : xml_parent}, {'BOTSID': tag_name})
        qty_qual = inn.get({'BOTSID': 'QTY', 'QTY01': None})
        out.put({'BOTSID': tag_name, 'qty_qual': qty_qual})
        out.put(
            {'BOTSID': tag_name, 'qty_qual__comment': getCodeComment(673, qty_qual)})
        out.put({'BOTSID': tag_name, 'qty': inn.get({'BOTSID': 'QTY', 'QTY02': None})})
        unit_measurement_code = inn.get({'BOTSID': 'QTY', 'QTY03.01': None})
        out.put({'BOTSID': tag_name, 'unit_measurement_code' : unit_measurement_code} )
        out.put({'BOTSID': tag_name, 'unit_measurement_code__comment' : getCodeComment(355, unit_measurement_code)})
        yield inn, out, tag_name

#################################
#
# REF
#
# Reference Identification
#
#################################
def seg_ref(inn_parent, out_parent, xml_parent):
    inn_loop = inn_parent.getloop({'BOTSID': inn_parent.record['BOTSID']}, {'BOTSID': 'REF'})
    tag_name = 'reference_ident'
    for inn in inn_loop:
        out = out_parent.putloop({'BOTSID' : xml_parent}, {'BOTSID': tag_name})
        reference_ident_qual = inn.get({'BOTSID': 'REF', 'REF01': None})
        out.put({'BOTSID': tag_name, 'reference_ident_qual': reference_ident_qual})
        out.put(
            {'BOTSID': tag_name, 'reference_ident_qual__comment': getCodeComment(128, reference_ident_qual)})
        out.put({'BOTSID': tag_name, 'reference_ident_value': inn.get({'BOTSID': 'REF', 'REF02': None})})
        out.put({'BOTSID': tag_name, 'description': inn.get({'BOTSID': 'REF', 'REF03': None})})
        yield inn, out, tag_name


#################################
#
# SE
#
# Transaction Set Trailer
#
#################################
def seg_se(inn_parent, out_parent, xml_parent):
    inn_loop = inn_parent.getloop({'BOTSID': inn_parent.record['BOTSID']}, {'BOTSID': 'SE'})
    tag_name = 'transaction_set_trailer'
    for inn in inn_loop:
        out = out_parent.putloop({'BOTSID': xml_parent}, {'BOTSID': tag_name})
        out.put({'BOTSID': tag_name, 'number_included_segments': inn.get({'BOTSID': 'SE', 'SE01': None})})
        out.put({'BOTSID': tag_name, 'transaction_set_control_number': inn.get({'BOTSID': 'SE', 'SE02': None})})
        yield inn, out, tag_name


#################################
#
# SI
#
# Service Characteristic Identification
#
#################################
def seg_si(inn_parent, out_parent, xml_parent):
    inn_loop = inn_parent.getloop({'BOTSID': inn_parent.record['BOTSID']}, {'BOTSID': 'SI'})
    tag_name = 'service_characteristic_ident'
    for inn in inn_loop:
        out = out_parent.putloop({'BOTSID': xml_parent}, {'BOTSID': tag_name})
        agency_qualifier_code = inn.get({'BOTSID': 'SI', 'SI01': None})
        out.put({'BOTSID': tag_name, 'agency_qualifier_code': agency_qualifier_code})
        out.put({'BOTSID': tag_name,
                    'agency_qualifier_code__comment': getCodeComment(559, agency_qualifier_code)})
        for k in range(2, 22, 2):
            service_characteristics_qualifier = inn.get({'BOTSID': 'SI', 'SI{0:02d}'.format(k): None})
            out.put({'BOTSID': tag_name,
                        'service_characteristics_qualifier_{0:d}'.format(int(k / 2)):
                            service_characteristics_qualifier})
            out.put({'BOTSID': tag_name,
                        'service_characteristics_qualifier_{0:d}__comment'.format(int(k / 2)):
                            getCodeComment(1000, service_characteristics_qualifier)})
            out.put({'BOTSID': tag_name, 'product_service_id_{0:d}'.format(int(k / 2)):
                inn.get({'BOTSID': 'SI', 'SI{0:02d}'.format(k + 1): None})})
        yield inn, out, tag_name


#################################
#
# SLN
#
# Subline Item Detail
#
#################################
def seg_sln(inn_loop, out_parent, xml_parent):
    tag_name = 'subline_item_detail'
    for inn in inn_loop:
        out = out_parent.putloop(xml_parent, {'BOTSID': tag_name})
        out.put({'BOTSID': tag_name, 'assigned_identification_1': inn.get({'BOTSID': 'SLN', 'SLN01': None})})
        out.put({'BOTSID': tag_name, 'assigned_identification_2': inn.get({'BOTSID': 'SLN', 'SLN02': None})})
        relationship_code = inn.get({'BOTSID': 'SLN', 'SLN03': None})
        out.put({'BOTSID': tag_name, 'relationship_code_1': relationship_code})
        out.put({'BOTSID': tag_name, 'relationship_code_1__comment': getCodeComment(662, relationship_code)})
        out.put({'BOTSID': tag_name, 'quantity': inn.get({'BOTSID': 'SLN', 'SLN04': None})})
        unit_measurement_code = inn.get({'BOTSID': 'SLN', 'SLN05.01': None})
        #out.put({'BOTSID': tag_name}, {'BOTSID': 'composite_unit_of_measure', 'unit_measurement_code' : unit_measurement_code} )
        out.put({'BOTSID': tag_name, 'unit_measurement_code' : unit_measurement_code} )
        out.put({'BOTSID': tag_name, 'unit_measurement_code__comment' : getCodeComment(355, unit_measurement_code)})
        out.put({'BOTSID': tag_name, 'unit_price': inn.get({'BOTSID': 'SLN', 'SLN06': None})})
        relationship_code = inn.get({'BOTSID': 'SLN', 'SLN08': None})
        out.put({'BOTSID': tag_name, 'relationship_code_2': relationship_code})
        out.put({'BOTSID': tag_name, 'relationship_code_2__comment': getCodeComment(662, relationship_code)})
        for k in range(9, 21, 2):
            product_service_id_qualifier = inn.get({'BOTSID': 'SLN', 'SLN{0:02d}'.format(k): None})
            out.put({'BOTSID': tag_name,
                     'product_service_id_qualifier_{0:d}'.format(int((k - 7) / 2)): product_service_id_qualifier})
            out.put({'BOTSID': tag_name,
                     'product_service_id_qualifier_{0:d}__comment'.format(int((k - 7) / 2)): getCodeComment(235,
                     product_service_id_qualifier)})
            product_service_id = inn.get({'BOTSID': 'SLN', 'SLN{0:02d}'.format(k + 1): None})
            out.put({'BOTSID': tag_name, 'product_service_id_{0:d}'.format(int((k - 7) / 2)): product_service_id})
            out.put({'BOTSID': tag_name,
                     'product_service_id_{0:d}__comment'.format(int((k - 7) / 2)): getCodeComment(234, product_service_id)})
        yield inn, out, tag_name


#################################
#
# TCD
#
# Itemized Call Detail
#
#################################
def seg_tcd(inn_parent, out_parent, xml_parent):
    inn_loop = inn_parent.getloop({'BOTSID': inn_parent.record['BOTSID']}, {'BOTSID': 'TCD'})
    tag_name = 'itemized_call_detail'
    for inn in inn_loop:
        out = out_parent.putloop({'BOTSID': xml_parent}, {'BOTSID': tag_name})
        out.put({'BOTSID': tag_name, 'assigned_id': inn.get({'BOTSID': 'TCD', 'TCD01': None})})
        out.put({'BOTSID': tag_name, 'date': inn.get({'BOTSID': 'TCD', 'TCD02': None})})
        out.put({'BOTSID': tag_name, 'time': inn.get({'BOTSID': 'TCD', 'TCD03': None})})
        location_qualifier_1 = inn.get({'BOTSID': 'TCD', 'TCD04': None})
        out.put({'BOTSID': tag_name, 'location_qualifier_1': location_qualifier_1})
        out.put({'BOTSID': tag_name, 'location_qualifier_1__comment': getCodeComment(309, location_qualifier_1)})
        out.put({'BOTSID': tag_name, 'location_identifier_1': inn.get({'BOTSID': 'TCD', 'TCD05': None})})
        out.put({'BOTSID': tag_name, 'state_code_1': inn.get({'BOTSID': 'TCD', 'TCD06': None})})
        location_qualifier_2 = inn.get({'BOTSID': 'TCD', 'TCD07': None})
        out.put({'BOTSID': tag_name, 'location_qualifier_2': location_qualifier_2})
        out.put({'BOTSID': tag_name, 'location_qualifier_2__comment': getCodeComment(309, location_qualifier_2)})
        out.put({'BOTSID': tag_name, 'location_identifier_2': inn.get({'BOTSID': 'TCD', 'TCD08': None})})
        out.put({'BOTSID': tag_name, 'state_code_2': inn.get({'BOTSID': 'TCD', 'TCD09': None})})
        out.put({'BOTSID': tag_name, 'measurement_value_1': inn.get({'BOTSID': 'TCD', 'TCD10': None})})
        out.put({'BOTSID': tag_name, 'measurement_value_2': inn.get({'BOTSID': 'TCD', 'TCD11': None})})
        out.put({'BOTSID': tag_name, 'monetary_amount': inn.get({'BOTSID': 'TCD', 'TCD12': None})})
        yield inn, out, tag_name


#################################
#
# TDS
#
# Itemized Call Detail
#
#################################
def seg_tds(inn_parent, out_parent, xml_parent):
    inn_loop = inn_parent.getloop({'BOTSID': inn_parent.record['BOTSID']}, {'BOTSID': 'TDS'})
    tag_name = 'total_monetary_value_summary'
    for inn in inn_loop:
        out = out_parent.putloop({'BOTSID': xml_parent}, {'BOTSID': tag_name})
        out.put({'BOTSID': tag_name, 'amount': inn.get({'BOTSID': 'TDS', 'TDS01': None})})
        yield inn, out, tag_name


#################################
#
# TXI
#
# Reference Identification
#
#################################
def seg_txi(inn_loop, out_parent, xml_parent):
    tag_name = 'tax_info'
    for inn in inn_loop:
        out = out_parent.putloop(xml_parent, {'BOTSID': tag_name})
        tax_type_code = inn.get({'BOTSID': 'TXI', 'TXI01': None})
        out.put({'BOTSID': tag_name, 'tax_type_code': tax_type_code})
        out.put({'BOTSID': tag_name, 'tax_type_code__comment': getCodeComment(963, tax_type_code)})
        out.put({'BOTSID': tag_name, 'monetary_amount': inn.get({'BOTSID': 'TXI', 'TXI02': None})})
        tax_jurisdiction_code_qualifier = inn.get({'BOTSID': 'TXI', 'TXI04': None})
        out.put({'BOTSID': tag_name, 'tax_jurisdiction_code_qualifier': tax_jurisdiction_code_qualifier})
        out.put({'BOTSID': tag_name,
                 'tax_jurisdiction_code_qualifier__comment': getCodeComment(995, tax_jurisdiction_code_qualifier)})
        out.put({'BOTSID': tag_name, 'tax_jurisdiction_code': inn.get({'BOTSID': 'TXI', 'TXI05': None})})
        tax_exempt_code = inn.get({'BOTSID': 'TXI', 'TXI06': None})
        out.put({'BOTSID': tag_name, 'tax_exempt_code': tax_exempt_code})
        out.put({'BOTSID': tag_name, 'tax_exempt_code__comment': getCodeComment(441, tax_exempt_code)})
        relationship_code = inn.get({'BOTSID': 'TXI', 'TXI07': None})
        out.put({'BOTSID': tag_name, 'relationship_code': relationship_code})
        out.put({'BOTSID': tag_name, 'relationship_code__comment': getCodeComment(662, relationship_code)})
        out.put({'BOTSID': tag_name, 'assigned_identification': inn.get({'BOTSID': 'TXI', 'TXI10': None})})
        yield inn, out, tag_name
