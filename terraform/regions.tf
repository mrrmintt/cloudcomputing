variable "regions" {
  description = "Azure regions to deploy application"
  type        = list(string)
  default     = ["westeurope", "northeurope"]
}