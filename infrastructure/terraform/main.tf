variable "location" {
  description = "Azure region for the demo resources."
  type        = string
  default     = "Central India"
}

variable "project_name" {
  description = "Lowercase, globally unique project prefix (3-12 letters/numbers)."
  type        = string
  default     = "imsdemo"
  validation {
    condition     = can(regex("^[a-z][a-z0-9]{2,11}$", var.project_name))
    error_message = "project_name must be 3-12 lowercase letters/numbers and start with a letter."
  }
}

variable "api_image" {
  description = "Public container image URI, for example ghcr.io/owner/repository:sha."
  type        = string
}

variable "container_cpu" {
  description = "vCPU allocation for the API container."
  type        = number
  default     = 0.25
}

variable "container_memory" {
  description = "Memory allocation for the API container."
  type        = string
  default     = "0.5Gi"
}

resource "azurerm_resource_group" "ims" {
  name     = "rg-${var.project_name}-demo"
  location = var.location
  tags = {
    project     = "azure-devsecops-capstone"
    environment = "demo"
    managed_by  = "terraform"
  }
}

resource "azurerm_log_analytics_workspace" "ims" {
  name                = "law-${var.project_name}-demo"
  location            = azurerm_resource_group.ims.location
  resource_group_name = azurerm_resource_group.ims.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_storage_account" "ims" {
  name                            = "${var.project_name}demo${substr(md5(azurerm_resource_group.ims.id), 0, 4)}"
  resource_group_name             = azurerm_resource_group.ims.name
  location                        = azurerm_resource_group.ims.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = true
}

resource "azurerm_storage_share" "ims" {
  name               = "inventory-data"
  storage_account_id = azurerm_storage_account.ims.id
  quota              = 1
}

resource "azurerm_container_app_environment" "ims" {
  name                       = "cae-${var.project_name}-demo"
  location                   = azurerm_resource_group.ims.location
  resource_group_name        = azurerm_resource_group.ims.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.ims.id
}

resource "azurerm_container_app_environment_storage" "ims" {
  name                         = "inventory-data"
  container_app_environment_id = azurerm_container_app_environment.ims.id
  account_name                 = azurerm_storage_account.ims.name
  share_name                   = azurerm_storage_share.ims.name
  access_key                   = azurerm_storage_account.ims.primary_access_key
  access_mode                  = "ReadWrite"
}

resource "azurerm_container_app" "ims" {
  name                         = "ca-${var.project_name}-api"
  container_app_environment_id = azurerm_container_app_environment.ims.id
  resource_group_name          = azurerm_resource_group.ims.name
  revision_mode                = "Single"

  identity {
    type = "SystemAssigned"
  }

  template {
    min_replicas = 1
    max_replicas = 1

    volume {
      name         = "inventory-data"
      storage_name = azurerm_container_app_environment_storage.ims.name
      storage_type = "AzureFile"
    }

    container {
      name   = "inventory-api"
      image  = var.api_image
      cpu    = var.container_cpu
      memory = var.container_memory

      env {
        name  = "PORT"
        value = "8000"
      }
      env {
        name  = "DATABASE_PATH"
        value = "/data/inventory.db"
      }

      volume_mounts {
        name = "inventory-data"
        path = "/data"
      }

      liveness_probe {
        transport = "HTTP"
        path      = "/health/live"
        port      = 8000
      }
      readiness_probe {
        transport = "HTTP"
        path      = "/health/ready"
        port      = 8000
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    transport        = "http"
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }
}

output "api_url" {
  description = "Public base URL of the deployed inventory API."
  value       = "https://${azurerm_container_app.ims.latest_revision_fqdn}"
}

output "resource_group_name" {
  value = azurerm_resource_group.ims.name
}