from osv import fields,osv
from mx import DateTime
import netsvc
import tools
import pooler
import time
import datetime
import math
import os
import traceback
from pprint import pprint
import base64, urllib
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
#inherit magento_configuration class to add sale import function
class magento_configuration(osv.osv):
    _inherit = 'magento.configuration'
    
    def import_orders (self,cr,uid): #Customized Import Order Function
        total_no_of_records=0# Number of sale order imported  
        start_timestamp = str(DateTime.utc())
        if True:
            # magneto object through which connecting openerp with defined magento configuration start
            start_timestamp = str(DateTime.utc())
            magento_configuration_object = self.pool.get('magento.configuration').get_magento_configuration_object(cr, uid)
            last_import = magento_configuration_object[0].last_imported_invoice_timestamp
            [status, server, session] = self.pool.get('magento.configuration').magento_openerp_syn(cr, uid)
            #checking server status
            if not status:
                raise osv.except_osv(_('There is no connection!'),_("There is no connection established with magento server\n\
                  please check the url,username and password") )
                server.endSession(session)
                return -1
            #end
            #API to fetch all sale order information###################################################
	    increment = 1000
            index = 1
            while(True):
              stop = index + increment - 1
	      if last_import:
		  listorder = server.call(session, 'sales_order.list',[{'updated_at': {'from':last_import}}])
	      else:
                  listorder = server.call(session, 'sales_order.list',[{'updated_at': {'from':last_import},'order_id': {'from': str(index), 'to': str(stop)}}])
              index = stop + 1
              all_increment_id=[]
              all_customer_id=[]
              for info_order in listorder:
                if info_order['customer_id']:
                    all_customer_id.append(info_order['customer_id'])
                all_increment_id.append(info_order['increment_id'])
              min=0
              max_number_order_import=20
              if magento_configuration_object[0].max_number_order_import:
                max_number_order_import=int(magento_configuration_object[0].max_number_order_import)
              max=max_number_order_import
              length_ord=len(listorder)
              while length_ord>0:
                all_customer_id_max=all_customer_id[min:max]
                all_increment_id_max=all_increment_id[min:max]  
#                try:
#                   #API to get customer information for all customer_id at a time 
                info_customers = [server.call(session, 'customapi_customer.itemslist' , [all_customer_id_max])][0];
#                except:
#                   info_customers=[] 
                
#                try:     
                   #API to get sale order information for all increment_ids at a time
                info_orders = [server.call(session, 'customapi_order.itemslist',[all_increment_id_max])][0]; 
