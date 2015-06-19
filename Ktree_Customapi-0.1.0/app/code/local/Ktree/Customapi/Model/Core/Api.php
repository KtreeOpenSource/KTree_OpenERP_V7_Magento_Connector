<?php
class Ktree_Customapi_Model_Core_Api
{
	/**
	 * Returns version of the installed magento
	 * @return String
	 */
	public function getVersion()
	{
		return Mage::getVersion();
	}
}
?>

