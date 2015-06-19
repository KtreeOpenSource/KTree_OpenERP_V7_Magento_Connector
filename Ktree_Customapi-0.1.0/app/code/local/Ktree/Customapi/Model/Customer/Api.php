<?php
/**
 * Catalog category api - overrides Mage_Catalog
 *
 * @category   Ktree
 * @package    Ktree_Catalog
 * @author     Alma Rajkumar<alma.rajkumar@goktree.com>
 */
class Ktree_Customapi_Model_Customer_Api extends Mage_Customer_Model_Customer_Api
{
    public function itemslist($customerIds)
    {  
        $collection = Mage::getModel('customer/customer')->getCollection()
            ->addAttributeToSelect('*')
            ->addAttributeToFilter('entity_id', array(
                       'in' => $customerIds
                   ));
		$result = array();
        foreach ($collection as $customer) {
            $data = $customer->toArray();
            $row  = array();
			foreach ($this->_mapAttributes as $attributeAlias => $attributeCode) {
                $row[$attributeAlias] = (isset($data[$attributeCode]) ? $data[$attributeCode] : null);
            }

            foreach ($this->getAllowedAttributes($customer) as $attributeCode => $attribute) {
                //if (isset($data[$attributeCode])) {
                    $row[$attributeCode] = $data[$attributeCode];
                //}
            }
	//$row['addresses'] = Mage::getModel('Mage_Customer_Model_Address_Api')->items($customer->getId());
		 foreach ($customer->getAddresses() as $address) {
            $data1 = $address->toArray();
			//$street=mb_substr($address->getData('street'), 0, 40, 'ISO-8859-1');
			$street=$address->getData('street');
			//$street = iconv('ASCII', 'UTF-8//IGNORE', $street);
            $row1  = array();
			$data1['customer_id']=$address->getData('customer_id');
			$data1['customer_address_id']=$address->getId();
			/*$data1['created_at']=$address->getData('created_at');
			$data1['updated_at']=$address->getData('updated_at');
			$data1['firstname']=$address->getData('firstname');
			$data1['lastname']=$address->getData('lastname');
			$data1['city']=$address->getData('city');
			$data1['region']=$address->getData('region');
			$data1['region_id']=$address->getData('region_id');
			$data1['country_id']=$address->getData('country_id');
			$data1['telephone']=$address->getData('telephone');
			$data1['street']=$street;
			$data1['middlename']=$address->getData('middlename');
			$data1['prefix']=$address->getData('prefix');
			$data1['suffix']=$address->getData('suffix');
			$data1['postcode']=$address->getData('postcode');
			$data1['company']=$address->getData('company');
			$data1['fax']=$address->getData('fax');
			$data1['incemented_id']=$address->getData('incemented_id');
			$data1['vat_id']=$address->getData('vat_id');
			$data1['vat_is_valid']=$address->getData('vat_is_valid');
			$data1['vat_request_date']=$address->getData('vat_request_date');
			$data1['vat_request_id']=$address->getData('vat_request_id');
			$data1['vat_request_success']=$address->getData('vat_request_success');
			$data1['is_default_billing'] = $customer->getDefaultBilling() == $address->getId();
            $data1['is_default_shipping'] = $customer->getDefaultShipping() == $address->getId();*/
$data1['is_default_billing'] = $customer->getDefaultBilling() == $address->getId();
            $data1['is_default_shipping'] = $customer->getDefaultShipping() == $address->getId();
			$row1[]=$data1;
			/*foreach ($this->_mapAttributes as $attributeAlias => $attributeCode) {
                $row1[$attributeAlias] = isset($data1[$attributeCode]) ? $data1[$attributeCode] : null;
            }

            foreach ($this->getAllowedAttributes($address) as $attributeCode => $attribute) {
               // if (isset($data1[$attributeCode])) {
                    $row1[$attributeCode] = $data1[$attributeCode];
             //   }
            }*/

            

            $row['addresses'] = $row1;

        }
	$result[] = $row;
        }
return $result;
        //return json_encode($result);
    }
}