#                except:
#                   info_orders=[]   
                
                min=max
                length_ord=length_ord-max_number_order_import
                if length_ord<max_number_order_import:
                    max=min+length_ord 
                else:
                    max=max+max_number_order_import 
                for info_order in info_orders: 
                        header=info_order['0']
                        #API to get sale order information based on increment_id
                        name_sales_order = str(header['increment_id'])
                        #searching sale order availability in openerp based on magneto_id or Order Reference
                        id_orders = self.pool.get('sale.order').search(cr, uid, ['|',('magento_id', '=', header['order_id']),('name', '=', name_sales_order)])
                        if True:
                            #To get customer information for each sale order from list of info_customers
                            info_customer = [customer for customer in info_customers if header['customer_id']==customer['customer_id']]
                            if info_customer:
                                info_customer=info_customer[0]
                            else:
                                info_customer = {
                                        'customer_id' : '0'
                                    }
                            pricelist_ids = self.pool.get('product.pricelist').search(cr, uid,[])
                            if (header['customer_is_guest'] == '1'):
                                info_customer['store_id'] = header['store_id']
                                info_customer['website_id'] = '1'
                                info_customer['email'] = header['customer_email']
                                info_customer['firstname'] = info_order['billing_address']['firstname']
                                info_customer['lastname'] = info_order['billing_address']['lastname']
                                info_customer['customer_is_guest'] = '1'
                            info_customer['shipping_address'] = info_order['shipping_address']
                            info_customer['billing_address'] = info_order['billing_address']
                            #getting billing and shipping address id from openerp
                            erp_customer_info = self.pool.get('magento.configuration').update_customer(cr, uid, info_customer)
                        if id_orders == []:     
                            if  header['status'] == 'canceled':
                                state = 'cancel'
                            else:
                                state = 'draft'    
                            
                            erp_sales_order = {
                                            'name' : name_sales_order,
                                            'date_order':header['created_at'],
                                            'state' : state,  
                                            'partner_id' : erp_customer_info['id'],
                                            'partner_invoice_id'  : erp_customer_info['billing_id'],
                                            'partner_order_id'    : erp_customer_info['billing_id'],
                                            'partner_shipping_id' : erp_customer_info['shipping_id'],
                                            'pricelist_id'        : pricelist_ids[0],
                                            'magento_id'      : header['order_id'],
                                            'magento_increment_id' : header['increment_id'],
                                           
                                           }
                           
                            if 'status_history' in info_order.keys() and (info_order['status_history']):
                                erp_sales_order['note']=''
                                for comment in info_order['status_history']:
                                            if comment['comment']:
                                                  erp_sales_order['note'] +=comment['comment']+'\n'
                            #creating sale order record in openerp
                            id_orders = [self.pool.get('sale.order').create(cr, uid, erp_sales_order)]
                            if id_orders:
                               total_no_of_records+=1 
                            missing_products_in_openerp=False
                            parents = {}
                            base_price=0.0
                            #fetching sale order line information from magneto 
                            for item in info_order['items']:
                                if item.has_key('product_type') and (item['product_type'] in ['configurable','bundle']):
                                    parents[item['item_id']] = {
                                        'base_price':   item['base_price'],
                                        'tax_percent':  item['tax_percent'],
                                    }
                                    continue
                                #searching product availability in openerp for each sale order line
                                product_ids = self.pool.get('product.product').search(cr, uid, [('magento_id', '=', item['product_id'])])
                                if (product_ids == []):
                                    try:
                                       info_products = server.call(session, 'catalog_product.itemslist',[item['product_id']])
                                    except:
                                       info_products=[] 
                                    missing_products_in_openerp = True
                                    continue
                                product_id = product_ids[0]
                                if base_price:
                                    price =  base_price                                    
                                else:
                                    price = item['base_price_incl_tax'] or item['base_price']
                                if  item.has_key('product_type') and item['product_type'] and (item['product_type'] != 'simple'):
                                       price=0.0    
                                #making product object for each sale order line's product
                                my_product = self.pool.get('product.product').browse(cr, uid, product_id)   
                                try:
                                    if (item['tax_percent'] != '0.0000'):
                                        tax_id = self.pool.get('magento.configuration').get_tax_id(cr, uid, item['tax_percent'])
                                        if (tax_id == 0):
                                            raise 
                                        else:
                                            tax_ids = [[6,0,[tax_id]]]   
                                    else:
                                        tax_ids = []
                                except:
                                    tax_ids = []      
                                erp_sales_order_line = { 'order_id'      : id_orders[0],
                                                         'product_id'      : product_id,
                                                         'name'            : my_product['name'],
                                                         'tax_id'          : tax_ids,
                                                         'price_unit'      : price,
                                                         'product_uom'     : my_product['uom_id']['id'],
                                                         'product_uom_qty' : item['qty_ordered'],
                                } 
                                #creating sale order line record in openerp
                                id_order_line = self.pool.get('sale.order.line').create(cr, uid, erp_sales_order_line)
                            #Shipping costs
                            try:
                                my_shipping = magento_configuration_object[0].shipping_product.id
                                try:
                                    if (header['shipping_tax_amount'] != '0.0000'):
                                        tax_percent = 100 * float(header['shipping_tax_amount']) / float(header['shipping_amount'])
                                        tax_id = self.pool.get('magento.configuration').get_tax_id(cr, uid, tax_percent)
                                        if (tax_id == 0):
                                            raise  
                                        else:
                                            tax_ids = [[6,0,[tax_id]]]      
                                    else:
                                        tax_ids = []     
                                except:
                                    tax_ids = []
                                if (header['shipping_incl_tax'] !='0.0000'):
                                          erp_ship_line = {
                                                         'order_id'      : id_orders[0],
                                                         'name'            : header['shipping_description'].replace('Select Shipping Method','Shipping Charges'),
                                                          'price_unit'      : float(header['shipping_incl_tax']),
                                                          'product_id' :my_shipping,
                                                          'tax_id':tax_ids,
                                                          'product_uom_qty' : 1,
                                                        }
                                          order_line = self.pool.get('sale.order.line').create(cr, uid, erp_ship_line)    
                            except:
                                pass
                            if missing_products_in_openerp:
                                continue 
                        else:
                           pass
	      cr.commit()
	      if last_import or not listorder:
		break
            #updating last imported time in openerp magneto object
            if magento_configuration_object[0].id:
                self.pool.get('magento.configuration').write(cr, uid, [magento_configuration_object[0].id], {'last_imported_invoice_timestamp':start_timestamp})    
                server.endSession(session)
                return total_no_of_records    
        server.endSession(session)
        return -1  

