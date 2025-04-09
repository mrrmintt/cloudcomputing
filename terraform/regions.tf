variable "regions" {
  description = "Azure regions to deploy application"
  type        = list(string)
  default     = ["westeurope", "northeurope"]
}



/*
Example usage:


resource "azurerm_resource_group" "rg" {
  for_each = toset(var.regions)
  
  name     = "${var.prefix}-resources-${each.value}"
  location = each.value
}


resource "azurerm_virtual_network" "vnet" {
  for_each = toset(var.regions)
  
  name                = "${var.prefix}-vnet-${each.value}"
  address_space       = ["10.0.0.0/16"]
  location            = each.value
  resource_group_name = azurerm_resource_group.rg[each.value].name
}



output "vm_public_ips" {
  value = {
    for region in var.regions : 
    region => azurerm_public_ip.publicip[region].ip_address
  }
}
*/