terraform {
  required_version = ">= 1.6.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Configuração parcial: o workflow informa resource group, storage account,
  # container e key via -backend-config (cada aluno usa o seu RM).
  backend "azurerm" {}
}

provider "azurerm" {
  features {}
}
