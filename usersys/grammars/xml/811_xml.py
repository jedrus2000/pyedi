from pyedi.botslib.consts import *

nextmessage = ({'BOTSID': 'envelope'}, {'BOTSID': 'message'})

syntax = {
    'merge': False,
    'indented': True  # creates nice printout
}

structure = [
    {ID: 'envelope', MIN: 1, MAX: 1,
     QUERIES: {
         'frompartner': {'BOTSID': 'envelope', 'sender': None},
         'topartner': {'BOTSID': 'envelope', 'receiver': None},
         'testindicator': {'BOTSID': 'envelope', 'test': None},
     }, LEVEL: [
        {ID: 'message', MIN: 1, MAX: 9999, LEVEL: [
            {ID: 'transaction_set_header', MIN: 1, MAX: 1},
            {ID: 'begseg_for_invoice', MIN: 1, MAX: 1},
            {ID: 'reference_ident', MIN: 0, MAX: 99999},
            {ID: 'terms_of_sale', MIN: 0, MAX: 5},
            {ID: 'date_time_reference', MIN: 0, MAX: 10},
            {ID: 'party_details', MIN: 0, MAX: 99999, LEVEL: [
                {ID: 'party_address', MIN: 0, MAX: 2},
                {ID: 'geo_location', MIN: 0, MAX: 1},
            ]},
            {ID: 'hierarchical_level', MIN: 1, MAX: 99999, LEVEL: [
                {ID: 'assigned_number', MIN: 0, MAX: 99999, LEVEL: [
                    {ID: 'service_characteristic_ident', MIN: 0, MAX: 8},
                    {ID: 'product_description', MIN: 0, MAX: 200},
                    {ID: 'reference_ident', MIN: 0, MAX: 99999},
                    {ID: 'monetary_amount', MIN: 0, MAX: 5},
                    {ID: 'date_time_reference', MIN: 0, MAX: 8},
                    {ID: 'tax_info', MIN: 0, MAX: 99999},
                ]},
                {ID: 'entity_name', MIN: 0, MAX: 1, LEVEL: [
                    {ID: 'name_add_info', MIN: 0, MAX: 2},
                    {ID: 'party_address', MIN: 0, MAX: 2},
                    {ID: 'geo_location', MIN: 0, MAX: 1},
                ]},

                {ID: 'baseline_invoice_data', MIN: 0, MAX: 999999, LEVEL: [
                    {ID: 'date_time_reference', MIN: 0, MAX: 10},
                ]},

                {ID: 'subline_item_detail',  MIN: 0, MAX: 99999, LEVEL: [
                    {ID: 'service_characteristic_ident', MIN: 0, MAX: 2},
                    {ID: 'product_description', MIN: 0, MAX: 200},
                    {ID: 'reference_ident', MIN: 0, MAX: 99999},
                    {ID: 'quantity', MIN: 0, MAX: 99999},
                ]},

                {ID: 'itemized_call_detail', MIN: 0, MAX: 99999, LEVEL: [
                    {ID: 'service_characteristic_ident', MIN: 0, MAX: 2},
                ]},
            ]},

            {ID: 'total_monetary_value_summary', MIN: 1, MAX: 1},

            {ID: 'balance_detail', MIN: 0, MAX: 99999, LEVEL: [
                {ID: 'date_time_reference', MIN: 0, MAX: 1},
            ]},

            {ID: 'transaction_totals', MIN: 0, MAX: 1},
            {ID: 'transaction_set_trailer', MIN: 1, MAX: 1},
            #            {ID:'partys',MIN:0,MAX:1,LEVEL:[
            #                {ID:'party',MIN:1,MAX:99},
            #            ]},
            #            {ID:'lines',MIN:0,MAX:1,LEVEL:[
            #               {ID:'line',MIN:1,MAX:99999},
            #            ]},
        ]},
    ]},
]