#added
#    def import_orders (self,cr,uid): #Customized Import Order Function
#        total_no_of_records=0# Number of sale order imported  
#        start_timestamp = str(DateTime.utc())
#        if True:
#            # magneto object through which connecting openerp with defined magento configuration start
#            start_timestamp = str(DateTime.utc())
#            magento_configuration_object = self.pool.get('magento.configuration').get_magento_configuration_object(cr, uid)
#            last_import = magento_configuration_object[0].last_imported_invoice_timestamp
#            [status, server, session] = self.pool.get('magento.configuration').magento_openerp_syn(cr, uid)
#            #checking server status
#            if not status:
#                raise osv.except_osv(_('There is no connection!'),_("There is no connection established with magento server\n\
#                  please check the url,username and password") )
#                server.endSession(session)
#                return -1
#            #end
#            #API to fetch all sale order information###################################################
#            listorder = server.call(session, 'sales_order.list',[{'updated_at': {'from':last_import}}])
#            
#            all_increment_id=[]
#            all_customer_id=[]
#            for info_order in listorder:
#                if info_order['customer_id']:
#                    all_customer_id.append(info_order['customer_id'])
#                all_increment_id.append(info_order['increment_id'])
#            min=0
#            max_number_order_import=20
#            if magento_configuration_object[0].max_number_order_import:
#                max_number_order_import=int(magento_configuration_object[0].max_number_order_import)
#            max=max_number_order_import
#            length_ord=len(listorder)
#            while length_ord>0:
#                all_customer_id_max=all_customer_id[min:max]
#                all_increment_id_max=all_increment_id[min:max]  
##                try:
##                   #API to get customer information for all customer_id at a time 
#                info_customers = [server.call(session, 'customapi_customer.itemslist' , [all_customer_id_max])][0];
##                except:
##                   info_customers=[] 
#                
##                try:     
#                   #API to get sale order information for all increment_ids at a time customapi_order.itemslist sales_order.itemslist
#                info_orders = [server.call(session, 'customapi_order.itemslist',[all_increment_id_max])][0]; 
##                except:
##                   info_orders=[]   
#                
#                min=max
#                length_ord=length_ord-max_number_order_import
#                if length_ord<max_number_order_import:
#                    max=min+length_ord 
#                else:
#                    max=max+max_number_order_import 
#                for info_order in info_orders: 
#                        header=info_order['0']
#                        #API to get sale order information based on increment_id
#                        name_sales_order = str(header['increment_id'])
#                        #searching sale order availability in openerp based on magneto_id or Order Reference
#                        id_orders = self.pool.get('sale.order').search(cr, uid, ['|',('magento_id', '=', header['order_id']),('name', '=', name_sales_order)])
#                        if True:
#                            #To get customer information for each sale order from list of info_customers
#                            info_customer = [customer for customer in info_customers if header['customer_id']==customer['customer_id']]
#                            if info_customer:
#                                info_customer=info_customer[0]
#                            else:
#                                info_customer = {
#                                        'customer_id' : '0'
#                                    }
#                            pricelist_ids = self.pool.get('product.pricelist').search(cr, uid,[])
#                            if (header['customer_is_guest'] == '1'):
#                                info_customer['store_id'] = header['store_id']
#                                info_customer['website_id'] = '1'
#                                info_customer['email'] = header['customer_email']
#                                info_customer['firstname'] = info_order['billing_address']['firstname']
#                                info_customer['lastname'] = info_order['billing_address']['lastname']
#                                info_customer['customer_is_guest'] = '1'
#                            info_customer['shipping_address'] = info_order['shipping_address']
#                            info_customer['billing_address'] = info_order['billing_address']
#                            #getting billing and shipping address id from openerp
#                            erp_customer_info = self.pool.get('magento.configuration').update_customer(cr, uid, info_customer)
#                        if id_orders == []:     
#                            if  header['status'] == 'canceled':
#                                state = 'cancel'
#                            else:
#                                state = 'draft'    
#                            erp_sales_order = {
#                                            'name' : name_sales_order,
##                                            'order_policy' : 'manual',  
#                                            'state' : state,  
#                                            'partner_id' : erp_customer_info['id'],
#                                            'partner_invoice_id'  : erp_customer_info['billing_id'],
#                                            'partner_id'    : erp_customer_info['billing_id'],
#                                            'partner_shipping_id' : erp_customer_info['shipping_id'],
#                                            'pricelist_id'        : pricelist_ids[0],
#                                            'magento_id'      : header['order_id'],
#                                            'magento_increment_id' : header['increment_id'],
#                                            'order_policy':'picking',
#                                           }
##                            erp_shop=self.pool.get('sale.shop').search(cr,uid,[('magento_id','=',header['store_id'])])
##                            if erp_shop:
##                                erp_sales_order['shop_id']=erp_shop[0]
#                            id_orders = [self.pool.get('sale.order').create(cr, uid, erp_sales_order)]
#                            if id_orders:
#                               total_no_of_records+=1 
#                            missing_products_in_openerp=False
#                            parents = {}
#                            product_ids_shop = []
#                            base_price=0.0
#                            #fetching sale order line information from magneto 
#                            print info_order['items'],' From the magento----------------------------'
#                            for item in info_order['items']:
#                                print item,' Itesm-------------------------'
#                                if item.has_key('product_type') and (item['product_type'] in ['configurable','bundle']):
#                                    parents[item['item_id']] = {
#                                        'base_price':   item['base_price_incl_tax'],
#                                        'tax_percent':  item['tax_percent'],
#                                    }
#                                    continue
#                                #searching product availability in openerp for each sale order line
#                                product_ids = self.pool.get('product.product').search(cr, uid, [('magento_id', '=', item['product_id'])])
#                                if (product_ids == []):
#                                    try:
#                                       info_products = server.call(session, 'catalog_product.itemslist',[item['product_id']])
#                                    except:
#                                       info_products=[] 
#                                    missing_products_in_openerp = True
#                                    continue
#                                product_id = product_ids[0]
#                                #making product object for each sale order line's product
#                                my_product = self.pool.get('product.product').browse(cr, uid, product_id)  
#                                if base_price:
#                                    price =  base_price                                    
#                                else:
#                                    price = item['base_price_incl_tax']
#                                if not price and item['parent_item_id']:
#                                    price = my_product.list_price #parents[item['parent_item_id']]['base_price']    
#                                if  item.has_key('product_type') and (item['product_type'] != 'simple'):
#                                       price=0.0    
#                                if item['tax_percent']=='0.0000' and item['parent_item_id']:
#                                   item['tax_percent']=parents[item['parent_item_id']]['tax_percent']
#                                try:
#                                    if (item['tax_percent'] != '0.0000'):
#                                        tax_id = self.pool.get('magento.configuration').get_tax_id(cr, uid, item['tax_percent'])
#                                        if (tax_id == 0):
#                                            raise 
#                                        else:
#                                            tax_ids = [[6,0,[tax_id]]]   
#                                    else:
#                                        tax_ids = []
#                                except:
#                                    tax_ids = []      
#                                erp_sales_order_line = { 'order_id'      : id_orders[0],
#                                                         'product_id'      : product_id,
#                                                         'name'            : item['name'],
#                                                         'tax_id'          : tax_ids,
#                                                         'price_unit'      : price,
#                                                         'product_uom'     : my_product['uom_id']['id'],
#                                                         'product_uom_qty' : item['qty_ordered'],
#                                } 
#                                #creating sale order line record in openerp
#                                id_order_line = self.pool.get('sale.order.line').create(cr, uid, erp_sales_order_line)
#                            #Shipping costs
#                            try:
#                                my_shipping = magento_configuration_object[0].shipping_product.id
#                                try:
#                                    if (header['shipping_tax_amount'] != '0.0000'):
#                                        tax_percent = 100 * float(header['shipping_tax_amount']) / float(header['shipping_amount'])
#                                        tax_id = self.pool.get('magento.configuration').get_tax_id(cr, uid, tax_percent)
#                                        if (tax_id == 0):
#                                            raise  
#                                        else:
#                                            tax_ids = [[6,0,[tax_id]]]      
#                                    else:
#                                        tax_ids = []     
#                                except:
#                                    tax_ids = []
#                                if (header['shipping_incl_tax'] !='0.0000'):
#                                          erp_ship_line = {
#                                                         'order_id'      : id_orders[0],
#                                                         'name'            : header['shipping_description'].replace('Select Shipping Method','Shipping Charges'),
#                                                          'price_unit'      : float(header['base_shipping_incl_tax']),
#                                                          'product_id' :my_shipping,
#                                                          'tax_id':tax_ids,
#                                                          'product_uom_qty' : 1,
#                                                        }
#                                          order_line = self.pool.get('sale.order.line').create(cr, uid, erp_ship_line)        
#                            except:
#                                pass
#                            if missing_products_in_openerp:
#                                continue 
#                        else:
#                           pass
#            #updating last imported time in openerp magneto object
#            if magento_configuration_object[0].id:
#                self.pool.get('magento.configuration').write(cr, uid, [magento_configuration_object[0].id], {'last_imported_invoice_timestamp':start_timestamp})    
#                server.endSession(session)
#                return total_no_of_records    
#        server.endSession(session)
#        return -1  



