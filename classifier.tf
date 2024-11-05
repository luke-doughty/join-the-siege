locals {
  version = "v0.01"
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

# ConfigMap to store the contents of classifier_categories.json
resource "kubernetes_config_map" "categories_config" {
  metadata {
    name = "categories-config"
  }

  data = {
    "classifier_categories.json" = file("classifier_categories.json")
  }
}

resource "kubernetes_service" "heron_data_classifier" {
  metadata {
    name = "heron-data-classifier"
    labels = {
      app = "heron-data-classifier"
    }
  }

  spec {
    type = "ClusterIP"

    session_affinity = "ClientIP"
    port {
      name        = "nginx"
      port        = 80
      target_port = 80
      protocol    = "TCP"
    }

    selector = {
      app = "heron-data-classifier"
    }
  }
}

resource "kubernetes_deployment" "heron_data_classifier" {
  timeouts {
    create = "1m"
    update = "1m"
    delete = "1m"
  }

  metadata {
    name = "heron-data-classifier"
  }

  spec {
    replicas = 3 # Bump up if more needed

    selector {
      match_labels = {
        app = "heron-data-classifier"
      }
    }

    template {
      metadata {
        labels = {
          app         = "heron-data-classifier"
          prom-scrape = true
        }
      }

      spec {
        container {
          env {
            name  = "CATEGORIES_FILE_PATH"
            value = "/config/classifier_categories.json" # Path in the container
          }

          name              = "heron-data-classifier"
          image             = "luke98doughty/heron-data-code-test:${local.version}"
          image_pull_policy = "Always"

          port {
            container_port = 80
          }

          volume_mount {
            name       = "categories-volume"
            mount_path = "/config" # Mount point in the container
            read_only  = true
          }
        }
      }
    }
  }
}
