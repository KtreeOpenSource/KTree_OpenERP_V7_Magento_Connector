<?php
/**
 * Catalog category api - overrides Mage_Catalog
 *
 * @category   Ktree
 * @package    Ktree_Catalog
 * @author     Alma Rajkumar <alma.rajkumar@goktree.com>
 */
class Ktree_Customapi_Model_Product_Api_v2 extends Mage_Catalog_Model_Product_Api_V2
{

  public function itemslist($entityIds,$store = null)
    {
      foreach($entityIds as $productId){

       $product = $this->_getProduct($productId, $store, $identifierType);

        $result = array( // Basic product data
            'product_id' => $product->getId(),
            'sku'        => $product->getSku(),
            'set'        => $product->getAttributeSetId(),
            'type'       => $product->getTypeId(),
            'categories' => $product->getCategoryIds(),
            'websites'   => $product->getWebsiteIds()
        );

        $allAttributes = array();
        if (!empty($attributes->attributes)) {
            $allAttributes = array_merge($allAttributes, $attributes->attributes);
        } else {
            foreach ($product->getTypeInstance(true)->getEditableAttributes($product) as $attribute) {
                if ($this->_isAllowedAttribute($attribute, $attributes)) {
                    $allAttributes[] = $attribute->getAttributeCode();
                }
            }
        }

        $_additionalAttributeCodes = array();
        if (!empty($attributes->additional_attributes)) {
            foreach ($attributes->additional_attributes as $k => $_attributeCode) {
                $allAttributes[] = $_attributeCode;
                $_additionalAttributeCodes[] = $_attributeCode;
            }
        }

        $_additionalAttribute = 0;
        foreach ($product->getTypeInstance(true)->getEditableAttributes($product) as $attribute) {
            if ($this->_isAllowedAttribute($attribute, $allAttributes)) {
                if (in_array($attribute->getAttributeCode(), $_additionalAttributeCodes)) {
                    $result['additional_attributes'][$_additionalAttribute]['key'] = $attribute->getAttributeCode();
                    $result['additional_attributes'][$_additionalAttribute]['value'] = $product
                        ->getData($attribute->getAttributeCode());
                    $_additionalAttribute++;
                } else {
                    $result[$attribute->getAttributeCode()] = $product->getData($attribute->getAttributeCode());
                }
            }
        }
       $finalresult['products'][]=$result; 
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
		//$finalresult=array();
		$finalresult['main_product']=$result;
		foreach($collection as $item) {
		
		
		$result[] = array( // Basic product data
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
		$finalresult['associated_products'][] = $result;
		}

        return $finalresult;
    }
}
