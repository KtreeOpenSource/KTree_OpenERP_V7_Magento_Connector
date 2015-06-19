<?php
/**
 * Catalog category api - overrides Mage_Catalog
 *
 * @category   Ktree
 * @package    Ktree_Catalog
 * @author     Alma Rajkumar<alma.rajkumar@goktree.com>
 */
class Ktree_Customapi_Model_Category_Api extends Mage_Catalog_Model_Category_Api
{
    public function itemslist($customerIds)
    {  
    }
public function getID($category_name){
 $category_model = Mage::getModel('catalog/category')->loadByAttribute('name',$category_name);
 $result = array();
 $result['category_id'] = $category_model->getId();
 $result['category_name'] = $category_name;
 return $result;
 }
}
