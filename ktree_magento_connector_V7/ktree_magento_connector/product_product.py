# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import pooler, tools
from openerp.osv import fields, osv


class product_range(osv.osv):
    _name="product.range"

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result
    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)


    _columns={
              'name':fields.char('Range Name',size=128),
              'brand_id':fields.many2one('product.brand','Brand'),
              'discount_factor':fields.integer('Discount Factor'),
              'code':fields.char('Code',size=28),
              'image':fields.binary('Image'),
              'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                    string="Medium-sized image", type="binary", multi="_get_image",
                    store={
                        'product.range': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                    },
                    help="Medium-sized image of this contact. It is automatically "\
                         "resized as a 128x128px image, with aspect ratio preserved. "\
                         "Use this field in form views or some kanban views."),
              'image_small': fields.function(_get_image, fnct_inv=_set_image,
                    string="Small-sized image", type="binary", multi="_get_image",
                    store={
                        'product.range': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                    },
                    help="Small-sized image of the product. It is automatically "\
                         "resized as a 64x64px image, with aspect ratio preserved. "\
                         "Use this field anywhere a small image is required."),
              'description':fields.text('Description'),
              'company_id':fields.many2one('res.company','Company'),
              
              'magento_id': fields.integer('Magento_id'),# addd
              
              }
    
    _defaults={
                'magento_id': lambda *a: -1,
                }
    
product_range()


class product_brand(osv.osv):
    
    _name="product.brand"

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result
    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)


    _columns={
              'name':fields.char('Brand Name',size=128),
              'manufacturer_id':fields.many2one('res.partner','Manufacturer'),
              'discount_factor':fields.integer('Discount Factor'),
              'code':fields.char('Code',size=28),
              'image':fields.binary('Image'),
              'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                    string="Medium-sized image", type="binary", multi="_get_image",
                    store={
                        'product.brand': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                    },
                    help="Medium-sized image of this contact. It is automatically "\
                         "resized as a 128x128px image, with aspect ratio preserved. "\
                         "Use this field in form views or some kanban views."),
              'image_small': fields.function(_get_image, fnct_inv=_set_image,
                    string="Small-sized image", type="binary", multi="_get_image",
                    store={
                        'product.brand': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                    },
                    help="Small-sized image of the product. It is automatically "\
                         "resized as a 64x64px image, with aspect ratio preserved. "\
                         "Use this field anywhere a small image is required."),
              'description':fields.text('Description'),
              'company_id':fields.many2one('res.company','Company')
              }

product_brand()

