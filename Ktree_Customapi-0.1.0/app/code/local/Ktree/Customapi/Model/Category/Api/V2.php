<?php
/**
 * Catalog category api - overrides Mage_Catalog
 *
 * @category   Ktree
 * @package    Ktree_Catalog
 * @author     Alma Rajkumar <alma.rajkumar@goktree.com>
 */
class Ktree_Customapi_Model_Category_Api_V2 extends Mage_Catalog_Model_Category_Api_V2
{
 /**
 * retrieves Category ID based on category name
 *
 */
 public function getID($category_name){
 $category_model = Mage::getModel('catalog/category')->loadByAttribute('name',$category_name);
 $result = array();
 $result['category_id'] = $category_model->getId();
 $result['category_name'] = $category_name;
 return $result;
 }
}
