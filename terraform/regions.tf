variable "regions" {
  description = "Azure regions to deploy application"
  type        = list(string)
  default     = ["westeurope", "northeurope"]
}

# This file illustrates how you would expand main.tf to support multiple regions
# To use this, you would need to modify main.tf to use a loop over regions variable

/*
Example usage:

# Create resource groups per region
resource "azurerm_resource_group" "rg" {
  for_each = toset(var.regions)
  
  name     = "${var.prefix}-resources-${each.value}"
  location = each.value
}

# Create virtual networks per region
resource "azurerm_virtual_network" "vnet" {
  for_each = toset(var.regions)
  
  name                = "${var.prefix}-vnet-${each.value}"
  address_space       = ["10.0.0.0/16"]
  location            = each.value
  resource_group_name = azurerm_resource_group.rg[each.value].name
}

# And so on for all resources...

# In your outputs:
output "vm_public_ips" {
  value = {
    for region in var.regions : 
    region => azurerm_public_ip.publicip[region].ip_address
  }
}
*/