variable "resource_group_name" {
  type        = string
  description = "Nome do Resource Group"
  default     = "rg-queimadas-dbx-aula"
}

variable "location" {
  type        = string
  description = "Região Azure"
  default     = "brazilsouth"
}

variable "mysql_admin_username" {
  type        = string
  description = "Administrador do MySQL Flexible Server"
  default     = "queimadasadmin"
}

variable "mysql_admin_password" {
  type        = string
  description = "Senha do admin do MySQL"
  sensitive   = true
}

variable "database_name" {
  type        = string
  description = "Nome do banco"
  default     = "queimadas"
}
