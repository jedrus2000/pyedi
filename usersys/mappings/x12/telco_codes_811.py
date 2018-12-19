#################################
#
# Codes translating functions
#
#
#################################
def getCodeComment(id, code):
    return {
        66: {
            '1': 'D-U-N-S Number, Dun & Bradstreet',
            '9': 'D-U-N-S+4, D-U-N-S Number with Four Character Suffix',
            '40': 'Electronic Mail User Code',
            '41': 'Telecommunications Carrier Identification Code',
            '42': 'Telecommunications Pseudo Carrier Identification Code',
            '91': 'Assigned by Seller or Seller s Agent',
            '92': 'Assigned by Buyer or Buyer s Agent',
        },

        98: {
            '77': 'Service Location',
            'IA': 'Installed At',
            'PE': 'Payee',
            'PR': 'Payer',
            'SJ': 'Service Provider',
            'AAA': 'Sub-account',
        },

        128: {
            '11': 'Account Number',
            '12': 'Billing Account',
            '14': 'Master Account Number',
            '4L': 'Location-specific Services Reference Number',
            '8M': 'Originating Company Identifier',
            '8N': 'Receiving Company Identifier',
            'AAO': 'Carrier Assigned Code',
            'BB': 'Authorization Number',
            'BF': 'Billing Center Identification',
            'BLT': 'Billing Type',
            'CT': 'Contract Number',
            'DO': 'Delivery Order Number',
            'EH': 'Financial Classification Code',
            'HB': 'Bill & Hold Invoice Number',
            'IV': "Seller's Invoice Number",
            'LJ': 'Local Jurisdiction',
            'LU': 'Location Number',
            'P4': 'Project Code',
            'PO': 'Purchase Order Number',
            'R0': 'Regiristo Federal de Contribuyentes (Mexican Federal Tax ID Number)',
            'RE': 'Release Number',
            'SU': 'Special Processing Code',
            'V0': 'Version',
            'VN': 'Vendor Order Number',
            'YN': 'Receiver ID Qualifier',
            'ZH': 'Carrier Assigned Reference Number',

            'AP': 'Accounts Receivable Number',
            'CR': 'Customer Reference Number',
            'ZZ': 'Mutually Defined',
        },

        234: {
            '0200': 'Monthly Service Charge',
            '0400': 'Other Charges and Credits/Additions and Changes',
            '0500': 'Itemized Calls',
            '0700': 'Usage',
        },

        235: {
            'SV': 'Service Rendered',
        },

        349: {
            'F': 'Free-form',
            'S': 'Structured (From Industry Code List)',
            'X': 'Semi-structured (Code and Text)',
        },

        309: {

        },

        355: {
            'EA': 'Each',
            'M4': 'Monetary Value',
            'MO': 'Months',
        },

        374: {
            '001': 'Cancel After',
            '003': 'Invoice',
            '007': 'Effective',
            '009': 'Process',
            '035': 'Delivered',
            '092': 'Contract Effective',
            '093': 'Contract Expiration',
            '102': 'Issue',
            '150': 'Service Period Start',
            '151': 'Service Period End',
            '152': 'Effective Date of Change',
            '153': 'Service Interruption',
            '154': 'Adjustment Period Start',
            '155': 'Adjustment Period End',
            '183': 'Connection',
            '186': 'Invoice Period Start',
            '187': 'Invoice Period End',
            '193': 'Period Start',
            '194': 'Period End',
            '198': 'Completion',
            '306': 'Adjustment Effective Date',
            '321': 'Purchased',
            '346': 'Plan Begin',
            '347': 'Plan End',
            '507': 'Extract',
            '949': 'Payment Effective',

        },

        441: {
            '2': 'No (Not Tax Exempt)',
        },

        522: {
            '1': 'Line Item Total',
            '5': 'Total Invoice Amount',
            '6': 'Amount Subject to Total Monetary Discount',
            '8': 'Total Monetary Discount Amount',
            '1E': 'Fixed Price',
            'AD': 'Adjusted Total',
            'AP': 'Amount Prior to Fractionalization',
            'AQ': 'Average Price Per Call',
            'AS': 'Average Price Per Minute',
            'AX': 'Previous Price',
            'BT': 'Bank Reject Total',
            'BM': 'Adjustments',
            'C4': 'Prior Payment - Actual',
            'CH': 'Change Amount',
            'CS': 'Commission Sales',
            'CT': 'Contract',
            'KO': 'Committed Amount',
            'LI': 'Line Item Unit Price',
            'LM': 'Limit',
            'N': 'Net',
            'NA': 'Net Adjustment',
            'NO': 'Non Commission Sales',
            'NR': 'Nonrecurring',
            'NS': 'Net Savings Amount',
            'PB': 'Billed Amount',
            'RJ': 'Rate Amount',
            'SC': 'Total Service Charge',
            'TP': 'Total payment amount',
            'TS': 'Total Sales',
            'TT': 'Total Transaction Amount',
            'ZT': 'Prorated Amount',
        },

        559: {
            'AS': 'Assigned by Seller',
            'TI': 'Telecommunications Industry',
        },

        662: {
            'A': 'Add',
            'I': 'Included',
        },

        673: {
            '99': 'Quantity Used'
        },

        750: {
            '08': 'Product',
            '09': 'Sub-product',
            'SF': 'Service Feature',
        },

        822: {
            'ALTPRDDESC': "Customer's Alternate Product Description",
            'GROUP': "Customer's Group Code",
            'SECTION': "Customer's Section Code",
            'SUBGROUP': "Customer's Sub-Group Code",
        },

        951: {
            'M': 'Current Month',
            'P': 'Previous Month',
        },

        963: {
            'FD': 'Federal Tax',
            'LO': 'Local Tax (Not Sales Tax)',
            'SL': 'State and Local Tax',
            'SU': 'Sales and Use Tax',
        },

        995: {
            'VE': 'Vertex',
        },

        1000: {
            'BT': 'Basic Service Type',
            'CN': 'Circuit Number Identification Code',
            'OD': 'Other Charges and Credits Description Code',
            'TN': 'Telephone Number',
            'ZZ': 'Mutually Defined',
        },

        1065: {
            '1': 'Person',
            '2': 'Non-Person Entity',
            '3': 'Unknown',
        },
    }[id].get(code, None)
