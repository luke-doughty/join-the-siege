# Heron Coding Challenge - File Classifier - Luke Doughty Submission

## Building an image

To build an image run `docker build . -t ${IMAGE_NAME}` from the root directory. This is also ran automatically when merging a PR to to master, with the image being pushed to my docker hub registry.

## To run locally:

1. Install dependencies:

   ```shell
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the Flask app:

   ```shell
   python -m src.app
   ```

3. Configure the catagories you want to classify in `classifer_catagories.json`

4. Test the classifier using a tool like curl:

   ```shell
   curl -X POST -F 'file=@path_to_pdf.pdf' http://127.0.0.1:5000/classify_file
   ```

5. Run tests:
   ```shell
    pytest
   ```

## To deploy in a cluster

1. Setup a kubernetes cluster

2. Configure `classifier.tf` so that the code below points to your cluster:

   ```
   provider "kubernetes" {
        config_path = "~/.kube/config"
   }
   ```

3. Set the amount of replicas you would like, following the format `replicas = 3`

4. Finally configure the catagories you want to classify in `classifer_catagories.json`

5. Use terraform to apply with the latest image
