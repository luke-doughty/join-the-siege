locals {
  version = "v0.01"
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
          name              = "heron-data-classifier"
          image             = "luke98doughty/heron-data-code-test:${local.version}"
          image_pull_policy = "Always"

          port {
            container_port = 80
          }
        }
      }
    }
  }
}
