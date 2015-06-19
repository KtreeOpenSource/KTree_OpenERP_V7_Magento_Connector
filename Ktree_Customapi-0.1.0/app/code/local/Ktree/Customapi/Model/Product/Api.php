<?php
/**
 * Catalog category api - overrides Mage_Catalog
 *
 * @category   Ktree
 * @package    Ktree_Catalog
 * @author     Alma Rajkumar<alma.rajkumar@goktree.com>
 */
class Ktree_Customapi_Model_Product_Api extends Mage_Catalog_Model_Product_Api
{
    
   
 public function itemslist($entityIds,$store = null)
    {  //$entityIds=array(1,4,6);
        $collection = Mage::getModel('catalog/product')->getCollection()
            ->addStoreFilter($this->_getStoreId($store))
            ->addAttributeToSelect('*')
            ->addAttributeToFilter('entity_id', array(
                       'in' => $entityIds
                   ));

      /*  if (is_array($filters)) {
            try {
                foreach ($filters as $field => $value) {
                    if (isset($this->_filtersMap[$field])) {
                        $field = $this->_filtersMap[$field];
                    }

                    $collection->addFieldToFilter($field, $value);
                }
            } catch (Mage_Core_Exception $e) {
                $this->_fault('filters_invalid', $e->getMessage());
            }
        }*/
        $finalresult=array();
        

        foreach ($collection as $product) { 
		$productId=$product['entity_id'];
		//$product = $this->_getProduct($productId, $store);
             $result = array();
            $result[] = $product->getData();
			 $result['category_ids'] = $product->getCategoryIds();
			$tax_helper = Mage::getSingleton('tax/calculation');
$tax_request = $tax_helper->getRateOriginRequest();
$tax_request->setProductClassId($product->getTaxClassId());

$tax = $tax_helper->getRate($tax_request);
			  $result['tax_percent'] = $tax;
           
          /*  $result[] = array( // Basic product data
                'product_id' => $product->getId(),
                'sku'        => $product->getSku(),
                'name'       => $product->getName(),
                'set'        => $product->getAttributeSetId(),
                'type'       => $product->getTypeId(),
                'category_ids'       => $product->getCategoryIds()
            );*/
       $finalresult[]=$result; 
       }

        return $finalresult;
    }
  public function ktreebundle($productId, $store = null,$identifierType = null)
    {
        $product = $this->_getProduct($productId, $store, $identifierType);
$collection = $product->getTypeInstance(true)
    ->getSelectionsCollection($product->getTypeInstance(true)->getOptionsIds($product), $product);
$result=array(
'product_id' => $product->getId(),
'name'=> $product->getName(),
'sku'        => $product->getSku(),
'price_type'=>$product->getPriceType(),
'price'=> $product->getPrice(),
	);	
		$finalresult=array();
		//$finalresult['main_product']=$result;
		foreach($collection as $item) {
		
		
		$result = array( // Basic product data
            'product_id' => $item->getId(),
			'name'=>$item->getName(),
            'sku'        => $item->getSku(),
			'selection_id'=>$item->getSelectionId(),
            'selection_qty' => $item->getSelectionQty()*1,
			'selection_can_change_qty' => $item->getSelectionCanChangeQty(),
            'selection_price_value'   => $item->getSelectionPriceValue(),
			'selection_price_type'   => $item->getSelectionPriceType(),
			'price'=> $item->getPrice(),
			'position' => $item->getPosition(),
        );
		/*$result['ids'][]=$item->product_id;
		$result['sku'][]=$item->getSku();
		//$result['item_details'][$item->product_id]=Mage::getModel('Mage_Catalog_Model_Product_Api')->info($item->product_id);
		$result['Qty'][]=$item->getSelectionQty()*1;
		$result['Price'][]=$item->getPrice();*/
		$finalresult[] = $result;
		}

        return $finalresult;
    }
}
