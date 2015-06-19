<?php
/**
 * Catalog category api - overrides Mage_Catalog
 *
 * @category   Ktree
 * @package    Ktree_Catalog
 * @author     Alma Rajkumar <alma.rajkumar@goktree.com>
 */
class Ktree_Customapi_Model_Customer_Api_v2 extends Mage_Customer_Model_Customer_Api_V2
{
public function itemslist($customerIds)
    {
$collection = Mage::getModel('customer/customer')->getCollection()
            ->addAttributeToSelect('*')
            ->addAttributeToFilter('entity_id', array(
                       'in' => $customerIds
                   ));

        if (is_array($filters)) {
            try {
                foreach ($filters as $field => $value) {
                    if (isset($this->_mapAttributes[$field])) {
                        $field = $this->_mapAttributes[$field];
                    }

                    $collection->addFieldToFilter($field, $value);
                }
            } catch (Mage_Core_Exception $e) {
                $this->_fault('filters_invalid', $e->getMessage());
            }
        }

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


	$row['addresses'] = Mage::getModel('Mage_Customer_Model_Address_Api')->items($customer->getId());

      /*
	foreach ($customer->getAddresses() as $address) {
            $data = $address->toArray();
            //$row  = array();

            foreach ($this->_mapAttributes as $attributeAlias => $attributeCode) {
                $row[$attributeAlias] = isset($data[$attributeCode]) ? $data[$attributeCode] : null;
            }

            foreach ($this->getAllowedAttributes($address) as $attributeCode => $attribute) {
                if (isset($data[$attributeCode])) {
                    $row[$attributeCode] = $data[$attributeCode];
                }
            }

            $row['is_default_billing'] = $customer->getDefaultBilling() == $address->getId();
            $row['is_default_shipping'] = $customer->getDefaultShipping() == $address->getId();

           // $result[] = $row;

        }
	*/   

            $result['customers'][] = $row;
        }

        return $result;
  }
}