#end

    
magento_configuration()    
#Sale orders Configuration based on magneto syn

#===============================================================================
# For taxes importing for magento products...........
#===============================================================================
class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _order ='id asc'
account_invoice_line()    
class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _order ='id asc'
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
                context = context or {}
                lang = lang or context.get('lang',False)
                if not  partner_id:
                    raise osv.except_osv(_('No Customer Defined !'), _('Before choosing a product,\n select a customer in the sales form.'))
                warning = {}
                product_uom_obj = self.pool.get('product.uom')
                partner_obj = self.pool.get('res.partner')
                product_obj = self.pool.get('product.product')
                context = {'lang': lang, 'partner_id': partner_id}
                if partner_id:
                    lang = partner_obj.browse(cr, uid, partner_id).lang
                context_partner = {'lang': lang, 'partner_id': partner_id}
        
                if not product:
                    return {'value': {'th_weight': 0,
                        'product_uos_qty': qty}, 'domain': {'product_uom': [],
                           'product_uos': []}}
                if not date_order:
                    date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        
                result = {}
                warning_msgs = ' '
                product_obj = product_obj.browse(cr, uid, product, context=context_partner)
        
                uom2 = False
                if uom:
                    uom2 = product_uom_obj.browse(cr, uid, uom)
                    if product_obj.uom_id.category_id.id != uom2.category_id.id:
                        uom = False
                if uos:
                    if product_obj.uos_id:
                        uos2 = product_uom_obj.browse(cr, uid, uos)
                        if product_obj.uos_id.category_id.id != uos2.category_id.id:
                            uos = False
                    else:
                        uos = False
                fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
                if update_tax: #The quantity only have changed
                    result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)
        
                if not flag:
                    result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
                    if product_obj.description_sale:
                        result['name'] += '\n'+product_obj.description_sale
                domain = {}
                if (not uom) and (not uos):
                    result['product_uom'] = product_obj.uom_id.id
                    if product_obj.uos_id:
                        result['product_uos'] = product_obj.uos_id.id
                        result['product_uos_qty'] = qty * product_obj.uos_coeff
                        uos_category_id = product_obj.uos_id.category_id.id
                    else:
                        result['product_uos'] = False
                        result['product_uos_qty'] = qty
                        uos_category_id = False
                    result['th_weight'] = qty * product_obj.weight
                    domain = {'product_uom':
                                [('category_id', '=', product_obj.uom_id.category_id.id)],
                                'product_uos':
                                [('category_id', '=', uos_category_id)]}
                elif uos and not uom: # only happens if uom is False
                    result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
                    result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
                    result['th_weight'] = result['product_uom_qty'] * product_obj.weight
                elif uom: # whether uos is set or not
                    default_uom = product_obj.uom_id and product_obj.uom_id.id
                    q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
                    result['product_uom'] = default_uom
                    if product_obj.uos_id:
                        result['product_uos'] = product_obj.uos_id.id
                        result['product_uos_qty'] = qty * product_obj.uos_coeff
                    else:
                        result['product_uos'] = False
                        result['product_uos_qty'] = qty
                    result['th_weight'] = q * product_obj.weight        # Round the quantity up
        
                if not uom2:
                    uom2 = product_obj.uom_id
                # get unit price
        
                if not pricelist:
                    warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                            'Please set one before choosing a product.')
                    warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
                else:
                    price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                            product, qty or 1.0, partner_id, {
                                'uom': uom or result.get('product_uom'),
                                'date': date_order,
                                })[pricelist]
                    if price is False:
                        warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                                "You have to change either the product, the quantity or the pricelist.")
        
                        warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
                    else:
                        result.update({'price_unit': price})
                if  product_obj.magento_id!=-1 and product_obj.taxes_id:
                          result.update({'price_unit': (price*product_obj.taxes_id[0].amount)+price})
                if warning_msgs!=' ':
                    warning = {
                               'title': _('Configuration Error!'),
                               'message' : warning_msgs
                            }
                return {'value': result, 'domain': domain, 'warning': warning}

sale_order_line()    


class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"

    _columns = {
        'magento_id' : fields.integer('Magento ID'),
        'magento_increment_id' :fields.char('Magento Increment ID',size =64),  
          }
    #creating index for search records
    def _auto_init(self, cr, context=None):
        super(sale_order, self)._auto_init(cr, context=context)
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = \'sale_magneto_id\'')
        if not cr.fetchone():
            cr.execute('CREATE INDEX sale_magneto_id ON sale_order (magento_id)')
sale_order()
