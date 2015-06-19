<?php
/**
 * Catalog category api - overrides Mage_Catalog
 *
 * @category   Ktree
 * @package    Ktree_Catalog
 * @author     Alma Rajkumar <alma.rajkumar@goktree.com>
 */
class Ktree_Catalog_Model_Product_Api_v2 extends Ktree_Catalog_Model_Product_Api
{

    
    
public function catlist($productId, $store = null, $filters = null)
    {
       

        return $productId;
    }
}