recorddefs = {

    'envelope': [
        ['BOTSID', 'M', 255, 'A'],
        ['sender', 'M', 35, 'AN'],
        ['receiver', 'M', 35, 'AN'],
        ['testindicator', 'C', 35, 'AN'],
    ],

    'message': [
        ['BOTSID', 'M', 255, 'A'],
    ],

    # AMT
    'monetary_amount': [
        ['BOTSID', 'M', 255, 'A'],
        ['qualifier_code', 'M', 3, 'AN'],
        ['qualifier_code__comment', 'C', 255, 'AN'],
        ['monetary_amount', 'M', 18, 'R'],

    ],

    # BAL
    'balance_detail': [
        ['BOTSID', 'M', 255, 'A'],
        ['type_code', 'M', 2, 'AN'],
        ['type_code__comment', 'C', 255, 'AN'],
        ['amount_qualifier_code', 'M', 3, 'AN'],
        ['amount_qualifier_code__comment', 'C', 255, 'AN'],
        ['monetary_amount', 'M', 18, 'R'],
    ],

    # BIG
    'begseg_for_invoice': [
        ['BOTSID', 'M', 255, 'A'],
        ['invoice_issue_date', 'M', (8, 8), 'DT'],  # CCYYMMDD # BIG01
        ['invoice_number', 'M', 22, 'AN'],  # BIG02
        ['transaction_type_code', 'C', (2, 2), 'AN'],  # BIG07
        ['transaction_type_code__comment', 'C', 255, 'AN'],
    ],

    # CTT
    'transaction_totals': [
        ['BOTSID', 'M', 255, 'A'],
        ['number_line_items', 'M', 6, 'R'],
    ],

    # DTM
    'date_time_reference': [
        ['BOTSID', 'M', 255, 'A'],
        ['date_time_qualifier', 'M', (3, 3), 'AN'],
        ['date_time_qualifier__comment', 'C', 255, 'AN'],
        ['date', 'C', (8, 8), 'DT'],
    ],

    # IT1
    'baseline_invoice_data': [
        ['BOTSID', 'M', 255, 'A'],
        ['assigned_identification', 'C', 20, 'AN'],
        ['quantity_invoiced', 'C', 10, 'R'],
        ['unit_measurement_code', 'C', (2, 2), 'AN'],
        ['unit_measurement_code__comment', 'C', 255, 'AN'],
        ['unit_price', 'C', 17, 'R'],
        ['product_service_id_qualifier_1', 'C', (2, 2), 'AN'],
        ['product_service_id_qualifier_1__comment', 'C', 255, 'AN'],
        ['product_service_id_1', 'C', 48, 'AN'],
        ['product_service_id_1__comment', 'C', 255, 'AN'],
        ['product_service_id_qualifier_2', 'C', (2, 2), 'AN'],
        ['product_service_id_qualifier_2__comment', 'C', 255, 'AN'],
        ['product_service_id_2', 'C', 48, 'AN'],
        ['product_service_id_2__comment', 'C', 255, 'AN'],
        ['product_service_id_qualifier_3', 'C', (2, 2), 'AN'],
        ['product_service_id_qualifier_3__comment', 'C', 255, 'AN'],
        ['product_service_id_3', 'C', 48, 'AN'],
        ['product_service_id_3__comment', 'C', 255, 'AN'],
    ],

    # N1
    'party_details': [
        ['BOTSID', 'M', 255, 'A'],
        ['entity_identifier_code', 'M', (2, 3), 'AN'],
        ['entity_identifier_code__comment', 'C', 255, 'AN'],
        ['name', 'C', 60, 'AN'],
        ['ident_code_qualifier', 'C', 2, 'AN'],
        ['ident_code_qualifier__comment', 'C', 255, 'AN'],
        ['ident_code', 'C', (2, 80), 'AN'],
    ],

    # N2
    'name_add_info': [
        ['BOTSID', 'M', 255, 'A'],
        ['name1', 'M', 60, 'AN'],
        ['name2', 'C', 60, 'AN'],
    ],

    # N3
    'party_address': [
        ['BOTSID', 'M', 255, 'A'],
        ['address_information_1', 'M', 55, 'AN'],
        ['address_information_2', 'C', 55, 'AN'],
    ],

    # N4
    'geo_location': [
        ['BOTSID', 'M', 255, 'A'],
        ['city_name', 'C', (2, 30), 'AN'],
        ['state_code', 'C', (2, 2), 'AN'],
        ['postal_code', 'C', (3, 15), 'AN'],
    ],

    # NM1
    'entity_name': [
        ['BOTSID', 'M', 255, 'A'],
        ['identifier_code', 'M', (2, 3), 'AN'],
        ['identifier_code__comment', 'C', 255, 'AN'],
        ['type_qualifier', 'C', 255, 'AN'],
        ['type_qualifier__comment', 'C', 255, 'AN'],
        ['name', 'C', 35, 'AN'],
        ['id_code_qualifier', 'C', 2, 'AN'],
        ['id_code_qualifier__comment', 'C', 255, 'AN'],
        ['id_code', 'C', (2, 80), 'AN'],
    ],

    # HL
    'hierarchical_level': [
        ['BOTSID', 'M', 255, 'A'],
        ['id_number', 'M', 12, 'AN'],
        ['parent_id_number', 'C', 12, 'AN'],
        ['level_code', 'M', 2, 'AN'],
        ['level_code__comment', 'C', 255, 'AN'],
        ['child_code', 'C', 1, 'AN'],
        ['child_code__comment', 'C', 255, 'AN'],
    ],

    # LX
    'assigned_number': [
        ['BOTSID', 'M', 255, 'A'],
        ['number', 'M', 6, 'R'],
    ],

    # ITD
    'terms_of_sale': [
        ['BOTSID', 'M', 255, 'A'],
        ['terms_type_code', 'C', (2, 2), 'AN'],
        ['terms_type_code__comment', 'C', 255, 'AN'],
        ['terms_net_due_date', 'C', (8, 8), 'DT'],
    ],

    # PID
    'product_description': [
        ['BOTSID', 'M', 255, 'A'],
        ['item_description_type', 'M', 1, 'AN'],
        ['item_description_type__comment', 'C', 255, 'AN'],
        ['product_characteristic_code',  'C', (2, 3), 'AN'],
        ['product_characteristic_code__comment', 'C', 255, 'AN'],
        ['agency_qualifier_code', 'C', (2, 2), 'AN'],
        ['agency_qualifier_code__comment', 'C', 255, 'AN'],
        ['product_description_code', 'C', 12, 'AN'],
        ['description', 'C', 80, 'AN'],
        ['source_subqualifier', 'C', 15, 'AN'],
        ['source_subqualifier__comment', 'C', 255, 'AN'],
    ],

    # QTY
    'quantity': [
        ['BOTSID', 'M', 255, 'A'],
        ['qty_qual', 'M', (2, 2), 'AN'],
        ['qty_qual__comment', 'C', 255, 'AN'],
        ['qty', 'C', 15, 'R'],
        ['unit_measurement_code', 'M', (2, 2), 'AN'],
        ['unit_measurement_code__comment', 'C', 255, 'AN'],
    ],
    
    # REF
    'reference_ident': [
        ['BOTSID', 'M', 255, 'A'],
        ['reference_ident_qual', 'M', (2, 3), 'AN'],
        ['reference_ident_qual__comment', 'C', 255, 'AN'],
        ['reference_ident_value', 'C', 30, 'AN'],
        ['description', 'C', 80, 'AN'],
    ],

    # SE
    'transaction_set_trailer' : [
        ['BOTSID', 'M', 255, 'A'],
        ['number_included_segments', 'M', 10,'R'],
        ['transaction_set_control_number', 'M', (4,9), 'AN'],
    ],

    # SI
    'service_characteristic_ident': [
        ['BOTSID', 'M', 255, 'A'],
        ['agency_qualifier_code', 'M', (2, 2), 'AN'],
        ['agency_qualifier_code__comment', 'C', 255, 'AN'],
        ['service_characteristics_qualifier_1', 'M', (2, 2), 'AN'],  # EDI guideline pages 10.4-22-10.4-62 - TODO
        ['service_characteristics_qualifier_1__comment', 'C', 255, 'AN'],
        ['product_service_id_1', 'M', 48, 'AN'],
        ['service_characteristics_qualifier_2', 'C', (2, 2), 'AN'],
        ['service_characteristics_qualifier_2__comment', 'C', 255, 'AN'],
        ['product_service_id_2', 'C', 48, 'AN'],
        ['service_characteristics_qualifier_3', 'C', (2, 2), 'AN'],
        ['service_characteristics_qualifier_3__comment', 'C', 255, 'AN'],
        ['product_service_id_3', 'C', 48, 'AN'],
        ['service_characteristics_qualifier_4', 'C', (2, 2), 'AN'],
        ['service_characteristics_qualifier_4__comment', 'C', 255, 'AN'],
        ['product_service_id_4', 'C', 48, 'AN'],
        ['service_characteristics_qualifier_5', 'C', (2, 2), 'AN'],
        ['service_characteristics_qualifier_5__comment', 'C', 255, 'AN'],
        ['product_service_id_5', 'C', 48, 'AN'],
        ['service_characteristics_qualifier_6', 'C', (2, 2), 'AN'],
        ['service_characteristics_qualifier_6__comment', 'C', 255, 'AN'],
        ['product_service_id_6', 'C', 48, 'AN'],
        ['service_characteristics_qualifier_7', 'C', (2, 2), 'AN'],
        ['service_characteristics_qualifier_7__comment', 'C', 255, 'AN'],
        ['product_service_id_7', 'C', 48, 'AN'],
        ['service_characteristics_qualifier_8', 'C', (2, 2), 'AN'],
        ['service_characteristics_qualifier_8__comment', 'C', 255, 'AN'],
        ['product_service_id_8', 'C', 48, 'AN'],
        ['service_characteristics_qualifier_9', 'C', (2, 2), 'AN'],
        ['service_characteristics_qualifier_9__comment', 'C', 255, 'AN'],
        ['product_service_id_9', 'C', 48, 'AN'],
        ['service_characteristics_qualifier_10', 'C', (2, 2), 'AN'],
        ['service_characteristics_qualifier_10__comment', 'C', 255, 'AN'],
        ['product_service_id_10', 'C', 48, 'AN'],
    ],

    # SLN
    'subline_item_detail': [
        ['BOTSID', 'M', 255, 'A'],
        ['assigned_identification_1', 'M', 20, 'AN'],
        ['assigned_identification_2', 'C', 20, 'AN'],
        ['relationship_code_1', 'M', 1, 'AN'],
        ['relationship_code_1__comment', 'C', 255, 'AN'],
        ['quantity', 'C', 15, 'R'],
        #['composite_unit_of_measure', 'C', [
            ['unit_measurement_code', 'M', (2, 2), 'AN'],
            ['unit_measurement_code__comment', 'C', 255, 'AN'],
        #],],
        ['unit_price', 'C', 17, 'R'],
        ['relationship_code_2', 'M', 1, 'AN'],
        ['relationship_code_2__comment', 'C', 255, 'AN'],
        ['product_service_id_qualifier_1', 'C', (2, 2), 'AN'],
        ['product_service_id_qualifier_1__comment', 'C', 255, 'AN'],
        ['product_service_id_1', 'C', 48, 'AN'],
        ['product_service_id_1__comment', 'C', 255, 'AN'],
        ['product_service_id_qualifier_2', 'C', (2, 2), 'AN'],
        ['product_service_id_qualifier_2__comment', 'C', 255, 'AN'],
        ['product_service_id_2', 'C', 48, 'AN'],
        ['product_service_id_2__comment', 'C', 255, 'AN'],
        ['product_service_id_qualifier_3', 'C', (2, 2), 'AN'],
        ['product_service_id_qualifier_3__comment', 'C', 255, 'AN'],
        ['product_service_id_3', 'C', 48, 'AN'],
        ['product_service_id_3__comment', 'C', 255, 'AN'],
        ['product_service_id_qualifier_4', 'C', (2, 2), 'AN'],
        ['product_service_id_qualifier_4__comment', 'C', 255, 'AN'],
        ['product_service_id_4', 'C', 48, 'AN'],
        ['product_service_id_4__comment', 'C', 255, 'AN'],
        ['product_service_id_qualifier_5', 'C', (2, 2), 'AN'],
        ['product_service_id_qualifier_5__comment', 'C', 255, 'AN'],
        ['product_service_id_6', 'C', 48, 'AN'],
        ['product_service_id_6__comment', 'C', 255, 'AN'],
        ['product_service_id_qualifier_7', 'C', (2, 2), 'AN'],
        ['product_service_id_qualifier_7__comment', 'C', 255, 'AN'],
        ['product_service_id_7', 'C', 48, 'AN'],
        ['product_service_id_7__comment', 'C', 255, 'AN'],

    ],

    # ST
    'transaction_set_header': [
        ['BOTSID', 'M', 255, 'A'],
        ['identifier_code', 'M', 3, 'AN'],
        ['control_number', 'M', 9, 'AN'],
    ],

    # TCD
    'itemized_call_detail': [
        ['BOTSID', 'M', 255, 'A'],
        ['assigned_id', 'C', 20,'AN'],
        ['date', 'C', (8,8),'DT'],
        ['time', 'C', (4,8),'TM'],
        ['location_qualifier_1', 'C', 2,'AN'],
        ['location_qualifier_1__comment', 'C', 30, 'AN'],
        ['location_identifier_1', 'C', (2,2), 'AN'],
        ['state_code_1', 'C', 2,'AN'],
        ['location_qualifier_2', 'C', 2,'AN'],
        ['location_qualifier_2__comment', 'C', 30, 'AN'],
        ['location_identifier_2', 'C', (2,2), 'AN'],
        ['state_code_2', 'C', 2,'AN'],
        ['measurement_value_1', 'C', 20,'R'],
        ['measurement_value_2', 'C', 20,'R'],
        ['monetary_amount', 'C', 18,'R']
    ],

    # TDS
    'total_monetary_value_summary': [
        ['BOTSID', 'M', 255, 'A'],
        ['amount', 'M', 15, 'N'],
    ],

    # TXI
    'tax_info': [
        ['BOTSID', 'M', 255, 'A'],
        ['tax_type_code', 'M', (2, 2), 'AN'],
        ['tax_type_code__comment', 'C', 255, 'AN'],
        ['monetary_amount', 'C', 18, 'R'],
        ['tax_jurisdiction_code_qualifier', 'C', (2, 2), 'AN'],
        ['tax_jurisdiction_code_qualifier__comment', 'C', 255, 'AN'],
        ['tax_jurisdiction_code', 'C', 10, 'AN'],
        ['tax_exempt_code', 'C', 1, 'AN'],
        ['tax_exempt_code__comment', 'C', 255, 'AN'],
        ['relationship_code', 'C', 1, 'AN'],
        ['relationship_code__comment', 'C', 255, 'AN'],
        ['assigned_identification', 'C', 20, 'AN'],
    ],

}
