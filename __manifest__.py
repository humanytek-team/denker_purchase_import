# -*- coding: utf-8 -*-
{
    'name' : 'Pestaña de importacion en ordenes de compra',
    'version' : '1',
    'author': 'Humanytek',
    'description': """
        Agrega pestania de importaciones en ordenes de compra
    """,
    'category' : 'Purchases',
    'depends' : ['purchase'],
    'data': [
        'purchase_view.xml',
        #'security/groups.xml',
        'security/ir.model.access.csv',
        
    ],
    'demo': [

    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
