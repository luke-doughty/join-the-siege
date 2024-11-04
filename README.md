# Heron Coding Challenge - File Classifier - Luke Doughty Submission

## Building an image

To build an image run `docker build . -t ${IMAGE_NAME}` from the root directory. This is also ran automatically when merging a PR to to master, with the image being pushed to my docker hub registry.

To deploy this, you would need a kubernetes cluster setup, and use the terraform file under `classifier.tf` to run a `terraform apply`
